"""Orquesta: crawler -> W -> P -> M -> Potencia y Monte Carlo -> gráficas."""
import argparse

import numpy as np

from crawler import rastrear
from graficas import (grafica_convergencia, grafica_mc_vs_numerico,
                      grafica_ranking_seo, grafica_sensibilidad)
from pagerank import (construir_M, construir_P, construir_W,
                      detectar_duplicados, metodo_potencia, monte_carlo,
                      verificar_ergodica)

# T2 necesita dos semillas: D y E no son alcanzables desde A.
SEMILLAS = {
    "topo1": ["topo1/P1.html"],
    "topo2": ["topo2/A.html", "topo2/D.html"],
    "topo3": ["topo3/T.html"],
}


def calcular(nombre, base, d, semilla, pasos):
    """Corre el pipeline de una topología y devuelve los resultados (sin imprimir)."""
    grafo = rastrear([f"{base}/{s}" for s in SEMILLAS[nombre]])
    nodos, W = construir_W(grafo)
    P, dead = construir_P(W)
    M = construir_M(P, d)
    pi_num, hist, iters = metodo_potencia(M)
    pi_mc = monte_carlo(M, pasos, semilla)
    return dict(nodos=nodos, W=W, P=P, M=M, dead=dead, pi_num=pi_num,
                pi_mc=pi_mc, hist=hist, iters=iters)


def imprimir_reporte(nombre, r, ver_P=False):
    """Imprime el reporte de una topología. La matriz P solo si se pide."""
    nodos = r["nodos"]
    print(f"\n{'=' * 50}\n{nombre.upper()}\n{'=' * 50}")
    print("Nodos:", nodos)
    print("Dead ends:", [nodos[i] for i in r["dead"]] or "ninguno")
    print("Duplicados:", detectar_duplicados(nodos, r["W"]) or "ninguno")
    print("M ergódica (filas=1, M>0):", verificar_ergodica(r["M"]))
    if ver_P:
        print("P =")
        print(r["P"])
    print(f"Iteraciones (Potencia): {r['iters']}")
    print("π Potencia   :", dict(zip(nodos, np.round(r["pi_num"], 4))))
    print("π Monte Carlo:", dict(zip(nodos, np.round(r["pi_mc"], 4))))
    print(f"Diferencia L1 = {np.abs(r['pi_num'] - r['pi_mc']).sum():.5f}")


def generar_figuras(r2, r3, mostrar):
    """Genera las 4 figuras obligatorias en la carpeta figuras/."""
    grafica_convergencia(r2["hist"], r2["nodos"], "figuras/fig1_convergencia.png", mostrar=mostrar)
    grafica_mc_vs_numerico(r2["nodos"], r2["pi_num"], r2["pi_mc"], "figuras/fig2_mc_vs_numerico.png", mostrar=mostrar)
    grafica_sensibilidad(r2["P"], "figuras/fig3_sensibilidad_d.png", mostrar=mostrar)
    grafica_ranking_seo(r3["nodos"], r3["pi_num"], "figuras/fig4_ranking_topo3.png", mostrar=mostrar)
    print("Figuras guardadas en figuras/")


MENU = """
--- LABORATORIO PAGERANK ---
1. Topología 1 (3 nodos)
2. Topología 2 (5 nodos: Dead End y Spider Trap)
3. Topología 3 (10 nodos: ataque SEO)
4. Generar las 4 gráficas
0. Salir
"""


def main():
    ap = argparse.ArgumentParser(description="Laboratorio PageRank")
    ap.add_argument("--base", default="http://localhost:8000")
    ap.add_argument("--d", type=float, default=0.85)
    ap.add_argument("--semilla", type=int, default=42)
    ap.add_argument("--pasos", type=int, default=150_000)
    ap.add_argument("--mostrar", action="store_true", help="mostrar figuras")
    a = ap.parse_args()

    cache = {}  # cada topología se calcula una sola vez

    def obtener(t):
        if t not in cache:
            print(f"Calculando {t}...")
            cache[t] = calcular(t, a.base, a.d, a.semilla, a.pasos)
        return cache[t]

    while True:
        print(MENU)
        op = input("Opción: ").strip()
        if op in ("1", "2", "3"):
            t = f"topo{op}"
            r = obtener(t)
            ver_P = input("¿Mostrar matriz P? (s/n): ").strip().lower() == "s"
            imprimir_reporte(t, r, ver_P)
        elif op == "4":
            generar_figuras(obtener("topo2"), obtener("topo3"), a.mostrar)
        elif op == "0":
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()