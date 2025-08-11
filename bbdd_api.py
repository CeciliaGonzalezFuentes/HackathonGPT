import asyncpg
import json
import logging
import os
import re
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Any, Optional
import openai
import shutil

load_dotenv()

# ---------------------------------
# Configuración logging
# ---------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------
# Configuración OpenAI
# ---------------------------------
openai.api_key = os.getenv("OPEN_AI_API_KEY")

# ---------------------------------
# Variables globales
# ---------------------------------
DB_POOL: Optional[asyncpg.Pool] = None
SCHEMA_CACHE: Optional[str] = None

# ---------------------------------
# Ruta del log y límites
# ---------------------------------
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
AUDIT_LOG_FILE = LOG_DIR / "audit_log.jsonl"
MAX_LOG_SIZE_MB = 5  # tamaño máximo antes de rotar (MB)

# ---------------------------------
# Filtro SQL
# ---------------------------------
SQL_BLOCKLIST = re.compile(
    r"\b(DROP|DELETE|TRUNCATE|ALTER|UPDATE|INSERT|CREATE|REPLACE)\b",
    re.IGNORECASE
)

# ---------------------------------
# Función de rotación de logs
# ---------------------------------
def rotate_log_if_needed():
    """Rota el archivo de log si supera el tamaño máximo."""
    if AUDIT_LOG_FILE.exists() and AUDIT_LOG_FILE.stat().st_size > MAX_LOG_SIZE_MB * 1024 * 1024:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        rotated_file = LOG_DIR / f"audit_log_{timestamp}.jsonl"
        shutil.move(AUDIT_LOG_FILE, rotated_file)
        logger.info(f"♻ Log rotado: {rotated_file}")


# ---------------------------------
# Función para escribir en el log
# ---------------------------------
def audit_log(entry: dict[str, Any]) -> None:
    try:
        rotate_log_if_needed()
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Error guardando en audit log: {e}")


# ---------------------------------
# Obtener esquema de la base
# ---------------------------------
async def get_schema() -> str:
    async with DB_POOL.acquire() as conn:
        rows = await conn.fetch("""
            SELECT table_name, column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """)
    schema = {}
    for row in rows:
        table = row["table_name"]
        column = row["column_name"]
        dtype = row["data_type"]
        schema.setdefault(table, []).append(f"{column} ({dtype})")
    return "\n".join(
        f"Table: {table}\n  " + "\n  ".join(columns)
        for table, columns in schema.items()
    )


# ---------------------------------
# Ejecutar consultas SQL seguras
# ---------------------------------
async def query(sql_query: str) -> list[dict[str, Any]]:
    if SQL_BLOCKLIST.search(sql_query):
        logger.warning(f"🚨 Consulta bloqueada: {sql_query}")
        return [{"error": "Consulta bloqueada por seguridad. Solo se permiten SELECTs."}]

    try:
        async with DB_POOL.acquire() as conn:
            rows = await conn.fetch(sql_query)
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error ejecutando SQL: {e}")
        return []


# ---------------------------------
# Lenguaje natural → SQL
# ---------------------------------
async def human_query_to_sql(human_query: str) -> Optional[str]:
    system_message = f"""
    Given the following schema, write a SQL query that retrieves the requested information. 
    Only SELECT queries are allowed. Do not generate DROP, DELETE, UPDATE, ALTER, TRUNCATE, or CREATE statements.
    Return the SQL query inside a JSON structure with the key "sql_query".
    <example>{{
        "sql_query": "SELECT * FROM users WHERE age > 18;",
        "original_query": "Show me all users older than 18 years old."
    }}
    </example>
    <schema>
    {SCHEMA_CACHE}
    </schema>
    """
    response = openai.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": human_query},
        ],
    )
    return response.choices[0].message.content


# ---------------------------------
# Construcción de respuesta final
# ---------------------------------
async def build_answer(result: list[dict[str, Any]], human_query: str) -> Optional[str]:
    system_message = f"""
    Given a user's question and the SQL rows response from the database, 
    write a clear, concise, and accurate answer to the user's question.
    <user_question> 
    {human_query}
    </user_question>
    <sql_response>
    {json.dumps(result, ensure_ascii=False)}
    </sql_response>
    """
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system_message}],
    )
    return response.choices[0].message.content


# ---------------------------------
# Modelos
# ---------------------------------
class PostHumanQueryPayload(BaseModel):
    human_query: str


# ---------------------------------
# Lifespan handler
# ---------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    global DB_POOL, SCHEMA_CACHE
    logger.info("🚀 Iniciando backend...")
    DB_POOL = await asyncpg.create_pool(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        min_size=1,
        max_size=5
    )
    SCHEMA_CACHE = await get_schema()
    logger.info("✅ Esquema cacheado y pool de conexiones listo.")

    yield

    if DB_POOL:
        await DB_POOL.close()
        logger.info("🔒 Pool de conexiones cerrado.")


# ---------------------------------
# App FastAPI
# ---------------------------------
BACKEND_SERVER = os.getenv("SERVER_URL")
app = FastAPI(servers=[{"url": BACKEND_SERVER}], lifespan=lifespan)


# ---------------------------------
# Endpoint principal
# ---------------------------------
@app.post("/human_query", name="Human Query", description="Convierte lenguaje natural a SQL, consulta la base y responde.")
async def human_query(payload: PostHumanQueryPayload) -> dict[str, str]:
    timestamp = datetime.now(timezone.utc).isoformat()

    sql_query_json = await human_query_to_sql(payload.human_query)
    if not sql_query_json:
        return {"error": "Falló la generación de la consulta SQL"}

    try:
        result_dict = json.loads(sql_query_json)
    except json.JSONDecodeError:
        return {"error": "La respuesta del LLM no es un JSON válido"}

    result = await query(result_dict["sql_query"])
    answer = await build_answer(result, payload.human_query)

    audit_log({
        "timestamp": timestamp,
        "human_query": payload.human_query,
        "sql_query": result_dict.get("sql_query"),
        "db_result": result,
        "final_answer": answer
    })

    if not answer:
        return {"error": "Falló la generación de la respuesta"}
    return {"answer": answer}


# ---------------------------------
# Arranque local
# ---------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8080)
