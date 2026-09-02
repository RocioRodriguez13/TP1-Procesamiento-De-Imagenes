import math
import random
from PIL import Image
from generadores import generador_gaussiano, generador_exponencial


def calcular_histograma_relativo(img_pil):
    
    ancho, alto = img_pil.size      # Obtenemos el ancho y el alto de la imagen.
    total_pixeles = ancho * alto    # Calculamos la cantidad total de píxeles de la imagen.

    histograma = [0] * 256 # Lista de 256 posiciones, una por cada nivel de gris, inicializando todas las frecuencias en 0.
    
    for y in range(alto):       # Recorremos todas las filas de la imagen.
        for x in range(ancho):  # Recorremos todas las columnas de la imagen.

            r, g, b = img_pil.getpixel((x, y)) # Obtenemos los valores de los tres canales del píxel
            gris = int((r + g + b) / 3) # Convertimos el píxel a girscalculando el promedio de sus tres canales
            histograma[gris] += 1 # Aumentamos en 1 la cantidad de píxeles que tienen ese nivel de gris.
    
    return [frecuencia / total_pixeles for frecuencia in histograma] # Dividimos la frecuencia de cada nivel por el total de píxeles


def aplicar_potencia(img_pil, gamma):

    ancho, alto = img_pil.size  # Obtenemos el ancho y el alto de la imagen.
    resultado = Image.new("RGB", (ancho, alto)) # Creamos una imagen RGB del mismo tamaño para guardar el resultado
    tabla = [int(255 * ((i / 255) ** gamma)) for i in range(256)] # Creamos una tabla con la transformación potencia para los 256 niveles de intensidad.

    for y in range(alto):       # Recorremos todas las filas de la imagen.
        for x in range(ancho):  # Recorremos todas las columnas de la imagen.
            r, g, b = img_pil.getpixel((x, y)) # Obtenemos los valores de los tres canales del píxel

            # Aplicamos la transformación potencia a cada canal utilizando la tabla previamente calculada.
            resultado.putpixel((x, y), (tabla[r], tabla[g], tabla[b])) 

    return resultado


def aplicar_negativo(img_pil):
    ancho, alto = img_pil.size  # Obtenemos el ancho y el alto de la imagen.
    resultado = Image.new("RGB", (ancho, alto)) # Creamos una imagen RGB del mismo tamaño para guardar el resultado
    for y in range(alto):           # Recorremos todas las filas de la imagen.
        for x in range(ancho):      # Recorremos todas las columnas de la imagen.
            r, g, b = img_pil.getpixel((x, y))      # Obtenemos los valores de los tres canales del píxel
            resultado.putpixel((x, y), (255 - r, 255 - g, 255 - b))     # Aplicamos el negativo en cada canak
    return resultado


def ecualizar_histograma(img_pil):

    ancho, alto = img_pil.size      # Obtenemos el ancho y el alto de la imagen.
    n_i_relativo = calcular_histograma_relativo(img_pil)    # Calculamos el histograma relativo

    s = [0.0] * 256 # Creamos una lista de 256 posiciones para guardar la función de distribución acumulada.
    acumulado = 0.0 # Inicializamos el acumulado en cero.

    for k in range(256):    # Recorremos los 256 niveles de gris.
        acumulado += n_i_relativo[k]    # Acumulamos las frecuencias relativas de los niveles de gris hasta k.
        s[k] = acumulado    # Guardamos la frecuencia acumulada para ese nivel.

    s_min = min(valor for valor in s if valor > 0) # Buscamos la primera frecuencia acumulada que sea mayor que cero.
    tabla = [0] * 256   # Creamos una tabla de transformación

    for k in range(256):    # Recorremos los 256 niveles de gris.
        valor = 255 * ((s[k] - s_min) / (1 - s_min)) # Aplicamos la ecualización del histograma y los valores de 0 a 255.
        tabla[k] = max(0, min(255, int(valor))) # Convertimos el resultado a entero

    resultado = Image.new("RGB", (ancho, alto)) # Creamos una nueva imagen RGB para guardar la imagen ecualizada.

    
    for y in range(alto):        # Recorremos todas las filas de la imagen.
        for x in range(ancho):   # Recorremos todas las columnas de la imagen.

            r, g, b = img_pil.getpixel((x, y))
            resultado.putpixel((x, y), (tabla[r], tabla[g], tabla[b]))  # Aplicamos la tabla de transformación a cada canal

    return resultado


