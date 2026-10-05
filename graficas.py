"""Las cuatro figuras obligatorias del laboratorio."""
import os

import matplotlib.pyplot as plt
import numpy as np

from pagerank import construir_M, metodo_potencia


def _guardar(fig, ruta, mostrar):
    """Guarda la figura en `ruta` y opcionalmente la muestra."""
    os.makedirs(os.path.dirname(ruta) or ".", exist_ok=True)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    if mostrar:
        plt.show()
    plt.close(fig)


def grafica_convergencia(historial, nodos, ruta, max_iter_graf=30, mostrar=False):
    """Fig. 1: π(n) de cada nodo vs iteración (primeras `max_iter_graf`)."""
    h = historial[: max_iter_graf + 1]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for j, nodo in enumerate(nodos):
        ax.plot(range(len(h)), h[:, j], marker="o", ms=3, label=nodo)
    ax.set_xlabel("Iteración n")
    ax.set_ylabel("π(n)")
    ax.set_title("Convergencia del Método de la Potencia (Topología 2)")
    ax.legend(title="Nodo")
    ax.grid(alpha=0.3)
    _guardar(fig, ruta, mostrar)


def grafica_mc_vs_numerico(nodos, pi_num, pi_mc, ruta, mostrar=False):
    """Fig. 2: barras agrupadas, Método de la Potencia vs Monte Carlo."""
    x = np.arange(len(nodos))
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(x - 0.2, pi_num, 0.4, label="Potencia (numérico)")
    ax.bar(x + 0.2, pi_mc, 0.4, label="Monte Carlo")
    ax.set_xticks(x)
    ax.set_xticklabels(nodos)
    ax.set_ylabel("PageRank")
    ax.set_title("Monte Carlo vs numérico (Topología 2)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    _guardar(fig, ruta, mostrar)


def grafica_sensibilidad(P, ruta, tol=1e-8, mostrar=False):
    """Fig. 3: iteraciones hasta converger vs d en [0.10, 0.99].

    Se compara con la cota teórica ln(tol)/ln(d), pues |λ2(M)| <= d.
    """
    ds = np.append(np.arange(0.10, 0.99, 0.05), 0.99)
    iteraciones = []
    for d in ds:
        _, _, it = metodo_potencia(construir_M(P, d), tol=tol, max_iter=5000)
        iteraciones.append(it)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(ds, iteraciones, "o-", label="Iteraciones medidas")
    ax.plot(ds, np.log(tol) / np.log(ds), "--", label="Cota ln(tol)/ln(d)")
    ax.set_yscale("log")
    ax.set_xlabel("Factor de amortiguación d")
    ax.set_ylabel("Iteraciones hasta tol")
    ax.set_title("Sensibilidad de la convergencia a d (Topología 2)")
    ax.legend()
    ax.grid(alpha=0.3, which="both")
    _guardar(fig, ruta, mostrar)


def grafica_ranking_seo(nodos, pi, ruta, mostrar=False):
    """Fig. 4: PageRank final de T, M, F1..F8 en la Topología 3."""
    orden = ["T", "M"] + [f"F{i}" for i in range(1, 9)]
    valores = [pi[nodos.index(n)] for n in orden]
    colores = ["tab:red", "tab:orange"] + ["tab:gray"] * 8
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(orden, valores, color=colores)
    for i, v in enumerate(valores):
        ax.text(i, v, f"{v:.3f}", ha="center", va="bottom", fontsize=8)
    ax.set_ylabel("PageRank")
    ax.set_title("Ranking en la Topología 3 (ataque SEO)")
    ax.grid(axis="y", alpha=0.3)
    _guardar(fig, ruta, mostrar)