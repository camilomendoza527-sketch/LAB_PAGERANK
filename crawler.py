"""Crawler BFS: descarga páginas por HTTP y extrae hipervínculos.

Preserva los enlaces duplicados (cada <a href> cuenta), ya que w_ij debe
aumentar con cada repetición (ecuación 2).
"""
import re
from collections import deque
from urllib.parse import urljoin, urldefrag, urlparse

import requests
from bs4 import BeautifulSoup

# Esquemas y anclas internas que no son navegación entre páginas.
PATRON_IGNORAR = re.compile(r"^(#|mailto:|javascript:|tel:)", re.IGNORECASE)


def nombre_nodo(url):
    """Devuelve el nombre del nodo: archivo sin extensión (".../P1.html" -> "P1")."""
    archivo = urlparse(url).path.rsplit("/", 1)[-1]
    return re.sub(r"\.html?$", "", archivo, flags=re.IGNORECASE)


def extraer_enlaces(html, url_base):
    """Extrae todos los <a href> de un HTML como URLs absolutas, con duplicados.

    Args:
        html: contenido HTML de la página.
        url_base: URL de la página, para resolver enlaces relativos.
    Returns:
        Lista de URLs absolutas (sin fragmento), en orden de aparición.
    """
    sopa = BeautifulSoup(html, "html.parser")
    enlaces = []
    for a in sopa.find_all("a", href=True):
        href = a["href"].strip()
        if not href or PATRON_IGNORAR.match(href):
            continue
        absoluta, _ = urldefrag(urljoin(url_base, href))
        enlaces.append(absoluta)
    return enlaces


def rastrear(semillas, max_paginas=200, timeout=5):
    """Exploración BFS desde una o más URLs semilla (solo mismo host).

    Varias semillas son necesarias cuando hay componentes no alcanzables
    desde una sola página (p. ej. la Spider Trap D<->E de la Topología 2).

    Returns:
        dict {nodo: [destinos...]} con destinos repetidos si hay duplicados.
        No contiene probabilidades: P se calcula después, en pagerank.py.
    """
    host = urlparse(semillas[0]).netloc
    cola = deque(semillas)
    vistas = set(semillas)
    grafo = {}
    sesion = requests.Session()

    while cola:
        url = cola.popleft()
        nodo = nombre_nodo(url)
        try:
            resp = sesion.get(url, timeout=timeout)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[aviso] No se pudo descargar {url}: {e}")
            grafo[nodo] = []
            continue

        destinos = []
        for enlace in extraer_enlaces(resp.text, url):
            if urlparse(enlace).netloc != host:
                continue  # enlace externo: fuera del grafo del laboratorio
            destinos.append(nombre_nodo(enlace))
            if enlace not in vistas and len(vistas) < max_paginas:
                vistas.add(enlace)
                cola.append(enlace)
        grafo[nodo] = destinos
    return grafo