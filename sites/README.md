# Web a Excel — Sites

**[Abrir la aplicación](https://web-a-excel.handyocean1.chatgpt.site)**

Consulta una página web o abre un archivo HTML, extrae tablas o elementos mediante selectores CSS y revisa hasta 20 registros antes de descargar el resultado completo en Excel o CSV.

- `app/`: interfaz y consulta de páginas.
- `lib/extraction.ts`: extracción de tablas y campos, generación de CSV y validación de Excel.
- `lib/source.ts`: consulta de fuentes y comprobación de robots.txt.
- `tests/`: pruebas de extracción y exportación.

Los resultados se procesan en el navegador, conservando textos, espacios, celdas vacías y duplicados.
