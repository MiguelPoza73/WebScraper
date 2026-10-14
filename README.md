# WebScraper

Herramienta en Python para extraer información de páginas web públicas, revisar los resultados y descargarlos en Excel (.xlsx) o CSV. Su interfaz utiliza Streamlit y colores pastel.

## Cómo funciona

1. Introduce la URL y confirma que has revisado las condiciones de la fuente.
2. Pulsa **Consultar página**.
3. Elige **Tablas HTML** o **Selectores CSS**.
4. Ejecuta la extracción y revisa las filas, columnas, campos y una vista previa de los primeros 20 registros.
5. Escribe un nombre y pulsa **Descargar Excel** o **Descargar CSV**. El navegador guarda el resultado en la carpeta que elijas para las descargas.

### Extraer tablas

La aplicación muestra cuántas tablas ha encontrado. Cada opción incluye su título o una muestra del contenido y el número de filas HTML para identificarla. Selecciona una y pulsa **Extraer tabla**.

La página de ejemplo es la [lista de países por población de Naciones Unidas en Wikipedia](https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)). Selecciona la tabla de países y población para revisar sus datos y exportarlos.

### Extraer elementos con CSS

El **selector CSS de registros** define los elementos que se convertirán en filas. Para cada campo, introduce:

- **Nombre:** nombre de la columna.
- **Selector relativo:** elemento que se busca dentro de cada registro. Vacío selecciona el propio registro.
- **Atributo:** por ejemplo, `href` para obtener el destino de un enlace. Vacío extrae el texto.

| Información | Selector de registros | Nombre del campo | Selector relativo | Atributo |
| --- | --- | --- | --- | --- |
| Títulos | `h2` | `texto` | Vacío | Vacío |
| Texto de enlaces | `a` | `texto` | Vacío | Vacío |
| Destino de enlaces | `a` | `destino` | Vacío | `href` |

Puedes definir varios campos de una misma estructura. Tras cambiar el número de campos, envía el formulario para mostrar los campos adicionales y completar sus selectores.

### Revisar y exportar

La vista previa muestra la URL de origen y el método utilizado. La exportación incluye todos los registros extraídos y conserva textos, espacios, celdas vacías y duplicados. La limpieza y el análisis se realizan después, manualmente en Excel.

## Organización

- `main.py`: interfaz y vista previa.
- `scraper.py`: acceso y extracción con requests, BeautifulSoup y pandas.
- `exporter.py`: generación de Excel con openpyxl y de CSV.
- `requirements.txt`: dependencias.
- `test_app.py`: pruebas automatizadas.
- `smoke_wikipedia.py`: comprobación con la fuente de ejemplo.
