import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
import procesamiento


class VentanaResultado(tk.Toplevel):
    def __init__(self, parent, titulo, imagen_pil, imagen_previa=None):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("600x600")

        self.imagen_pil = imagen_pil
        self.imagen_previa = imagen_previa
        self.imagen_tk = None

        btn_frame = ttk.Frame(self, padding=5)
        btn_frame.pack(side="top", fill="x")
        ttk.Button(btn_frame, text="Guardar Resultado", command=self.guardar).pack(side="left", padx=2)

        if self.imagen_previa is not None:
            ttk.Button(btn_frame, text="Comparar Histogramas", command=self.comparar_histogramas).pack(side="left", padx=5)

        self.canvas = tk.Canvas(self, bg="#222222")
        self.canvas.pack(expand=True, fill="both", padx=10, pady=10)
        self.after(100, self.mostrar)

    def mostrar(self):
        w = max(self.canvas.winfo_width(), 100)
        h = max(self.canvas.winfo_height(), 100)
        img_copia = self.imagen_pil.copy()
        img_copia.thumbnail((w, h))

        from PIL import ImageTk
        self.imagen_tk = ImageTk.PhotoImage(img_copia)
        self.canvas.delete("all")
        self.canvas.create_image(w // 2, h // 2, image=self.imagen_tk, anchor="center")

    def guardar(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".png")
        if ruta:
            self.imagen_pil.save(ruta)
            messagebox.showinfo("Éxito", "Resultado guardado correctamente.")

    def comparar_histogramas(self):
        hist1 = procesamiento.calcular_histograma(self.imagen_previa)
        hist2 = procesamiento.calcular_histograma(self.imagen_pil)

        plt.figure("Comparación de Histogramas", figsize=(12, 4))
        plt.subplot(1, 2, 1)
        plt.bar(range(256), hist1, color="gray", width=1.0)
        plt.title("1ª Ecualización")
        plt.xlabel("Nivel de Gris")
        plt.ylabel("Cantidad de Píxeles")
        plt.xlim([0, 255])
        plt.grid(True, linestyle="--", alpha=0.5)

        plt.subplot(1, 2, 2)
        plt.bar(range(256), hist2, color="gray", width=1.0)
        plt.title("2ª Ecualización")
        plt.xlabel("Nivel de Gris")
        plt.ylabel("Cantidad de Píxeles")
        plt.xlim([0, 255])
        plt.grid(True, linestyle="--", alpha=0.5)

        plt.tight_layout()
        plt.show()