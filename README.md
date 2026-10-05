# Laboratorio PageRank — Procesos Estocásticos (603504)

## Ejecución
Terminal 1 (desde `proyecto_pagerank/`):

    python generar_html.py && cd web_lab && python -m http.server 8000

Terminal 2 (desde `proyecto_pagerank/`):

    pip install -r requirements.txt && python main.py

Opciones: `--d 0.85 --semilla 42 --pasos 150000 --mostrar`.
Las figuras se guardan en `figuras/`.

## Decisiones de diseño
- El crawler solo descarga HTML y cuenta `<a href>`; P se calcula en `pagerank.py`.
- Topología 2 usa dos semillas (A y D): D<->E no es alcanzable desde A.
- Se ignoran `#ancla`, `mailto:`, `javascript:` y `tel:` (regex `re`).

## Topología 1: cálculo analítico
P1→{P2,P3}, P2→P3, P3→P1, es decir
P = [[0, 1/2, 1/2], [0, 0, 1], [1, 0, 0]].

**Sin amortiguación (d=1):** π1 = π3, π2 = π1/2, π3 = π1/2 + π2.
Con Σπ = 1: 2.5·π1 = 1, luego **π = (0.4, 0.2, 0.4)**.

**Con d = 0.85** (m=3, (1−d)/m = 0.05; como Σπ = 1, el término de E aporta 0.05 a cada componente):

    π1 = 0.85·π3 + 0.05
    π2 = 0.85·(π1/2) + 0.05 = 0.425·π1 + 0.05
    π3 = 0.85·(π1/2 + π2) + 0.05 = 0.78625·π1 + 0.0925

Sustituyendo π3 en la primera: π1 = 0.6683125·π1 + 0.128625, luego π1 = 686/1769.

    π1 = 686/1769 ≈ 0.3878
    π2 = 380/1769 ≈ 0.2148
    π3 = 703/1769 ≈ 0.3974      (suma = 1)

`main.py` debe reproducir estos valores con error < 1e-6 (Potencia).

## Respuestas de sustentación

**1. ¿Por qué (1−d)/m·E hace M irreducible y aperiódica?**
Todas las entradas de M son ≥ (1−d)/m > 0. Desde cualquier estado se llega a
cualquier otro en un paso, así que la cadena es irreducible. Además m_ii > 0
(hay autotransición), el período es 1 y la cadena es aperiódica. Las filas
suman d + (1−d) = 1 (P ya es estocástica tras reparar los dead ends). Como M
es positiva y estocástica, Perron-Frobenius da: λ=1 simple, único π con
todas las componentes positivas y |λ_k| < 1 para el resto. Sin ese término,
una Spider Trap absorbería toda la masa (cadena reducible).

**2. Tres enlaces duplicados a la misma URL.**
Cada duplicado suma 1 a w_ij (ec. 2), y p_ij = 3/c_i, con c_i contando los
tres. Los duplicados no crean masa: la fila sigue sumando 1. Solo redistribuyen
dentro de la fila hacia el destino repetido. En F8 (c=3, w_F8,T=3), p_F8,T = 1,
idéntico a un solo enlace. Por eso el truco es casi ineficaz en T3. Sí
inflaría el rango si la página tuviera además otros enlaces. Mitigación
posible: deduplicar destinos al construir W.

**3. ¿Por qué M conserva un PageRank alto en T3?**
T enlaza solo a M, así que T le pasa todo su rango: π_M ≈ d·π_T + (1−d)/m.
M reparte entre F1..F8, y estas devuelven su masa a T (ciclo T→M→Fi→T).
Con d = 0.85, m = 10, las ecuaciones son:

    f = 0.10625·π_M + 0.015
    π_T = 0.85·8f + 0.015
    π_M = 0.85·π_T + 0.015

Valores esperados: π_T ≈ 0.331, π_M ≈ 0.297, π_Fi ≈ 0.047 cada una. M queda
casi tan alta como T porque es el único destino de T y el nodo que alimenta
la granja.

**4. Papel de λ2 en la convergencia.**
π(n) = π(0)·Mⁿ. Descomponiendo π(0) en autovectores, el error decae como
|λ2|ⁿ, es decir, convergencia geométrica con razón |λ2|. Para la matriz de
Google, |λ2| ≤ d. Iteraciones aproximadas: n ≈ ln(tol)/ln|λ2|; para
tol = 1e-8, d=0.85 → ≈ 113 (cota); d=0.99 → ≈ 1833. Cuando d → 1, |λ2| → 1
y la convergencia se vuelve lenta (Fig. 3). Un d menor converge más rápido,
pero se parece menos a la estructura real de enlaces.