def contaminar_gaussiano(img_pil, porcentaje, mu, sigma):

    ancho, alto = img_pil.size  # Obtenemos el ancho y el alto
    resultado = img_pil.copy()  # Creamos una copia de la imagen original
    total_pixeles = ancho * alto    # Ccantidad total de píxeles de la imagen.
    cantidad_a_contaminar = int(total_pixeles * porcentaje / 100)   # Calculamos cuántos píxeles vamos a contaminar

    coordenadas = [(x, y) for x in range(ancho) for y in range(alto)] # Creamos una lista de las coordenadas de todos los píxeles
    elegidas = random.sample(coordenadas, cantidad_a_contaminar)  # Elegimos aleatoriamente los píxeles se van a contaminar
    ruido = generador_gaussiano(mu, sigma, cantidad_a_contaminar) # Generamos los valores de ruido gaussiano

    for (x, y), valor_ruido in zip(elegidas, ruido):  # Recorremos las coordenadas elegidas junto con los valores de ruido.

        pixel_r, pixel_g, pixel_b = resultado.getpixel((x, y)) # Valores RGB del píxel seleccionado

        # Sumamos el ruido a acda canal
        nuevo_r = max(0, min(255, int(pixel_r + valor_ruido)))
        nuevo_g = max(0, min(255, int(pixel_g + valor_ruido)))
        nuevo_b = max(0, min(255, int(pixel_b + valor_ruido)))

        resultado.putpixel((x, y), (nuevo_r, nuevo_g, nuevo_b))     # Guardamos el nuevo píxel RGB en la misma posición.

    return resultado



def contaminar_exponencial(img_pil, porcentaje, lambd):
    ancho, alto = img_pil.size  # Obtenemos el ancho y el alto
    resultado = img_pil.copy()  # Creamos una copia de la imagen original
    total_pixeles = ancho * alto    # Cantidad total de píxeles de la imagen.
    cantidad_a_contaminar = int(total_pixeles * porcentaje / 100)   # Calculamos cuántos píxeles vamos a contaminar

    coordenadas = [(x, y) for x in range(ancho) for y in range(alto)]  # Creamos una lista de las coordenadas de todos los píxeles
    elegidas = random.sample(coordenadas, cantidad_a_contaminar)    # Elegimos aleatoriamente los píxeles se van a contaminar
    ruido = generador_exponencial(lambd, cantidad_a_contaminar)     # Generamos los valores de ruido gaussiano

    for (x, y), valor_ruido in zip(elegidas, ruido):  # Recorremos las coordenadas elegidas junto con los valores de ruido.
        pixel_r, pixel_g, pixel_b = resultado.getpixel((x, y)) # Valores RGB del píxel seleccionado
        # Multiplicsmos el ruido a cada canal
        nuevo_r = max(0, min(255, int(pixel_r * valor_ruido)))
        nuevo_g = max(0, min(255, int(pixel_g * valor_ruido)))
        nuevo_b = max(0, min(255, int(pixel_b * valor_ruido)))
        resultado.putpixel((x, y), (nuevo_r, nuevo_g, nuevo_b))

    return resultado

def generar_ruido_sal_pimienta(img_pil, p):
    ancho, alto = img_pil.size  # Obtenemos el ancho y el alto
    resultado = img_pil.copy()  # Creamos una copia de la imagen original

    for y in range(alto):       # Recorremos todas las filas de la imagen.
        for x in range(ancho):  # Recorremos todas las filas de la imagen.
            valor = random.random()     #Tomamos un valor aleatorio entre 0 y 1 para cada pixel
            if valor <= p:          # Si el valor es menor a la probabilidad, el pixle va a ser negro 
                resultado.putpixel((x, y), (0, 0, 0))
            elif valor > 1 - p:     # Si el valor es mayor a 1 - la probabilidad, el pixel va a ser blanco 
                resultado.putpixel((x, y), (255, 255, 255))

    return resultado


