# WebScraper — Python y Streamlit

Versión original de Web a Excel: introduce una URL, selecciona una tabla o define campos con selectores CSS, revisa los resultados y descárgalos en Excel o CSV.

**[Visitar la versión online](https://web-a-excel.handyocean1.chatgpt.site)**

- `main.py`: interfaz y vista previa.
- `scraper.py`: consulta y extracción con requests y BeautifulSoup.
- `exporter.py`: generación de Excel y CSV.
- `requirements.txt`: dependencias.
- `test_app.py`: pruebas automatizadas.
- `smoke_wikipedia.py`: comprobación con la página de ejemplo.

La extracción conserva textos, espacios, celdas vacías y duplicados. La vista previa muestra los primeros 20 registros; la descarga contiene todos los datos extraídos.
