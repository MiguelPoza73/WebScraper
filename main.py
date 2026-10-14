import re
from datetime import datetime
from urllib.parse import urlsplit

import streamlit as st
from scraper import EXAMPLE, ScrapingError, fetch_page, find_tables, extract_table, extract_css
from exporter import to_csv, to_excel

st.set_page_config(page_title="Web a Excel", page_icon="🌿", layout="wide")
st.markdown("""<style>
.stApp {background:#f7f8fc;color:#26334a} .stButton>button {background:#dfd8fa;border:0;border-radius:12px}
h1,h2,h3 {color:#354561} [data-testid="stMetric"] {background:#e6f3ee;padding:16px;border-radius:14px}
</style>""", unsafe_allow_html=True)
st.title("Web a Excel")
st.write("Extrae una página pública, revisa sus datos y descarga el resultado.")
with st.form("source"):
    url = st.text_input("URL de origen", value=EXAMPLE)
    allowed = st.checkbox("He comprobado que las condiciones de la fuente permiten esta extracción.")
    load = st.form_submit_button("Consultar página")
if load:
    for key in ("page", "result", "method", "origin"):
        st.session_state.pop(key, None)
    if not allowed:
        st.warning("Comprueba las condiciones de la fuente antes de continuar.")
    else:
        try:
            with st.spinner("Consultando acceso y HTML…"):
                st.session_state.page, st.session_state.origin = fetch_page(url)
        except ScrapingError as exc:
            st.error(str(exc))
if "page" in st.session_state:
    soup = st.session_state.page
    st.caption(f"Página consultada: {st.session_state.origin}")
    method = st.radio("Método de extracción", ["Tablas HTML", "Selectores CSS"], horizontal=True)
    if method == "Tablas HTML":
        tables = find_tables(soup)
        st.write(f"Se han encontrado {len(tables)} tablas.")
        if tables:
            def label(i):
                caption = tables[i].find("caption")
                text = caption.get_text() if caption else tables[i].get_text()[:120]
                return f"Tabla {i + 1} · {len(tables[i].find_all('tr'))} filas HTML · {text}"
            selected = st.selectbox("Selecciona una tabla por su contenido", range(len(tables)), format_func=label)
            if st.button("Extraer tabla"):
                st.session_state.pop("result", None)
                try:
                    st.session_state.result = extract_table(tables[selected])
                    st.session_state.method = f"Tabla HTML {selected + 1}"
                except ScrapingError as exc:
                    st.error(str(exc))
        else:
            st.info("No hay tablas en el HTML recibido. La web puede usar JavaScript; esta versión no lo ejecuta.")
    else:
        st.caption("El selector de registros define una fila. Cada campo busca un elemento dentro de ella; selector vacío = el propio registro.")
        with st.form("selectors"):
            selector = st.text_input("Selector CSS de registros", "h2")
            count = st.number_input("Número de campos", 1, 6, 1)
            fields = []
            for i in range(int(count)):
                a, b, c = st.columns(3)
                name = a.text_input(f"Nombre {i+1}", "texto" if i == 0 else f"campo_{i+1}")
                css = b.text_input(f"Selector relativo {i+1}", "")
                attr = c.text_input(f"Atributo {i+1} (vacío = texto)", "")
                fields.append((name, css, attr))
            run = st.form_submit_button("Extraer elementos")
        if run:
            st.session_state.pop("result", None)
            try:
                st.session_state.result = extract_css(soup, selector, fields)
                st.session_state.method = f"CSS {selector!r}; campos: {fields!r}"
            except ScrapingError as exc:
                st.error(str(exc))
    if "result" in st.session_state:
        data = st.session_state.result
        st.subheader("Vista previa")
        a, b = st.columns(2)
        a.metric("Filas obtenidas", len(data))
        b.metric("Columnas", len(data.columns))
        st.write("Campos:", list(data.columns))
        st.caption(f"Origen: {st.session_state.origin} · Método: {st.session_state.method}")
        # La vista usa índices posicionales para admitir nombres repetidos sin cambiarlos en el archivo.
        preview = data.head(20).copy()
        preview.columns = [f"{i+1}: {name}" for i, name in enumerate(data.columns)]
        st.dataframe(preview, use_container_width=True)
        if data.empty:
            st.info("No se encontraron registros. Comprueba el selector y el HTML recibido; no se han inventado resultados.")
        else:
            default = f"{urlsplit(st.session_state.origin).hostname}_{datetime.now():%Y%m%d_%H%M}"
            filename = st.text_input("Nombre del archivo", default)
            if not re.fullmatch(r"[\w .-]{1,100}", filename) or filename in (".", ".."):
                st.warning("Usa un nombre de 1 a 100 caracteres, sin separadores de carpetas.")
            else:
                st.download_button("Descargar CSV", to_csv(data), filename + ".csv", "text/csv")
                try:
                    st.download_button("Descargar Excel", to_excel(data), filename + ".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                except (ValueError, TypeError) as exc:
                    st.error(f"No se pudo generar Excel: {exc}")
st.caption("Sin limpieza ni deduplicación. HTML estático únicamente. Los datos permanecen en la sesión local.")
