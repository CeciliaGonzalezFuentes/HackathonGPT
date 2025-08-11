| 🇪🇸 Español                                                                                                                                                                                                                           | 🇬🇧 English                                                                                                                                                                                                            |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Infios GPT** es un modelo conversacional que actúa como intermediario entre el usuario y una API conectada a **PostgreSQL**. Permite realizar consultas en lenguaje natural y devuelve las respuestas tal cual las recibe de la API. | **Infios GPT** is a conversational model that acts as an intermediary between the user and an API connected to **PostgreSQL**. It allows natural language queries and returns answers exactly as received from the API. |
| Español                                                                 | English                                                                  |
| ----------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| 📡 Conexión directa a API en `ngrok`.                                   | 📡 Direct API connection via `ngrok`.                                    |
| 🗄 Acceso a tablas como *orders*, *customers*, *products*, *suppliers*. | 🗄 Access to tables like *orders*, *customers*, *products*, *suppliers*. |
| 💬 Consultas en lenguaje natural, sin escribir SQL.                     | 💬 Natural language queries, no SQL needed.                              |
| 📏 Respuestas fieles, sin inventar datos.                               | 📏 Accurate responses, no fabricated data.                               |
| 📊 Visualización de datos con *matplotlib* (barras, pastel).            | 📊 Data visualization with *matplotlib* (bar, pie).                      |
| Español                                     | English                                     |
| ------------------------------------------- | ------------------------------------------- |
| **suppliers** (proveedores)                 | **suppliers**                               |
| **customers** (clientes)                    | **customers**                               |
| **orders** (pedidos)                        | **orders**                                  |
| **products** (productos)                    | **products**                                |
| **categories**, **shippers**, **employees** | **categories**, **shippers**, **employees** |
| Español                                                                    | English                                                                  |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `query all the suppliers` → Lista todos los proveedores.                   | `query all the suppliers` → Lists all suppliers.                         |
| `get the number of suppliers per country` → Cuenta proveedores por país.   | `get the number of suppliers per country` → Counts suppliers by country. |
| `get the number of orders in the year 1996` → Cantidad de pedidos en 1996. | `get the number of orders in the year 1996` → Number of orders in 1996.  |
| Transformar datos en gráfico de pastel.                                    | Transform data into a pie chart.                                         |
| Español                                                              | English                                                              |
| -------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 1️⃣ Usuario envía consulta en lenguaje natural.                      | 1️⃣ User sends a natural language query.                             |
| 2️⃣ GPT reenvía la consulta a `https://e8418d61276d.ngrok-free.app`. | 2️⃣ GPT forwards the query to `https://e8418d61276d.ngrok-free.app`. |
| 3️⃣ API procesa y responde en texto.                                 | 3️⃣ API processes and responds in text.                              |
| 4️⃣ GPT muestra la respuesta sin modificar.                          | 4️⃣ GPT displays the answer without changes.                         |
| Español                                  | English                                      |
| ---------------------------------------- | -------------------------------------------- |
| ❌ No genera ni ejecuta SQL directamente. | ❌ Does not generate or execute SQL directly. |
| ❌ No modifica respuestas de la API.      | ❌ Does not modify API responses.             |
| ❌ No inventa datos.                      | ❌ Does not fabricate data.                   |
| Español                                          | English                                     |
| ------------------------------------------------ | ------------------------------------------- |
| API en `ngrok` con acceso a PostgreSQL.          | API on `ngrok` with PostgreSQL access.      |
| Soporte para *matplotlib* si se desean gráficos. | *Matplotlib* support if charts are desired. |
| Gráfico de barras / Bar Chart                                               | Gráfico de pastel / Pie Chart                                               |
| --------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| <img width="2000" height="1200" alt="suppliers_bar" src="https://github.com/user-attachments/assets/ddfbedb0-44bd-4cf5-8045-423d18e20509" />| <img width="1600" height="1600" alt="suppliers_pie" src="https://github.com/user-attachments/assets/f9fa065a-bcb5-47a4-a548-5db91305a794" />|


