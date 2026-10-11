import time
from collections import deque

TOTAL_M = 3
TOTAL_C = 3
CAPACIDAD_BOTE = 2
INICIAL = (TOTAL_M, TOTAL_C, 0)
META = (0, 0, 1)

# (misioneros, canibales) que viajan en el bote
OPERADORES = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]


def es_valido(estado):
    m_izq, c_izq, _ = estado
    m_der, c_der = TOTAL_M - m_izq, TOTAL_C - c_izq
    if not (0 <= m_izq <= TOTAL_M and 0 <= c_izq <= TOTAL_C):
        return False
    if m_izq > 0 and c_izq > m_izq:
        return False
    if m_der > 0 and c_der > m_der:
        return False
    return True


def es_meta(estado):
    return estado == META


def sucesores(estado):
    m_izq, c_izq, bote = estado
    signo = -1 if bote == 0 else 1  # bote izq: salen de la izquierda
    resultado = []
    for dm, dc in OPERADORES:
        nuevo = (m_izq + signo * dm, c_izq + signo * dc, 1 - bote)
        if es_valido(nuevo):
            resultado.append(((dm, dc), nuevo))
    return resultado


def describir_operador(op, bote_antes):
    dm, dc = op
    partes = []
    if dm:
        partes.append(f"{dm} misionero{'s' if dm > 1 else ''}")
    if dc:
        partes.append(f"{dc} can\u00edbal{'es' if dc > 1 else ''}")
    destino = "derecha" if bote_antes == 0 else "izquierda"
    return " y ".join(partes) + f" cruzan a la {destino}"


def _reconstruir(nodo):
    camino = []
    while nodo is not None:
        estado, padre, op = nodo
        camino.append((estado, op))
        nodo = padre
    camino.reverse()
    return camino


def _resultado(nombre, nodo_meta, generados, expandidos, max_mem, t0):
    camino = _reconstruir(nodo_meta) if nodo_meta else []
    return {
        "algoritmo": nombre,
        "encontrada": nodo_meta is not None,
        "camino": camino,                       # [(estado, operador), ...]
        "costo": max(len(camino) - 1, 0),       # numero de cruces
        "generados": generados,
        "expandidos": expandidos,
        "max_memoria": max_mem,                 # max nodos simultaneos
        "tiempo_ms": (time.perf_counter() - t0) * 1000,
    }


def bfs():
    t0 = time.perf_counter()
    raiz = (INICIAL, None, None)
    if es_meta(INICIAL):
        return _resultado("BFS", raiz, 1, 0, 1, t0)
    frontera = deque([raiz])
    visitados = {INICIAL}
    generados, expandidos, max_mem = 1, 0, 1
    while frontera:
        nodo = frontera.popleft()
        expandidos += 1
        for op, hijo in sucesores(nodo[0]):
            if hijo in visitados:
                continue
            visitados.add(hijo)
            generados += 1
            nuevo = (hijo, nodo, op)
            if es_meta(hijo):
                return _resultado("BFS", nuevo, generados, expandidos,
                                  max(max_mem, len(frontera) + len(visitados)), t0)
            frontera.append(nuevo)
        max_mem = max(max_mem, len(frontera) + len(visitados))
    return _resultado("BFS", None, generados, expandidos, max_mem, t0)


def dfs():
    t0 = time.perf_counter()
    raiz = (INICIAL, None, None)
    pila = [raiz]
    generados, expandidos, max_mem = 1, 0, 1
    while pila:
        nodo = pila.pop()
        if es_meta(nodo[0]):
            return _resultado("DFS", nodo, generados, expandidos, max_mem, t0)
        expandidos += 1
        # estados de la ruta actual, para evitar ciclos
        ruta = set()
        n = nodo
        while n is not None:
            ruta.add(n[0])
            n = n[1]
        # se invierte para explorar los operadores en el orden definido
        for op, hijo in reversed(sucesores(nodo[0])):
            if hijo in ruta:
                continue
            generados += 1
            pila.append((hijo, nodo, op))
        max_mem = max(max_mem, len(pila))
    return _resultado("DFS", None, generados, expandidos, max_mem, t0)


if __name__ == "__main__":
    for f in (bfs, dfs):
        r = f()
        print(r["algoritmo"], "cruces:", r["costo"], "gen:", r["generados"],
              "exp:", r["expandidos"], "mem:", r["max_memoria"],
              f"t={r['tiempo_ms']:.3f}ms")
        for est, op in r["camino"]:
            print("  ", est, op)
