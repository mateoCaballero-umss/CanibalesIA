import tkinter as tk
from tkinter import ttk

import busquedas as b

ANCHO, ALTO = 780, 330
ORILLA_IZQ_FIN, ORILLA_DER_INI = 230, 550
BOTE_X_IZQ, BOTE_X_DER = 240, 440      # esquina izquierda del bote
BOTE_ANCHO, BOTE_Y = 100, 215
RADIO = 14
FRAMES_CRUCE = 30


class App:
    def __init__(self, root):
        self.root = root
        root.title("Misioneros y Can\u00edbales - B\u00fasqueda BFS vs DFS")
        self.resultados = {}
        self.token = 0            # para cancelar animaciones en curso

        self.canvas = tk.Canvas(root, width=ANCHO, height=ALTO, bg="white")
        self.canvas.pack(padx=10, pady=(10, 5))

        barra = ttk.Frame(root)
        barra.pack(pady=5)
        ttk.Button(barra, text="Resolver con BFS (amplitud)",
                   command=lambda: self.resolver("BFS")).grid(row=0, column=0, padx=4)
        ttk.Button(barra, text="Resolver con DFS (profundidad)",
                   command=lambda: self.resolver("DFS")).grid(row=0, column=1, padx=4)
        ttk.Button(barra, text="Comparar ambos",
                   command=self.comparar).grid(row=0, column=2, padx=4)
        ttk.Button(barra, text="Reiniciar",
                   command=self.reiniciar).grid(row=0, column=3, padx=4)

        self.estado_lbl = ttk.Label(root, text="Elige un algoritmo para comenzar")
        self.estado_lbl.pack()

        inferior = ttk.Frame(root)
        inferior.pack(fill="both", expand=True, padx=10, pady=10)

        self.lista = tk.Listbox(inferior, width=48, height=12)
        self.lista.pack(side="left", fill="y")

        cols = ("alg", "sol", "cruces", "gen", "exp", "mem", "t")
        self.tabla = ttk.Treeview(inferior, columns=cols, show="headings", height=4)
        titulos = ["Algoritmo", "Soluci\u00f3n", "Cruces", "Generados",
                   "Expandidos", "M\u00e1x. memoria", "Tiempo (ms)"]
        for c, t in zip(cols, titulos):
            self.tabla.heading(c, text=t)
            self.tabla.column(c, width=85, anchor="center")
        self.tabla.pack(side="left", fill="x", expand=True, padx=(10, 0), anchor="n")

        self.dibujar_estado(b.INICIAL)

    # ---------------------------------------------------------- dibujo
    def _grupo(self, x0, y0, m, c, hacia_derecha=True):
        """Dibuja m misioneros (azul) y c canibales (rojo) en fila."""
        paso = 2 * RADIO + 6
        i = 0
        for color, n, letra in (("#3b6fd4", m, "M"), ("#d43b3b", c, "C")):
            for _ in range(n):
                x = x0 + i * paso if hacia_derecha else x0 - i * paso
                self.canvas.create_oval(x - RADIO, y0 - RADIO, x + RADIO, y0 + RADIO,
                                        fill=color, outline="black")
                self.canvas.create_text(x, y0, text=letra, fill="white",
                                        font=("Arial", 10, "bold"))
                i += 1

    def _escena(self, izq, der, bote_x, pasajeros):
        cv = self.canvas
        cv.delete("all")
        # orillas y rio
        cv.create_rectangle(0, 0, ORILLA_IZQ_FIN, ALTO, fill="#c9e4a5", outline="")
        cv.create_rectangle(ORILLA_DER_INI, 0, ANCHO, ALTO, fill="#c9e4a5", outline="")
        cv.create_rectangle(ORILLA_IZQ_FIN, 0, ORILLA_DER_INI, ALTO, fill="#9ecbf0", outline="")
        cv.create_text(ORILLA_IZQ_FIN // 2, 20, text="Orilla izquierda",
                       font=("Arial", 11, "bold"))
        cv.create_text((ORILLA_DER_INI + ANCHO) // 2, 20, text="Orilla derecha",
                       font=("Arial", 11, "bold"))
        # personas en orillas (dos filas: misioneros arriba, canibales abajo)
        self._grupo(30, 100, izq[0], 0)
        self._grupo(30, 150, 0, izq[1])
        self._grupo(ORILLA_DER_INI + 30, 100, der[0], 0)
        self._grupo(ORILLA_DER_INI + 30, 150, 0, der[1])
        # bote
        cv.create_polygon(bote_x, BOTE_Y, bote_x + BOTE_ANCHO, BOTE_Y,
                          bote_x + BOTE_ANCHO - 15, BOTE_Y + 25, bote_x + 15, BOTE_Y + 25,
                          fill="#8b5a2b", outline="black")
        if pasajeros:
            self._grupo(bote_x + 25, BOTE_Y - 18, pasajeros[0], pasajeros[1])

    def dibujar_estado(self, estado):
        m, c, bote = estado
        x = BOTE_X_IZQ if bote == 0 else BOTE_X_DER
        self._escena((m, c), (b.TOTAL_M - m, b.TOTAL_C - c), x, None)

    def _dibujar_cruce(self, prev, op, frame):
        m, c, bote = prev
        dm, dc = op
        if bote == 0:
            izq, der = (m - dm, c - dc), (b.TOTAL_M - m, b.TOTAL_C - c)
            x0, x1 = BOTE_X_IZQ, BOTE_X_DER
        else:
            izq, der = (m, c), (b.TOTAL_M - m - dm, b.TOTAL_C - c - dc)
            x0, x1 = BOTE_X_DER, BOTE_X_IZQ
        x = x0 + (x1 - x0) * frame / FRAMES_CRUCE
        self._escena(izq, der, x, op)

    # ------------------------------------------------------- acciones
    def reiniciar(self):
        self.token += 1
        self.lista.delete(0, tk.END)
        self.estado_lbl.config(text="Elige un algoritmo para comenzar")
        self.dibujar_estado(b.INICIAL)

    def _ejecutar(self, nombre):
        r = b.bfs() if nombre == "BFS" else b.dfs()
        self.resultados[nombre] = r
        self._actualizar_tabla()
        return r

    def _actualizar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        for nombre in ("BFS", "DFS"):
            r = self.resultados.get(nombre)
            if r:
                self.tabla.insert("", tk.END, values=(
                    nombre, "S\u00ed" if r["encontrada"] else "No", r["costo"],
                    r["generados"], r["expandidos"], r["max_memoria"],
                    f"{r['tiempo_ms']:.3f}"))

    def comparar(self):
        self._ejecutar("BFS")
        self._ejecutar("DFS")
        self.estado_lbl.config(text="Comparaci\u00f3n actualizada (ver tabla)")

    def resolver(self, nombre):
        self.token += 1
        r = self._ejecutar(nombre)
        self.lista.delete(0, tk.END)
        if not r["encontrada"]:
            self.estado_lbl.config(text=f"{nombre}: sin soluci\u00f3n")
            return
        camino = r["camino"]
        self.estado_lbl.config(
            text=f"{nombre}: soluci\u00f3n con {r['costo']} cruces")
        self.lista.insert(tk.END, f"0. Estado inicial {camino[0][0]}")
        self._animar(camino, 0, 0, self.token)

    def _animar(self, camino, i, frame, token):
        if token != self.token:
            return                      # animacion cancelada
        if i >= len(camino) - 1:
            self.dibujar_estado(camino[-1][0])
            self.estado_lbl.config(
                text=self.estado_lbl.cget("text") + "  \u2714 Meta alcanzada")
            return
        prev = camino[i][0]
        nuevo, op = camino[i + 1]
        if frame <= FRAMES_CRUCE:
            self._dibujar_cruce(prev, op, frame)
            self.root.after(20, self._animar, camino, i, frame + 1, token)
        else:
            self.dibujar_estado(nuevo)
            self.lista.insert(
                tk.END, f"{i + 1}. {b.describir_operador(op, prev[2])} -> {nuevo}")
            self.lista.see(tk.END)
            self.root.after(500, self._animar, camino, i + 1, 0, token)


if __name__ == "__main__":
    ventana = tk.Tk()
    App(ventana)
    ventana.mainloop()
