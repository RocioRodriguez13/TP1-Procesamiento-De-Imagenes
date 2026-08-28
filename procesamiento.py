import math
import random
from PIL import Image
from generadores import generador_gaussiano, generador_exponencial

def calcular_histograma(img_pil):
    ancho, alto = img_pil.size
    histograma = [0] * 256
    for y in range(alto):
        for x in range(ancho):
            r, g, b = img_pil.getpixel((x, y))
            gris = int((r + g + b) / 3)
            histograma[gris] += 1
    return histograma

def aplicar_potencia(img_pil, gamma):
    ancho, alto = img_pil.size
    resultado = Image.new("RGB", (ancho, alto))
    tabla = [int(255 * ((i / 255) ** gamma)) for i in range(256)]
    for y in range(alto):
        for x in range(ancho):
            r, g, b = img_pil.getpixel((x, y))
            resultado.putpixel((x, y), (tabla[r], tabla[g], tabla[b]))
    return resultado

def aplicar_negativo(img_pil):
    ancho, alto = img_pil.size
    resultado = Image.new("RGB", (ancho, alto))
    for y in range(alto):
        for x in range(ancho):
            r, g, b = img_pil.getpixel((x, y))
            resultado.putpixel((x, y), (255 - r, 255 - g, 255 - b))
    return resultado

def ecualizar_histograma(img_pil):
    ancho, alto = img_pil.size
    n = ancho * alto
    n_i = calcular_histograma(img_pil)

    s = [0.0] * 256
    acumulado = 0
    for k in range(256):
        acumulado += n_i[k]
        s[k] = acumulado / n

    s_min = min(valor for valor in s if valor > 0)
    tabla = [0] * 256
    for k in range(256):
        valor = 255 * ((s[k] - s_min) / (1 - s_min))
        tabla[k] = max(0, min(255, int(valor)))

    resultado = Image.new("RGB", (ancho, alto))
    for y in range(alto):
        for x in range(ancho):
            r, g, b = img_pil.getpixel((x, y))
            resultado.putpixel((x, y), (tabla[r], tabla[g], tabla[b]))

    return resultado

def contaminar_gaussiano(img_pil, porcentaje, mu, sigma):
    ancho, alto = img_pil.size
    resultado = img_pil.copy()
    total_pixeles = ancho * alto
    cantidad_a_contaminar = int(total_pixeles * porcentaje / 100)

    coordenadas = [(x, y) for x in range(ancho) for y in range(alto)]
    elegidas = random.sample(coordenadas, cantidad_a_contaminar)
    ruido = generador_gaussiano(mu, sigma, cantidad_a_contaminar)

    for (x, y), r_val in zip(elegidas, ruido):
        pr, pg, pb = resultado.getpixel((x, y))
        nr = max(0, min(255, int(pr + r_val)))
        ng = max(0, min(255, int(pg + r_val)))
        nb = max(0, min(255, int(pb + r_val)))
        resultado.putpixel((x, y), (nr, ng, nb))

    return resultado

def contaminar_exponencial(img_pil, porcentaje, lambd):
    ancho, alto = img_pil.size
    resultado = img_pil.copy()
    total_pixeles = ancho * alto
    cantidad_a_contaminar = int(total_pixeles * porcentaje / 100)

    coordenadas = [(x, y) for x in range(ancho) for y in range(alto)]
    elegidas = random.sample(coordenadas, cantidad_a_contaminar)
    ruido = generador_exponencial(lambd, cantidad_a_contaminar)

    for (x, y), r_val in zip(elegidas, ruido):
        pr, pg, pb = resultado.getpixel((x, y))
        nr = max(0, min(255, int(pr * r_val)))
        ng = max(0, min(255, int(pg * r_val)))
        nb = max(0, min(255, int(pb * r_val)))
        resultado.putpixel((x, y), (nr, ng, nb))

    return resultado

def generar_ruido_sal_pimienta(img_pil, densidad):
    ancho, alto = img_pil.size
    resultado = img_pil.copy()
    total_pixeles = ancho * alto
    cantidad_a_contaminar = int(total_pixeles * densidad / 100)

    coordenadas = [(x, y) for x in range(ancho) for y in range(alto)]
    elegidas = random.sample(coordenadas, cantidad_a_contaminar)

    for (x, y) in elegidas:
        if random.random() < 0.5:
            resultado.putpixel((x, y), (255, 255, 255))
        else:
            resultado.putpixel((x, y), (0, 0, 0))

    return resultado


def obtener_ventana_rgb(img_pil, x, y, radio_mascara):
    """
    No se aplica padding: se asume que la máscara entra completa en la imagen.
    """
    vecindad_r, vecindad_g, vecindad_b = [], [], []
    for dy in range(-radio_mascara, radio_mascara + 1):
        for dx in range(-radio_mascara, radio_mascara + 1):
            r, g, b = img_pil.getpixel((x + dx, y + dy))
            vecindad_r.append(r)
            vecindad_g.append(g)
            vecindad_b.append(b)
    return vecindad_r, vecindad_g, vecindad_b