def obtener_ventana(img_pil, x, y, radio_mascara):

    ancho, alto = img_pil.size      # Obtenemos el ancho y el alto
    vecindad_r, vecindad_g, vecindad_b = [], [], [] # Creamos tres listas vacías para guardar los valores de cada canales

    # El radio indica qué tan grande será la ventana.
    for dy in range(-radio_mascara, radio_mascara + 1): # Recorremos las filas de la ventana alrededor del píxel (x, y)
        for dx in range(-radio_mascara, radio_mascara + 1): # Recorremos las columnas de la ventana alrededor del píxel (x, y)

            # Calculamos la coordenada x del píxel vecino, max evita que sea menor que 0 y min evita que supere el ancho.
            xi = min(max(x + dx, 0), ancho - 1)

            # Calculamos la coordenada y del píxel vecino, max evita que sea menor que 0 y min evita que supere el alto.
            yi = min(max(y + dy, 0), alto - 1)

            r, g, b = img_pil.getpixel((xi, yi))    # Obtenemos los valores RGB del píxel vecino.

            # Agregamos el valor de  cada canal a su respectuva lista
            vecindad_r.append(r)
            vecindad_g.append(g)
            vecindad_b.append(b)

    return vecindad_r, vecindad_g, vecindad_b


def aplicar_filtro_media(img_pil, tamano_mascara=3):
    img_pil = img_pil.convert("RGB")    # Convertimos a RGB
    ancho, alto = img_pil.size          # Obtenemos el ancho y alto
    radio_mascara = tamano_mascara // 2 # Calculamos el radio de la máscara, una máscara de 3x3, el radio es 1.
    resultado = Image.new("RGB", (ancho, alto)) # Creamos una imagen del mismo tamaño para guardar los resultados

    for y in range(alto):       # Recorremos las filas
        for x in range(ancho):  # Recorremos las columnas

            # Obtenemos los valores de RGB de los píxeles que forman la ventana alrededor del píxel actual.
            vecindad_r, vecindad_g, vecindad_b = obtener_ventana(img_pil, x, y, radio_mascara)

            # Calculamos el promedio de los valores por canal
            r = int(sum(vecindad_r) / len(vecindad_r))
            g = int(sum(vecindad_g) / len(vecindad_g))
            b = int(sum(vecindad_b) / len(vecindad_b))
            resultado.putpixel((x, y), (r, g, b))  # Creamos un nuveo pixel con los valores calculados y lo agregamos a resultado

    return resultado


