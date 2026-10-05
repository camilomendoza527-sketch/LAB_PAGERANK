"""Núcleo matemático: W, P, M, Método de la Potencia y Monte Carlo."""
import warnings

import numpy as np


def construir_W(grafo):
    """Matriz de pesos W: w_ij = número de enlaces de i hacia j (con duplicados).

    Returns:
        (nodos ordenados, W de m x m).
    """
    nodos = sorted(set(grafo) | {d for ds in grafo.values() for d in ds})
    idx = {n: i for i, n in enumerate(nodos)}
    W = np.zeros((len(nodos), len(nodos)))
    for origen, destinos in grafo.items():
        for destino in destinos:
            W[idx[origen], idx[destino]] += 1.0
    return nodos, W


def construir_P(W):
    """Matriz de transición P (ecs. 1-3).

    p_ij = w_ij / c_i. Si c_i = 0 (Dead End), la fila es 1/m (ec. 3).

    Returns:
        (P, indices de dead ends).
    """
    m = W.shape[0]
    c = W.sum(axis=1)                      # ec. (1)
    dead_ends = np.where(c == 0)[0]
    P = np.empty_like(W)
    for i in range(m):
        P[i] = W[i] / c[i] if c[i] > 0 else 1.0 / m
    return P, dead_ends


def construir_M(P, d=0.85):
    """Matriz de Google M = d*P + (1-d)/m * E (ec. 4)."""
    if not 0.0 < d < 1.0:
        raise ValueError("d debe estar en (0, 1)")
    m = P.shape[0]
    return d * P + (1.0 - d) / m * np.ones((m, m))


def detectar_duplicados(nodos, W):
    """Lista (origen, destino, w) de los enlaces con peso w_ij > 1."""
    filas, cols = np.where(W > 1)
    return [(nodos[i], nodos[j], int(W[i, j])) for i, j in zip(filas, cols)]


def verificar_ergodica(M):
    """Comprueba filas que suman 1 y M estrictamente positiva.

    M > 0 implica irreducible (todo estado alcanzable en 1 paso) y
    aperiódica (p_ii > 0), por lo que existe un único π.
    """
    return bool(np.allclose(M.sum(axis=1), 1.0) and np.all(M > 0))


def metodo_potencia(M, tol=1e-8, max_iter=500):
    """Método de la Potencia: pi(n+1) = pi(n) M, criterio de paro en norma L1.

    Returns:
        (pi final, historial de pi(n) con forma (n+1, m), iteraciones usadas).
    """
    m = M.shape[0]
    pi = np.ones(m) / m
    historial = [pi.copy()]
    for n in range(1, max_iter + 1):
        pi_sig = pi @ M
        historial.append(pi_sig.copy())
        if np.linalg.norm(pi_sig - pi, 1) < tol:
            return pi_sig, np.array(historial), n
        pi = pi_sig
    warnings.warn(f"Potencia no convergió en {max_iter} iteraciones (tol={tol}).")
    return pi, np.array(historial), max_iter


def monte_carlo(M, pasos=150_000, semilla=42):
    """Simulación del navegante aleatorio (reproducible con `semilla`).

    Usa la CDF acumulada de cada fila y searchsorted: evita la validación
    de np.random.choice en cada paso.

    Returns:
        Frecuencia relativa de visitas por nodo.
    """
    m = M.shape[0]
    rng = np.random.default_rng(semilla)
    cdf = np.cumsum(M, axis=1)
    cdf[:, -1] = 1.0                       # evita errores de redondeo
    estado = int(rng.integers(m))
    u = rng.random(pasos)
    visitas = np.zeros(m)
    for k in range(pasos):
        visitas[estado] += 1
        estado = int(np.searchsorted(cdf[estado], u[k], side="right"))
    return visitas / pasos