import json
from pathlib import Path
from collections import Counter

LOG_DIR = Path(__file__).parent / "logs"

def leer_todos_los_logs():
    """Lee todos los archivos JSONL en la carpeta logs/ y devuelve lista de entradas."""
    entradas = []
    if not LOG_DIR.exists():
        print("⚠ La carpeta logs/ no existe.")
        return entradas

    for archivo in sorted(LOG_DIR.glob("audit_log*.jsonl")):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                for linea in f:
                    try:
                        entradas.append(json.loads(linea))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            print(f"⚠ No se pudo leer {archivo}: {e}")
    return entradas


def generar_reporte(entradas):
    total = len(entradas)
    bloqueadas = sum(1 for e in entradas if any("bloqueada" in str(val).lower() for val in e.get("db_result", [])))
    errores = sum(1 for e in entradas if "error" in str(e.get("final_answer", "")).lower())

    # Top preguntas más frecuentes
    preguntas = Counter(e.get("human_query", "").strip() for e in entradas if e.get("human_query"))
    top_preguntas = preguntas.most_common(5)

    print("\n📊 REPORTE DE LOGS")
    print("=" * 40)
    print(f"Total de consultas registradas: {total}")
    print(f"🚫 Consultas bloqueadas por seguridad: {bloqueadas} ({bloqueadas/total*100:.2f}%)" if total else "🚫 Consultas bloqueadas por seguridad: 0")
    print(f"❌ Consultas con errores: {errores} ({errores/total*100:.2f}%)" if total else "❌ Consultas con errores: 0")

    print("\n🔝 Top 5 preguntas más frecuentes:")
    if top_preguntas:
        for pregunta, count in top_preguntas:
            print(f"  - {pregunta} → {count} veces")
    else:
        print("  No hay preguntas registradas.")

    print("=" * 40)


def mostrar_queries(entradas):
    print("\n📜 LISTADO DE QUERIES EJECUTADAS")
    print("=" * 80)
    for e in entradas:
        timestamp = e.get("timestamp", "Sin fecha")
        human = e.get("human_query", "").strip()
        sql = e.get("sql_query", "").strip()

        print(f"🕒 {timestamp}")
        print(f"🗣 Pregunta: {human}")
        print(f"🛠 SQL: {sql}")
        print("-" * 80)


if __name__ == "__main__":
    entradas = leer_todos_los_logs()
    if not entradas:
        print("📂 No se encontraron entradas en los logs.")
    else:
        generar_reporte(entradas)
        mostrar_queries(entradas)