def mediana_de(lista):
    lista.sort()
    n = len(lista)
    if n % 2 == 0:
        return int((lista[n // 2 - 1] + lista[n // 2]) / 2)
    return lista[n // 2]

def aplicar_filtro_mediana(img_pil, tamano_mascara=3):
    img_pil = img_pil.convert("RGB")    # Convertimos a RGB
    ancho, alto = img_pil.size          # Obtenemos el ancho y alto
    radio_mascara = tamano_mascara // 2 # Calculamos el radio de la máscara, una máscara de 3x3, el radio es 1.
    resultado = Image.new("RGB", (ancho, alto)) # Creamos una imagen del mismo tamaño para guardar los resultados

    for y in range(alto):           # Recorremos las filas
        for x in range(ancho):      # Recorremos las columans

            # Obtenemos por separado los valores RGB de los píxeles que forman la ventana
            vecindad_r, vecindad_g, vecindad_b = obtener_ventana(img_pil, x, y, radio_mascara)
            # Calculamos la mediana de cada canal por separado.
            r, g, b = mediana_de(vecindad_r), mediana_de(vecindad_g), mediana_de(vecindad_b)
            resultado.putpixel((x, y), (r, g, b))

    return resultado


def aplicar_mediana_ponderada_3x3(img_pil):

    img_pil = img_pil.convert("RGB")        # Convertimos la imagen a RGB
    ancho, alto = img_pil.size              # Obtenemos el ancho y el alto
    radio_mascara = 1                       # Para una máscara 3x3 el radio es 1
    resultado = Image.new("RGB", (ancho, alto)) # Creamos una nueva imagen del mismo tamaño para guardar el resultado

    # Definimos los pesos de la máscara 3x3.
    mascara = [1, 2, 1,
                2, 4, 2,
                1, 2, 1]

    def mediana_ponderada_de(lista):

        lista_ponderada = []    # Creamos una lista vacía donde vamos a repetir cada valor según el peso que tenga

        for valor, peso in zip(lista, mascara): # Recorremos los valores de la ventana junto con sus pesos
            lista_ponderada.extend([valor] * peso)  # Repetimos cada valor tantas veces como indique su peso

        lista_ponderada.sort()      # Ordenamos los valores de menor a mayor
        n = len(lista_ponderada)

        return lista_ponderada[n // 2]      

    
    for y in range(alto):           # Recorremos todas las filas
        for x in range(ancho):      # Recorremos todas las columnas

            # Obtenemos los valores RGB de la ventana 3x3.
            vecindad_r, vecindad_g, vecindad_b = obtener_ventana(img_pil, x, y, radio_mascara)

            # Calculamos la mediana ponderada de cada canal
            r = mediana_ponderada_de(vecindad_r)
            g = mediana_ponderada_de(vecindad_g)
            b = mediana_ponderada_de(vecindad_b)

            resultado.putpixel((x, y), (r, g, b))   # Guardamos el nuevo píxel RGB en la misma posición.

    return resultado



def aplicar_filtro_gaussiano(img_pil, sigma=1.0):

    img_pil = img_pil.convert("RGB")        # Convertimos la imagen a RGB

    tamano_mascara = int(2 * sigma + 1)     # Calculamos el tamaño de la máscara
    radio_mascara = tamano_mascara // 2     # Calculamos el radio de la máscara

    ancho, alto = img_pil.size                      # Obtenemos el ancho y alto de la imagen
    resultado = Image.new("RGB", (ancho, alto))     # Creamos una imagen nueva del mismo tamaño

    mascara = []                    # Lista donde guardamos los pesos de la máscara
    suma_pesos = 0.0                # Variable para sumar todos los pesos

    # Recorremos todas las posiciones de la máscara
    for dy in range(-radio_mascara, radio_mascara + 1):
        for dx in range(-radio_mascara, radio_mascara + 1):

            # Calculamos el peso gaussiano para cada posición
            peso = math.exp(-(dx**2 + dy**2) / (2 * sigma**2))

            mascara.append(peso)     # Guardamos el peso en la máscara
            suma_pesos += peso        # Acumulamos la suma de los pesos

    mascara = [peso / suma_pesos for peso in mascara]   # Normalizamos los pesos para que su suma sea igual a 1

    # Recorremos todos los píxeles de la imagen
    for y in range(alto):
        for x in range(ancho):

            # Obtenemos los valores RGB de la ventana alrededor del píxel
            vecindad_r, vecindad_g, vecindad_b = obtener_ventana(img_pil, x, y, radio_mascara)

            # Calculamos el nuevo valor de cada canal usando los pesos gaussianos
            r = max(0, min(255, int(round(sum(v * p for v, p in zip(vecindad_r, mascara))))))
            g = max(0, min(255, int(round(sum(v * p for v, p in zip(vecindad_g, mascara))))))
            b = max(0, min(255, int(round(sum(v * p for v, p in zip(vecindad_b, mascara))))))

            # Guardamos el nuevo píxel RGB en la imagen resultado
            resultado.putpixel((x, y), (r, g, b))

    return resultado


def aplicar_realce_bordes(img_pil, tamano_mascara=3):

    img_pil = img_pil.convert("RGB")        # Convertimos la imagen a RGB
    ancho, alto = img_pil.size              # Obtenemos el ancho y alto de la imagen
    radio_mascara = tamano_mascara // 2     # Calculamos el radio de la máscara

    resultado = Image.new("RGB", (ancho, alto))  # Creamos la imagen resultado

    cantidad_celdas = tamano_mascara * tamano_mascara   # Calculamos la cantidad total de posiciones de la máscara

    peso_centro = (cantidad_celdas - 1) / cantidad_celdas   # Peso que tendrá el píxel central
    peso_resto = -1 / cantidad_celdas   # Peso que tendrán todos los demás píxeles

    mascara = []

    # Recorremos todas las posiciones de la máscara
    for dy in range(-radio_mascara, radio_mascara + 1):
        for dx in range(-radio_mascara, radio_mascara + 1):

            # Si estamos en el centro usamos el peso central
            if dx == 0 and dy == 0:
                mascara.append(peso_centro)

            # Para el resto de las posiciones usamos el peso negativo
            else:
                mascara.append(peso_resto)

    # Recorremos todos los píxeles de la imagen
    for y in range(alto):
        for x in range(ancho):

            # Obtenemos los valores de RGB de la ventana
            vecindad_r, vecindad_g, vecindad_b = obtener_ventana(img_pil, x, y, radio_mascara)

            # Aplicamos la máscara a cada canal
            r = max(0, min(255,int(round(sum(v*m for v,m in zip(vecindad_r, mascara)))) + 128))
            g = max(0, min(255,int(round(sum(v*m for v,m in zip(vecindad_g, mascara)))) + 128))
            b = max(0, min(255,int(round(sum(v*m for v,m in zip(vecindad_b, mascara)))) + 128))

            # Guardamos el nuevo píxel RGB
            resultado.putpixel((x, y), (r, g, b))

    return resultado