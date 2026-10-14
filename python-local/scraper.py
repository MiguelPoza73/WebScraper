"""Extracción de HTML estático sin limpieza de los textos."""
import ipaddress
import socket
import time
from urllib.parse import urlsplit, urljoin
from urllib.robotparser import RobotFileParser

import pandas as pd
import requests
from bs4 import BeautifulSoup
from soupsieve import SelectorSyntaxError

EXAMPLE = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
USER_AGENT = "LearningTableExtractor/1.0"
_last_request = {}


class ScrapingError(ValueError):
    """Error que puede mostrarse directamente en la interfaz."""


def validate_url(url):
    try:
        parts = urlsplit(url)
    except ValueError as exc:
        raise ScrapingError("La URL tiene un formato inválido.") from exc
    if parts.scheme not in ("http", "https") or not parts.hostname or parts.username or parts.password:
        raise ScrapingError("Introduce una URL http o https pública, sin credenciales.")
    try:
        if parts.port not in (None, 80, 443):
            raise ScrapingError("Solo se permiten los puertos web 80 y 443.")
        addresses = socket.getaddrinfo(parts.hostname, parts.port or 443)
        if any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
            raise ScrapingError("La dirección debe pertenecer a una web pública.")
    except (OSError, ValueError) as exc:
        raise ScrapingError("La dirección no es válida o no se puede resolver.") from exc
    return url


def _request(url, interval=2):
    validate_url(url)
    host = urlsplit(url).netloc
    time.sleep(max(0, interval - (time.monotonic() - _last_request.get(host, 0))))
    _last_request[host] = time.monotonic()
    try:
        # Las redirecciones se validan antes de seguirlas; nunca se reintenta un bloqueo.
        with requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=(5, 20),
                          allow_redirects=False, stream=True) as response:
            if response.is_redirect:
                return response.status_code, response.headers, b""
            if response.status_code >= 400:
                return response.status_code, response.headers, b""
            data = bytearray()
            for chunk in response.iter_content(65536):
                data.extend(chunk)
                if len(data) > 8_000_000:
                    raise ScrapingError("La página supera el límite de 8 MB.")
            return response.status_code, response.headers, bytes(data)
    except requests.RequestException as exc:
        raise ScrapingError("No se pudo conectar con la fuente dentro del tiempo permitido.") from exc


def fetch_page(url):
    """Comprueba robots.txt y descarga una página, sin recursos secundarios."""
    for _ in range(6):
        validate_url(url)
        parts = urlsplit(url)
        robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
        status, _, content = _request(robots_url)
        interval = 2
        if status == 200:
            robots = RobotFileParser()
            robots.parse(content.decode("utf-8", errors="replace").splitlines())
            if not robots.can_fetch(USER_AGENT, url):
                raise ScrapingError("robots.txt no permite extraer esta página.")
            interval = max(interval, robots.crawl_delay(USER_AGENT) or 0)
            rate = robots.request_rate(USER_AGENT)
            if rate:
                interval = max(interval, rate.seconds / rate.requests)
        elif status not in (404, 410):
            raise ScrapingError(f"No se pudo verificar robots.txt (HTTP {status}).")
        status, headers, content = _request(url, interval)
        if status in (301, 302, 303, 307, 308):
            location = headers.get("Location")
            if not location:
                raise ScrapingError("Redirección sin destino.")
            url = urljoin(url, location)
            continue
        if status != 200:
            raise ScrapingError(f"La fuente respondió HTTP {status}. No se intentará eludir el bloqueo.")
        if "html" not in headers.get("Content-Type", "").lower():
            raise ScrapingError("La respuesta no es una página HTML compatible.")
        return BeautifulSoup(content, "html.parser"), url
    raise ScrapingError("Demasiadas redirecciones.")


def find_tables(soup):
    return soup.find_all("table")


def extract_table(table):
    # BeautifulSoup conserva espacios y evita las conversiones numéricas de read_html.
    rows = [r for r in table.find_all("tr") if r.find_parent("table") is table]
    grid, header_count = [], 0
    for row in rows:
        cells = row.find_all(["th", "td"], recursive=False)
        if not cells:
            continue
        if len(grid) == header_count and all(c.name == "th" for c in cells):
            header_count += 1
        values = []
        for cell in cells:
            if cell.get("rowspan", "1") != "1" or cell.get("colspan", "1") != "1":
                raise ScrapingError("Esta tabla tiene celdas combinadas. Selecciona sus filas con CSS para conservar los textos sin expandir ni inventar celdas.")
            values.append(cell.get_text(separator="", strip=False))
        grid.append(values)
    if not grid:
        raise ScrapingError("La tabla no contiene filas extraíbles.")
    width = max(map(len, grid))
    if any(len(row) != width for row in grid):
        raise ScrapingError("La tabla tiene filas de distinta longitud. Usa CSS para extraer su estructura explícitamente.")
    if header_count == 1:
        columns = grid[0]
    elif header_count > 1:
        columns = pd.MultiIndex.from_tuples(list(zip(*grid[:header_count])))
    else:
        columns = list(range(width))
    return pd.DataFrame(grid[header_count:], columns=columns, dtype=object)


def extract_css(soup, row_selector, fields):
    """Cada campo es (nombre, selector relativo, atributo o cadena vacía)."""
    if not row_selector or not fields:
        raise ScrapingError("Define un selector y al menos un campo.")
    try:
        rows = soup.select(row_selector)
        result = []
        for row in rows:
            values = []
            for name, selector, attribute in fields:
                matches = row.select(selector) if selector else [row]
                if len(matches) > 1:
                    raise ScrapingError(f"El campo {name!r} encuentra varios elementos por fila. Ajusta el selector.")
                element = matches[0] if matches else None
                values.append(None if element is None else element.get(attribute) if attribute else element.get_text(separator="", strip=False))
            result.append(values)
        return pd.DataFrame(result, columns=[f[0] for f in fields], dtype=object)
    except SelectorSyntaxError as exc:
        raise ScrapingError(f"Selector CSS inválido: {exc}") from exc
