"""Genera el sitio web de laboratorio (web_lab/) con las tres topologías.

Cada página es un HTML con etiquetas <a href>. Los enlaces duplicados se
escriben repetidos a propósito (F8 -> T tres veces). El crawler NO lee este
diccionario: solo descarga las páginas por HTTP.
"""
import os

TOPOLOGIAS = {
    "topo1": {
        "P1": ["P2", "P3"],
        "P2": ["P3"],
        "P3": ["P1"],
    },
    "topo2": {
        "A": ["B", "C"],
        "B": ["C"],
        "C": [],            # Dead End
        "D": ["E"],         # Spider Trap D <-> E
        "E": ["D"],
    },
    "topo3": {
        "T": ["M"],
        **{f"F{i}": ["T"] for i in range(1, 8)},
        "F8": ["T", "T", "T"],            # 3 enlaces duplicados
        "M": [f"F{i}" for i in range(1, 9)],
    },
}

PLANTILLA = """<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><title>{nombre}</title></head>
<body id="arriba">
<h1>Página {nombre}</h1>
<ul>
{enlaces}
</ul>
</body>
</html>
"""


def escribir_sitio(raiz="web_lab"):
    """Escribe todas las páginas HTML de las tres topologías en `raiz`."""
    for topo, paginas in TOPOLOGIAS.items():
        carpeta = os.path.join(raiz, topo)
        os.makedirs(carpeta, exist_ok=True)
        for nombre, destinos in paginas.items():
            enlaces = "\n".join(
                f'  <li><a href="{d}.html">{d}</a></li>' for d in destinos
            )
            ruta = os.path.join(carpeta, f"{nombre}.html")
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(PLANTILLA.format(nombre=nombre, enlaces=enlaces))
        print(f"[ok] {topo}: {len(paginas)} páginas en {carpeta}/")


if __name__ == "__main__":
    escribir_sitio()