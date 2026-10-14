# WebScraper — Web a Excel

Herramienta para extraer información de páginas web, revisar los resultados y descargarlos en Excel (.xlsx) o CSV.

**[Abrir la aplicación](https://web-a-excel.handyocean1.chatgpt.site)**

## Cómo funciona

1. Introduce la URL de origen o abre un archivo HTML guardado.
2. Selecciona una tabla HTML o define los registros y campos con selectores CSS.
3. Revisa la vista previa y el número de filas y columnas obtenidas.
4. Elige un nombre y descarga todos los registros en Excel o CSV.

La extracción conserva los textos, espacios, celdas vacías y duplicados. Los selectores CSS permiten obtener tanto el texto de los elementos como atributos, por ejemplo el destino de un enlace. Los archivos Excel conservan los valores como texto.

## Versiones

- **`sites/`**: código fuente de la aplicación publicada, con interfaz en React y TypeScript, consulta de páginas y exportación en el navegador.
- **`python-local/`**: versión original en Python y Streamlit, con extracción mediante BeautifulSoup y generación de archivos con pandas y openpyxl.