def aplicar_filtro_media_rgb(img_pil, tamano_mascara=3):
    img_pil = img_pil.convert("RGB")
    ancho, alto = img_pil.size
    radio_mascara = tamano_mascara // 2
    resultado = Image.new("RGB", (ancho, alto))

    for y in range(radio_mascara, alto - radio_mascara):
        for x in range(radio_mascara, ancho - radio_mascara):
            vr, vg, vb = obtener_ventana_rgb(img_pil, x, y, radio_mascara)
            r = int(sum(vr) / len(vr))
            g = int(sum(vg) / len(vg))
            b = int(sum(vb) / len(vb))
            resultado.putpixel((x, y), (r, g, b))

    return resultado


def aplicar_filtro_mediana_rgb(img_pil, tamano_mascara=3):
    img_pil = img_pil.convert("RGB")
    ancho, alto = img_pil.size
    radio_mascara = tamano_mascara // 2
    resultado = Image.new("RGB", (ancho, alto))

    def mediana_de(lista):
        lista.sort()
        n = len(lista)
        if n % 2 == 0:
            return int((lista[n // 2 - 1] + lista[n // 2]) / 2)
        return lista[n // 2]

    for y in range(radio_mascara, alto - radio_mascara):
        for x in range(radio_mascara, ancho - radio_mascara):
            vr, vg, vb = obtener_ventana_rgb(img_pil, x, y, radio_mascara)
            r, g, b = mediana_de(vr), mediana_de(vg), mediana_de(vb)
            resultado.putpixel((x, y), (r, g, b))

    return resultado


def aplicar_mediana_ponderada_3x3_rgb(img_pil):
    img_pil = img_pil.convert("RGB")
    ancho, alto = img_pil.size
    radio_mascara = 1
    resultado = Image.new("RGB", (ancho, alto))

    mascara = [1, 2, 1,
               2, 4, 2,
               1, 2, 1]

    def mediana_ponderada_de(lista):
        lista_ponderada = []
        for valor, peso in zip(lista, mascara):
            lista_ponderada.extend([valor] * peso)
        lista_ponderada.sort()
        n = len(lista_ponderada)
        if n % 2 == 0:
            return int((lista_ponderada[n // 2 - 1] + lista_ponderada[n // 2]) / 2)
        return lista_ponderada[n // 2]

    for y in range(radio_mascara, alto - radio_mascara):
        for x in range(radio_mascara, ancho - radio_mascara):
            vr, vg, vb = obtener_ventana_rgb(img_pil, x, y, radio_mascara)
            r = mediana_ponderada_de(vr)
            g = mediana_ponderada_de(vg)
            b = mediana_ponderada_de(vb)
            resultado.putpixel((x, y), (r, g, b))

    return resultado


def aplicar_filtro_gaussiano_rgb(img_pil, sigma=1.0):
    img_pil = img_pil.convert("RGB")

    tamano_mascara = int(2 * sigma + 1)
    if tamano_mascara % 2 == 0:
        tamano_mascara += 1
    radio_mascara = tamano_mascara // 2

    ancho, alto = img_pil.size
    resultado = Image.new("RGB", (ancho, alto))

    # La máscara gaussiana es la misma para los tres canales,
    # así que se calcula una sola vez, fuera del loop de píxeles.
    mascara = []
    suma_pesos = 0.0
    for dy in range(-radio_mascara, radio_mascara + 1):
        for dx in range(-radio_mascara, radio_mascara + 1):
            peso = math.exp(-(dx**2 + dy**2) / (2 * sigma**2))
            mascara.append(peso)
            suma_pesos += peso
    mascara = [p / suma_pesos for p in mascara]

    for y in range(radio_mascara, alto - radio_mascara):
        for x in range(radio_mascara, ancho - radio_mascara):
            vr, vg, vb = obtener_ventana_rgb(img_pil, x, y, radio_mascara)
            r = max(0, min(255, int(round(sum(v * p for v, p in zip(vr, mascara))))))
            g = max(0, min(255, int(round(sum(v * p for v, p in zip(vg, mascara))))))
            b = max(0, min(255, int(round(sum(v * p for v, p in zip(vb, mascara))))))
            resultado.putpixel((x, y), (r, g, b))

    return resultado


def aplicar_realce_bordes_rgb(img_pil):
    img_pil = img_pil.convert("RGB")
    ancho, alto = img_pil.size
    radio_mascara = 1
    resultado = Image.new("RGB", (ancho, alto))

    mascara = [-1/9, -1/9, -1/9,
               -1/9,  8/9, -1/9,
               -1/9, -1/9, -1/9]

    for y in range(radio_mascara, alto - radio_mascara):
        for x in range(radio_mascara, ancho - radio_mascara):
            vr, vg, vb = obtener_ventana_rgb(img_pil, x, y, radio_mascara)
            r = max(0, min(255, int(round(sum(v*m for v,m in zip(vr, mascara)))) + 128))
            g = max(0, min(255, int(round(sum(v*m for v,m in zip(vg, mascara)))) + 128))
            b = max(0, min(255, int(round(sum(v*m for v,m in zip(vb, mascara)))) + 128))
            resultado.putpixel((x, y), (r, g, b))

    return resultado