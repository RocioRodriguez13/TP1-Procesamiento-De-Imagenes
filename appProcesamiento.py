import math
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
import matplotlib.pyplot as plt
from PIL import Image, ImageTk

# Importaciones de los demás móduloss
import procesamiento
from generadores import generador_gaussiano, generador_exponencial
from ventana_resultado import VentanaResultado


class AppProcesamiento(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Procesamiento de Imágenes")
        self.geometry("1050x700")

        self.imagen_original = None
        self.imagen_tk = None

        self.rect_id = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None

        self.panel_botones = ttk.Frame(self, padding=10)
        self.panel_botones.pack(side="left", fill="y")

        ttk.Label(self.panel_botones, text="Controles de Procesamiento", font=("Arial", 11, "bold")).pack(pady=(0, 10))

        ttk.Button(self.panel_botones, text="Cargar Imagen", command=self.cargar_imagen).pack(fill="x", pady=2)
        ttk.Button(self.panel_botones, text="Guardar Imagen", command=self.guardar_imagen).pack(fill="x", pady=2)
        ttk.Separator(self.panel_botones, orient="horizontal").pack(fill="x", pady=8)

        ttk.Button(self.panel_botones, text="Modificar Píxel (0,0)", command=self.modificar_pixel_ejemplo).pack(fill="x", pady=2)
        ttk.Button(self.panel_botones, text="Copiar Región", command=self.copiar_region_seleccionada).pack(fill="x", pady=2)
        ttk.Separator(self.panel_botones, orient="horizontal").pack(fill="x", pady=8)

        ttk.Button(self.panel_botones, text="Restar Imágenes", command=self.restar_imagenes).pack(fill="x", pady=2)
        ttk.Separator(self.panel_botones, orient="horizontal").pack(fill="x", pady=8)

        ttk.Button(self.panel_botones, text="Info de Región Seleccionada", command=self.calcular_info_region).pack(fill="x", pady=2)
        ttk.Separator(self.panel_botones, orient="horizontal").pack(fill="x", pady=8)

        ttk.Button(self.panel_botones, text="Función de Potencia (γ)", command=self.aplicar_potencia).pack(fill="x", pady=2)
        ttk.Button(self.panel_botones, text="Negativo", command=self.aplicar_negativo).pack(fill="x", pady=2)
        ttk.Button(self.panel_botones, text="Histograma de Grises", command=self.mostrar_histograma).pack(fill="x", pady=2)
        ttk.Button(self.panel_botones, text="Umbralización", command=self.aplicar_umbral).pack(fill="x", pady=2)
        ttk.Button(self.panel_botones, text="Ecualizar Histograma", command=self.aplicar_ecualizacion).pack(fill="x", pady=2)
        ttk.Button(self.panel_botones, text="Re-ecualizar", command=self.aplicar_reecualizacion).pack(fill="x", pady=2)
        ttk.Separator(self.panel_botones, orient="horizontal").pack(fill="x", pady=8)

        ttk.Button(self.panel_botones, text="Generador Gaussiano", command=self.generar_gaussiana).pack(fill="x", pady=2)
        ttk.Button(self.panel_botones, text="Generador Exponencial", command=self.generar_exponencial).pack(fill="x", pady=2)
        ttk.Separator(self.panel_botones, orient="horizontal").pack(fill="x", pady=8)

        ttk.Button(self.panel_botones, text="Ruido Gaussiano Aditivo", command=self.aplicar_ruido_gaussiano).pack(fill="x", pady=2)
        ttk.Button(self.panel_botones, text="Ruido Exponencial Multiplicativo", command=self.aplicar_ruido_exponencial).pack(fill="x", pady=2)
        ttk.Button(self.panel_botones, text="Ruido Sal y Pimienta", command=self.aplicar_sal_pimienta).pack(fill="x", pady=2)
        ttk.Separator(self.panel_botones, orient="horizontal").pack(fill="x", pady=8)

        ttk.Label(self.panel_botones, text="Filtros Espaciales", font=("Arial", 10, "bold")).pack(pady=2)
        ttk.Button(self.panel_botones, text="Filtro Media", command=lambda: self.ejecutar_filtro("media")).pack(fill="x", pady=2)
        ttk.Button(self.panel_botones, text="Filtro Mediana", command=lambda: self.ejecutar_filtro("mediana")).pack(fill="x", pady=2)
        ttk.Button(self.panel_botones, text="Mediana Ponderada", command=lambda: self.ejecutar_filtro("mediana_p")).pack(fill="x", pady=2)
        ttk.Button(self.panel_botones, text="Filtro Gaussiano", command=lambda: self.ejecutar_filtro("gauss")).pack(fill="x", pady=2)
        ttk.Button(self.panel_botones, text="Realce de Bordes", command=lambda: self.ejecutar_filtro("realce")).pack(fill="x", pady=2)

        self.lbl_info = ttk.Label(self.panel_botones, text="Haz clic o arrastra sobre la imagen.", wraplength=180)
        self.lbl_info.pack(pady=15, side="bottom")

        self.canvas = tk.Canvas(self, bg="#333333")
        self.canvas.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def cargar_imagen(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Todas las imágenes", "*.png *.jpg *.jpeg *.bmp *.pgm *.ppm *.tif *.tiff *.raw"), ("Todos los archivos", "*.*")]
        )
        if ruta:
            try:
                if ruta.lower().endswith(".raw"):
                    img = self.leer_archivo_raw(ruta)
                    if img:
                        self.imagen_original = img
                        self.mostrar_imagen(self.imagen_original)
                else:
                    self.imagen_original = Image.open(ruta).convert("RGB")
                    self.mostrar_imagen(self.imagen_original)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{e}")

    def leer_archivo_raw(self, ruta):
        try:
            with open(ruta, "rb") as f:
                bytes_data = f.read()

            total_bytes = len(bytes_data)
            lado = int(math.sqrt(total_bytes))

            if lado * lado != total_bytes:
                ancho = simpledialog.askinteger("Imagen RAW", f"El archivo pesa {total_bytes} bytes.\nIngrese ANCHO:", initialvalue=lado)
                if not ancho:
                    return None
                alto = total_bytes // ancho
            else:
                ancho = lado
                alto = lado

            return Image.frombytes("L", (ancho, alto), bytes_data[:ancho * alto]).convert("RGB")
        except Exception as e:
            messagebox.showerror("Error RAW", f"No se pudo cargar el archivo RAW:\n{e}")
            return None

    def guardar_imagen(self):
        if self.imagen_original is None:
            messagebox.showwarning("Atención", "No hay ninguna imagen cargada.")
            return

        ruta = filedialog.asksaveasfilename(defaultextension=".png")
        if ruta:
            self.imagen_original.save(ruta)
            messagebox.showinfo("Éxito", "Imagen guardada.")

    def modificar_pixel_ejemplo(self):
        if self.imagen_original is None:
            messagebox.showwarning("Atención", "Primero cargá una imagen.")
            return
        p_val = self.imagen_original.getpixel((0, 0))
        self.imagen_original.putpixel((0, 0), (255, 0, 0))
        self.mostrar_imagen(self.imagen_original)
        messagebox.showinfo("Puntos 1c/1d", f"El valor original del píxel (0,0) era: {p_val}.\nSe pintó de Rojo (255, 0, 0).")

    def copiar_region_seleccionada(self):
        box = self.obtener_coordenadas_imagen()
        if not box:
            messagebox.showwarning("Atención", "Seleccioná primero un área con el mouse.")
            return

        x1, y1, x2, y2 = box
        ancho = x2 - x1
        alto = y2 - y1

        region = Image.new("RGB", (ancho, alto))
        for j in range(alto):
            for i in range(ancho):
                valor = self.imagen_original.getpixel((x1 + i, y1 + j))
                region.putpixel((i, j), valor)

        VentanaResultado(self, "Copia de Región", region)

    def restar_imagenes(self):
        if self.imagen_original is None:
            messagebox.showwarning("Atención", "Primero cargá la imagen base.")
            return

        ruta2 = filedialog.askopenfilename(
            filetypes=[("Todas las imágenes", "*.png *.jpg *.jpeg *.bmp *.pgm *.ppm *.tif *.tiff *.raw"), ("Todos los archivos", "*.*")]
        )
        if not ruta2:
            return

        try:
            if ruta2.lower().endswith(".raw"):
                img2 = self.leer_archivo_raw(ruta2)
            else:
                img2 = Image.open(ruta2).convert("RGB")

            if img2.size != self.imagen_original.size:
                img2 = img2.resize(self.imagen_original.size)

            ancho, alto = self.imagen_original.size
            resultado = Image.new("RGB", (ancho, alto))

            for y in range(alto):
                for x in range(ancho):
                    r1, g1, b1 = self.imagen_original.getpixel((x, y))
                    r2, g2, b2 = img2.getpixel((x, y))
                    resultado.putpixel((x, y), (abs(r1 - r2), abs(g1 - g2), abs(b1 - b2)))

            VentanaResultado(self, "Resultado de la Resta", resultado)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la segunda imagen:\n{e}")

    def aplicar_potencia(self):
        if self.imagen_original is None:
            messagebox.showwarning("Atención", "Primero cargá una imagen.")
            return

        gamma = simpledialog.askfloat("Función de Potencia", "Ingresá γ (0 < γ < 2, γ ≠ 1):", minvalue=0.01, maxvalue=1.99)
        if gamma and gamma != 1:
            res = procesamiento.aplicar_potencia(self.imagen_original, gamma)
            VentanaResultado(self, f"Función Potencia (γ={gamma})", res)

    def aplicar_negativo(self):
        if self.imagen_original is None:
            messagebox.showwarning("Atención", "Primero cargá una imagen.")
            return
        res = procesamiento.aplicar_negativo(self.imagen_original)
        VentanaResultado(self, "Negativo", res)

    def mostrar_histograma(self):
        if self.imagen_original is None:
            messagebox.showwarning("Atención", "Primero cargá una imagen.")
            return

        histograma = procesamiento.calcular_histograma(self.imagen_original)
        plt.figure(figsize=(8, 4))
        plt.bar(range(256), histograma, width=1, color="gray")
        plt.title("Histograma de Niveles de Gris")
        plt.xlabel("Nivel de gris (0-255)")
        plt.ylabel("Cantidad de píxeles")
        plt.xlim(0, 255)
        plt.tight_layout()
        plt.show()

    def aplicar_umbral(self):
        if self.imagen_original is None:
            messagebox.showwarning("Atención", "Primero cargá una imagen.")
            return

        umbral = simpledialog.askinteger("Umbralización", "Ingresá el umbral (0-255):", minvalue=0, maxvalue=255)
        if umbral is not None:
            ancho, alto = self.imagen_original.size
            resultado = Image.new("RGB", (ancho, alto))
            for y in range(alto):
                for x in range(ancho):
                    r, g, b = self.imagen_original.getpixel((x, y))
                    gris = int((r + g + b) / 3)
                    valor = 255 if gris >= umbral else 0
                    resultado.putpixel((x, y), (valor, valor, valor))
            VentanaResultado(self, f"Umbralización ({umbral})", resultado)

    def aplicar_ecualizacion(self):
        if self.imagen_original is None:
            messagebox.showwarning("Atención", "Primero cargá una imagen.")
            return
        res = procesamiento.ecualizar_histograma(self.imagen_original)
        VentanaResultado(self, "Ecualización de Histograma", res)

    def aplicar_reecualizacion(self):
        if self.imagen_original is None:
            messagebox.showwarning("Atención", "Primero cargá una imagen.")
            return
        img_ec1 = procesamiento.ecualizar_histograma(self.imagen_original)
        img_ec2 = procesamiento.ecualizar_histograma(img_ec1)
        VentanaResultado(self, "Re-ecualización de Histograma", img_ec2, imagen_previa=img_ec1)

    def generar_gaussiana(self):
        mu = simpledialog.askfloat("Gaussiana", "Media (µ):", initialvalue=0)
        sigma = simpledialog.askfloat("Gaussiana", "Desvío (σ):", minvalue=0.0001, initialvalue=1)
        cant = simpledialog.askinteger("Gaussiana", "Cantidad:", minvalue=1, initialvalue=10000)
        if mu is not None and sigma is not None and cant:
            datos = generador_gaussiano(mu, sigma, cant)
            plt.figure(figsize=(8, 4))
            plt.hist(datos, bins=50, color="steelblue", edgecolor="black")
            plt.title(f"Gaussiana (µ={mu}, σ={sigma})")
            plt.tight_layout()
            plt.show()

    def generar_exponencial(self):
        lambd = simpledialog.askfloat("Exponencial", "Parámetro λ:", minvalue=0.0001, initialvalue=1)
        cant = simpledialog.askinteger("Exponencial", "Cantidad:", minvalue=1, initialvalue=10000)
        if lambd is not None and cant:
            datos = generador_exponencial(lambd, cant)
            plt.figure(figsize=(8, 4))
            plt.hist(datos, bins=50, color="indianred", edgecolor="black")
            plt.title(f"Exponencial (λ={lambd})")
            plt.tight_layout()
            plt.show()

    def aplicar_ruido_gaussiano(self):
        if self.imagen_original is None:
            messagebox.showwarning("Atención", "Primero cargá una imagen.")
            return
        porc = simpledialog.askfloat("Ruido Gaussiano", "% Píxeles (0-100):", minvalue=0, maxvalue=100, initialvalue=10)
        mu = simpledialog.askfloat("Ruido Gaussiano", "Media (µ):", initialvalue=0)
        sigma = simpledialog.askfloat("Ruido Gaussiano", "Desvío (σ):", minvalue=0.0001, initialvalue=25)
        if porc is not None and mu is not None and sigma is not None:
            res = procesamiento.contaminar_gaussiano(self.imagen_original, porc, mu, sigma)
            VentanaResultado(self, f"Ruido Gaussiano ({porc}%)", res)

    def aplicar_ruido_exponencial(self):
        if self.imagen_original is None:
            messagebox.showwarning("Atención", "Primero cargá una imagen.")
            return
        porc = simpledialog.askfloat("Ruido Exponencial", "% Píxeles (0-100):", minvalue=0, maxvalue=100, initialvalue=10)
        lambd = simpledialog.askfloat("Ruido Exponencial", "Parámetro λ:", minvalue=0.0001, initialvalue=1)
        if porc is not None and lambd is not None:
            res = procesamiento.contaminar_exponencial(self.imagen_original, porc, lambd)
            VentanaResultado(self, f"Ruido Exponencial ({porc}%)", res)

    def aplicar_sal_pimienta(self):
        if self.imagen_original is None:
            messagebox.showwarning("Atención", "Primero cargá una imagen.")
            return
        densidad = simpledialog.askfloat("Sal y Pimienta", "Densidad (%):", minvalue=0, maxvalue=100, initialvalue=5)
        if densidad is not None:
            res = procesamiento.generar_ruido_sal_pimienta(self.imagen_original, densidad)
            VentanaResultado(self, f"Sal y Pimienta ({densidad}%)", res)

    def ejecutar_filtro(self, tipo):
        if self.imagen_original is None:
            messagebox.showwarning("Atención", "Primero cargá una imagen.")
            return

        if tipo == "media":
            tam = simpledialog.askinteger("Filtro Media", "Tamaño (impar):", minvalue=3, initialvalue=3)
            if tam:
                res = procesamiento.aplicar_filtro_media(self.imagen_original, tam)
                VentanaResultado(self, f"Filtro Media ({tam}x{tam})", res)

        elif tipo == "mediana":
            tam = simpledialog.askinteger("Filtro Mediana", "Tamaño (impar):", minvalue=3, initialvalue=3)
            if tam:
                res = procesamiento.aplicar_filtro_mediana(self.imagen_original, tam)
                VentanaResultado(self, f"Filtro Mediana ({tam}x{tam})", res)

        elif tipo == "mediana_p":
            res = procesamiento.aplicar_mediana_ponderada_3x3(self.imagen_original)
            VentanaResultado(self, "Mediana Ponderada (3x3)", res)

        elif tipo == "gauss":
            sigma = simpledialog.askfloat("Filtro Gaussiano", "Valor σ:", minvalue=0.1, initialvalue=1.0)
            if sigma:
                res = procesamiento.aplicar_filtro_gaussiano(self.imagen_original, sigma)
                VentanaResultado(self, f"Filtro Gauss (σ={sigma})", res)

        elif tipo == "realce":
            res = procesamiento.aplicar_realce_bordes(self.imagen_original)
            VentanaResultado(self, "Realce de Bordes", res)

    def calcular_info_region(self):
        box = self.obtener_coordenadas_imagen()
        if not box:
            messagebox.showwarning("Atención", "Seleccioná una región con el mouse.")
            return

        x1, y1, x2, y2 = box
        region = self.imagen_original.crop((x1, y1, x2, y2))
        cant_pixels = region.width * region.height

        pixeles = list(region.getdata())
        suma_r = sum(p[0] for p in pixeles)
        suma_g = sum(p[1] for p in pixeles)
        suma_b = sum(p[2] for p in pixeles)

        prom_r, prom_g, prom_b = suma_r / cant_pixels, suma_g / cant_pixels, suma_b / cant_pixels
        prom_gris = (prom_r + prom_g + prom_b) / 3

        msg = (f"Píxeles: {cant_pixels}\n"
               f"Promedio Gris: {prom_gris:.2f}\n"
               f"Promedio RGB: R={prom_r:.1f}, G={prom_g:.1f}, B={prom_b:.1f}")
        messagebox.showinfo("Info de Región", msg)

    def on_button_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

        box = self.obtener_coordenadas_imagen(single_point=(event.x, event.y))
        if box and self.imagen_original:
            px, py = box[0], box[1]
            val = self.imagen_original.getpixel((px, py))
            self.lbl_info.config(text=f"Píxel ({px}, {py})\nValor: {val}")

    def on_move_press(self, event):
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        self.end_x, self.end_y = event.x, event.y

    def obtener_coordenadas_imagen(self, single_point=None):
        if self.imagen_original is None:
            return None

        cw, ch = max(self.canvas.winfo_width(), 1), max(self.canvas.winfo_height(), 1)
        iw, ih = self.imagen_original.size

        escala = min(cw / iw, ch / ih, 1.0)
        disp_w, disp_h = iw * escala, ih * escala

        offset_x, offset_y = (cw - disp_w) / 2, (ch - disp_h) / 2

        if single_point:
            px = int((single_point[0] - offset_x) / escala)
            py = int((single_point[1] - offset_y) / escala)
            if 0 <= px < iw and 0 <= py < ih:
                return (px, py)
            return None

        if self.start_x is None or self.end_x is None:
            return None

        x1 = int((min(self.start_x, self.end_x) - offset_x) / escala)
        y1 = int((min(self.start_y, self.end_y) - offset_y) / escala)
        x2 = int((max(self.start_x, self.end_x) - offset_x) / escala)
        y2 = int((max(self.start_y, self.end_y) - offset_y) / escala)

        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(iw, x2), min(ih, y2)

        if x2 > x1 and y2 > y1:
            return (x1, y1, x2, y2)
        return None

    def mostrar_imagen(self, img_pil):
        w, h = max(self.canvas.winfo_width(), 100), max(self.canvas.winfo_height(), 100)
        img_copia = img_pil.copy()
        img_copia.thumbnail((w, h))

        self.imagen_tk = ImageTk.PhotoImage(img_copia)
        self.canvas.delete("all")
        self.canvas.create_image(w // 2, h // 2, image=self.imagen_tk, anchor="center")