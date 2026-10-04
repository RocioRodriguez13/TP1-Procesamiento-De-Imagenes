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


def aplicar_mediana_ponderada_5x5(img_pil):

    img_pil = img_pil.convert("RGB")        # Convertimos la imagen a RGB
    ancho, alto = img_pil.size              # Obtenemos el ancho y el alto
    radio_mascara = 2                       # Para una máscara 5x5 el radio es 2
    resultado = Image.new("RGB", (ancho, alto)) # Creamos una nueva imagen del mismo tamaño para guardar el resultado

    # Definimos los pesos de la máscara 5x5.
    mascara = [1, 2, 3, 2, 1,
                2, 3, 5, 3, 2,
                3, 5, 9, 5, 3,
                2, 3, 5, 3, 2,
                1, 2, 3, 2, 1]

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


def aplicar_bordes_prewitt(img_pil):
    img_pil = img_pil.convert("RGB")  # Conevrtimos a RGB
    ancho, alto = img_pil.size  # Obtenemos el tamaño de la imagen
    resultado = Image.new("RGB", (ancho, alto))  # Imagen nueva y vacía donde vamos a guardar el resultado

    # Máscara horizontal (bordes verticales)
    mascara_x = [
        -1, 0, 1,
        -1, 0, 1,
        -1, 0, 1]

    # Máscara vertical (bordes horizontales)
    mascara_y = [
        -1, -1, -1,
        0,  0,  0,
        1,  1,  1]

    for y in range(alto):        # Recorremos todas las filas de la imagen
        for x in range(ancho):   # Recorremos todas las columnas de la imagen
            
            vecindad_r, vecindad_g, vecindad_b = obtener_ventana(img_pil, x, y, 1) # Obtenemos ventana de 3x3 de vecinos

            # Aplicamos las máscaras sobre el canal rojo
            gx_r = sum(v * m for v, m in zip(vecindad_r, mascara_x))  # Gradiente horizontal del rojo
            gy_r = sum(v * m for v, m in zip(vecindad_r, mascara_y))  # Gradiente vertical del rojo

            # Aplicamos las máscaras sobre el canal verde
            gx_g = sum(v * m for v, m in zip(vecindad_g, mascara_x))  # Gradiente horizontal del verde
            gy_g = sum(v * m for v, m in zip(vecindad_g, mascara_y))  # Gradiente vertical del verde

            # Aplicamos las máscaras sobre el canal azul
            gx_b = sum(v * m for v, m in zip(vecindad_b, mascara_x))  # Gradiente horizontal del azul
            gy_b = sum(v * m for v, m in zip(vecindad_b, mascara_y))  # Gradiente vertical del azul

            # Combinamos gx y gy para obtener la magnitud total del borde, sin importar su dirección
            r = int(min(255, math.sqrt(gx_r**2 + gy_r**2)))  # Magnitud del borde en rojo
            g = int(min(255, math.sqrt(gx_g**2 + gy_g**2)))  # Magnitud del borde en verde
            b = int(min(255, math.sqrt(gx_b**2 + gy_b**2)))  # Magnitud del borde en azul

            resultado.putpixel((x, y), (r, g, b))  # Escribimos el píxel resultado

    return resultado


def aplicar_bordes_sobel(img_pil):
    img_pil = img_pil.convert("RGB")  # Conevrtimos a RGB
    ancho, alto = img_pil.size  # Obtenemos el tamaño de la imagen
    resultado = Image.new("RGB", (ancho, alto))  # Imagen nueva y vacía donde vamos a guardar el resultado

    # Máscara horizontal (bordes verticales)
    mascara_x = [
        -1, 0, 1,
        -2, 0, 2,
        -1, 0, 1]

    # Máscara vertical (bordes horizontales)
    mascara_y = [
        -1, -2, -1,
        0,  0,  0,
        1,  2,  1]

    for y in range(alto):        # Recorremos todas las filas de la imagen
        for x in range(ancho):   # Recorremos todas las columnas de la imagen

            vecindad_r, vecindad_g, vecindad_b = obtener_ventana(img_pil, x, y, 1) # Obtenemos ventana de 3x3 de vecinos

            # Aplicamos las máscaras sobre el canal rojo
            gx_r = sum(v * m for v, m in zip(vecindad_r, mascara_x))  # Gradiente horizontal del rojo
            gy_r = sum(v * m for v, m in zip(vecindad_r, mascara_y))  # Gradiente vertical del rojo

            # Aplicamos las máscaras sobre el canal verde
            gx_g = sum(v * m for v, m in zip(vecindad_g, mascara_x))  # Gradiente horizontal del verde
            gy_g = sum(v * m for v, m in zip(vecindad_g, mascara_y))  # Gradiente vertical del verde

            # Aplicamos las máscaras sobre el canal azul
            gx_b = sum(v * m for v, m in zip(vecindad_b, mascara_x))  # Gradiente horizontal del azul
            gy_b = sum(v * m for v, m in zip(vecindad_b, mascara_y))  # Gradiente vertical del azul

            # Combinamos gx y gypara obtener la magnitud total del borde
            r = int(min(255, math.sqrt(gx_r**2 + gy_r**2)))  # Magnitud del borde en rojo
            g = int(min(255, math.sqrt(gx_g**2 + gy_g**2)))  # Magnitud del borde en verde
            b = int(min(255, math.sqrt(gx_b**2 + gy_b**2)))  # Magnitud del borde en azul

            resultado.putpixel((x, y), (r, g, b))

    return resultado


def aplicar_bordes_laplaciano(img_pil):
    img_pil = img_pil.convert("RGB")                # Conevrtimos a RGB
    ancho, alto = img_pil.size                      # Obtenemos el tamaño de la imagen
    resultado = Image.new("RGB", (ancho, alto))     # Imagen nueva y vacía donde vamos a guardar el resultado

    # Máscara del Laplaciano
    mascara = [
        0, -1,  0,
        -1,  4, -1,
        0, -1,  0]

    for y in range(alto):        # Recorremos todas las filas de la imagen
        for x in range(ancho):   # Recorremos todas las columnas de la imagen

            vecindad_r, vecindad_g, vecindad_b = obtener_ventana(img_pil, x, y, 1) # Obtenemos ventana de 3x3 de vecinos

            # Aplicamos el Laplaciano a cada canal
            lap_r = sum(v * m for v, m in zip(vecindad_r, mascara))
            lap_g = sum(v * m for v, m in zip(vecindad_g, mascara))
            lap_b = sum(v * m for v, m in zip(vecindad_b, mascara))

            # Tomamos el valor absoluto (0=sin cambio, más alto=más borde)
            r = max(0, min(255, abs(lap_r)))
            g = max(0, min(255, abs(lap_g)))
            b = max(0, min(255, abs(lap_b)))

            # Guardamos el resultado
            resultado.putpixel((x, y), (r, g, b))

    return resultado 


def aplicar_bordes_laplaciano_pendiente(img_pil, umbral_borde=100):
    img_pil = img_pil.convert("RGB")  # Convertimos a RGB
    ancho, alto = img_pil.size  # Obtenemos el tamaño de la imagen

    # Máscara del Laplaciano
    mascara = [
        0, -1,  0,
        -1,  4, -1,
        0, -1,  0]

    # Dos matrices del mismo tamaño que la imagen: una para guardar la respuesta del Laplaciano de cada píxel,
    # otra para guardar su intensidad de gris original.
    # Las necesitamos calculadas de antemano, porque vamos a comparar cada píxel con sus vecinos,
    # y no podemos hacerlo si solo tenemos un píxel a la vez.
    laplaciano = [[0] * ancho for y in range(alto)]
    gris = [[0] * ancho for y in range(alto)]  # guardamos también la intensidad original

    # PRIMERA PASADA: calculamos el Laplaciano y la intensidad de gris de cada píxel
    for y in range(alto):
        for x in range(ancho):
            r, g, b = obtener_ventana(img_pil, x, y, 1)  # Ventana 3x3 de vecinos
            vecindad = [(r[i] + g[i] + b[i]) / 3 for i in range(9)]  # Convertimos cada vecino a gris (promedio RGB)
            valor = sum(v * m for v, m in zip(vecindad, mascara))  # Aplicamos la máscara del Laplaciano sobre el gris
            laplaciano[y][x] = valor  # Guardamos la respuesta del Laplaciano para este píxel
            gris[y][x] = vecindad[4]  # el valor del centro de la ventana (el propio píxel)

    resultado = Image.new("RGB", (ancho, alto))  # Imagen final donde vamos a marcar los bordes

    # SEGUNDA PASADA: para cada píxel, buscamos si hay un cruce por cero con algún vecino
    for y in range(alto):
        for x in range(ancho):
            centro = laplaciano[y][x]  # Respuesta del Laplaciano en este píxel
            hay_borde = False  # Todavía no encontramos ningún cruce por cero válido

            # Revisamos los 4 vecinos directos (arriba, abajo, izquierda, derecha)
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                xi = x + dx
                yi = y + dy
                if 0 <= xi < ancho and 0 <= yi < alto:  # No salirnos de la imagen
                    vecino = laplaciano[yi][xi]  # Respuesta del Laplaciano en el vecino
                    if centro * vecino < 0:  # Si tienen signo distinto, hay un cruce por cero acá
                        # Pendiente sobre la intensidad original, no sobre el Laplaciano
                        pendiente = abs(gris[y][x] - gris[yi][xi])  # Diferencia de intensidad entre ambos píxeles
                        if pendiente > umbral_borde:  # Si el salto de intensidad es suficientemente fuerte
                            hay_borde = True  # lo marcamos como borde
                            break  # No hace falta seguir revisando los demás vecinos

            # Pintamos el píxel: blanco si es borde, negro si no
            if hay_borde:
                resultado.putpixel((x, y), (255, 255, 255))
            else:
                resultado.putpixel((x, y), (0, 0, 0))

    return resultado


def aplicar_marr_hildreth(img_pil, sigma):

    img_pil = img_pil.convert("RGB")  # Convertimos a RGB
    ancho, alto = img_pil.size  # Obtenemos el tamaño de la imagen

    # Tamaño de la máscara: n = 4σ + 1
    n = int(4 * sigma + 1)

    # Si el tamaño resulta par, lo hacemos impar
    if n % 2 == 0:
        n += 1
    radio = n // 2  # Radio de la ventana a partir del tamaño total

    # Construimos la máscara LoG (Laplaciano de la Gaussiana)
    mascara = []

    for y in range(-radio, radio + 1):        # Recorremos cada posición vertical dentro de la ventana
        for x in range(-radio, radio + 1):    # Recorremos cada posición horizontal dentro de la ventana

            distancia = x*x + y*y  # Distancia al cuadrado desde el centro

            # Fórmula de la segunda derivada de la Gaussiana
            valor = (
                1 / (2 * math.pi * sigma**3)
                * math.exp(-distancia / (2 * sigma**2))
                * (distancia / sigma**2 - 2))

            mascara.append(valor)  # Guardamos el peso calculado para esta posición de la máscara

    # Matriz del mismo tamaño que la imagen, donde vamos a guardar la respuesta del filtro LoG para cada píxel
    valores_log = [[0.0] * ancho for _ in range(alto)]

    # PRIMERA PASADA: aplicamos la máscara LoG sobre toda la imagen
    for y in range(alto):
        for x in range(ancho):

            # Ventana de vecinos del tamaño de la máscara LoG
            vecindad_r, vecindad_g, vecindad_b = obtener_ventana(img_pil, x, y, radio)

            # Convertimos cada vecino a gris
            vecindad_gris = [
                (r + g + b) / 3
                for r, g, b in zip(vecindad_r, vecindad_g, vecindad_b)]

            # Aplicamos la máscara
            valor = sum(v * m for v, m in zip(vecindad_gris, mascara))

            valores_log[y][x] = valor  # Guardamos la respuesta del LoG para este píxel

    # Imagen final donde vamos a marcar los bordes detectados
    resultado = Image.new("RGB", (ancho, alto))

    # SEGUNDA PASADA: buscamos cruces por cero comparando cada píxel con sus vecinos
    for y in range(alto):
        for x in range(ancho):

            centro = valores_log[y][x]  # Respuesta del LoG en el píxel actual
            hay_borde = False  # Todavía no encontramos ningún cruce por cero

            # Revisamos los 4 vecinos directos (arriba, abajo, izquierda, derecha)
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:

                # No salrinos de la imagen en los bordes
                xi = min(max(x + dx, 0), ancho - 1)
                yi = min(max(y + dy, 0), alto - 1)

                vecino = valores_log[yi][xi]  # Respuesta del LoG en ese vecino

                # Cruce por cero: si el centro y el vecino tienen signos opuestos, hay un borde
                if (centro < 0 and vecino > 0) or (centro > 0 and vecino < 0):
                    hay_borde = True
                    break

            # Pintamos el píxel: blanco si es borde, negro si no
            if hay_borde:
                resultado.putpixel((x, y), (255, 255, 255))
            else:
                resultado.putpixel((x, y), (0, 0, 0))

    return resultado


def difusion_isotropica_canal(matriz, ancho, alto, iteraciones, lambd):

    for it in range(iteraciones):   # Repetimos el proceso la cantidad de iteraciones pedida
        nueva = []  # Matriz donde guardamos el resultado de esta iteración
        for i in range(alto):
            fila = [0] * ancho
            nueva.append(fila)

        for y in range(alto):
            for x in range(ancho):
                centro = matriz[y][x]

                # Buscamos los 4 vecinos (norte, sur, este, oeste). Si estamos en el borde, repetimos el centro.
                if y - 1 >= 0:
                    norte = matriz[y - 1][x]
                else:
                    norte = centro

                if y + 1 <= alto - 1:
                    sur = matriz[y + 1][x]
                else:
                    sur = centro

                if x + 1 <= ancho - 1:
                    este = matriz[y][x + 1]
                else:
                    este = centro

                if x - 1 >= 0:
                    oeste = matriz[y][x - 1]
                else:
                    oeste = centro

                # Sumamos las diferencias de cada vecino contra el centro (los gradientes)
                sumaGradientes = (norte - centro) + (sur - centro) + (este - centro) + (oeste - centro)

                nuevoValor = centro + lambd * sumaGradientes   # Actualizamos el valor del pixel

                # Nos aseguramos de que quede entre 0 y 255
                if nuevoValor < 0:
                    nuevoValor = 0
                if nuevoValor > 255:
                    nuevoValor = 255

                nueva[y][x] = nuevoValor

        matriz = nueva  

    return matriz


def aplicar_difusion_isotropica(imgPil, iteraciones=10, lambd=0.15):
    imgPil = imgPil.convert("RGB")
    ancho, alto = imgPil.size

    # Creamos una matriz por cada canal con los valores originales de la imagen
    matrizR = []
    matrizG = []
    matrizB = []
    for i in range(alto):
        matrizR.append([0] * ancho)
        matrizG.append([0] * ancho)
        matrizB.append([0] * ancho)

    for y in range(alto):
        for x in range(ancho):
            r, g, b = imgPil.getpixel((x, y))
            matrizR[y][x] = r
            matrizG[y][x] = g
            matrizB[y][x] = b

    # Aplicamos la difusión isotrópica a cada canal por separado
    matrizR = difusion_isotropica_canal(matrizR, ancho, alto, iteraciones, lambd)
    matrizG = difusion_isotropica_canal(matrizG, ancho, alto, iteraciones, lambd)
    matrizB = difusion_isotropica_canal(matrizB, ancho, alto, iteraciones, lambd)

    resultado = Image.new("RGB", (ancho, alto))
    for y in range(alto):
        for x in range(ancho):
            resultado.putpixel((x, y), (int(matrizR[y][x]), int(matrizG[y][x]), int(matrizB[y][x])))

    return resultado


def coeficiente_difusion(gradiente, k):
    return math.exp(-((gradiente / k) ** 2))


def difusion_anisotropica_canal(matriz, ancho, alto, iteraciones, lambd, k):

    for it in range(iteraciones):
        nueva = []
        for i in range(alto):
            fila = [0] * ancho
            nueva.append(fila)

        for y in range(alto):
            for x in range(ancho):
                centro = matriz[y][x]

                if y - 1 >= 0:
                    norte = matriz[y - 1][x]
                else:
                    norte = centro

                if y + 1 <= alto - 1:
                    sur = matriz[y + 1][x]
                else:
                    sur = centro

                if x + 1 <= ancho - 1:
                    este = matriz[y][x + 1]
                else:
                    este = centro

                if x - 1 >= 0:
                    oeste = matriz[y][x - 1]
                else:
                    oeste = centro

                gradN = norte - centro
                gradS = sur - centro
                gradE = este - centro
                gradO = oeste - centro

                
                cN = coeficiente_difusion(gradN, k)
                cS = coeficiente_difusion(gradS, k)
                cE = coeficiente_difusion(gradE, k)
                cO = coeficiente_difusion(gradO, k)

                nuevoValor = centro + lambd * (cN * gradN + cS * gradS + cE * gradE + cO * gradO)

                if nuevoValor < 0:
                    nuevoValor = 0
                if nuevoValor > 255:
                    nuevoValor = 255

                nueva[y][x] = nuevoValor

        matriz = nueva

    return matriz


def aplicar_difusion_anisotropica(imgPil, iteraciones=10, lambd=0.15, k=15):
    imgPil = imgPil.convert("RGB")
    ancho, alto = imgPil.size

    matrizR = []
    matrizG = []
    matrizB = []
    for i in range(alto):
        matrizR.append([0] * ancho)
        matrizG.append([0] * ancho)
        matrizB.append([0] * ancho)

    for y in range(alto):
        for x in range(ancho):
            r, g, b = imgPil.getpixel((x, y))
            matrizR[y][x] = r
            matrizG[y][x] = g
            matrizB[y][x] = b

    matrizR = difusion_anisotropica_canal(matrizR, ancho, alto, iteraciones, lambd, k)
    matrizG = difusion_anisotropica_canal(matrizG, ancho, alto, iteraciones, lambd, k)
    matrizB = difusion_anisotropica_canal(matrizB, ancho, alto, iteraciones, lambd, k)

    resultado = Image.new("RGB", (ancho, alto))
    for y in range(alto):
        for x in range(ancho):
            resultado.putpixel((x, y), (int(matrizR[y][x]), int(matrizG[y][x]), int(matrizB[y][x])))

    return resultado




def aplicar_filtro_bilateral(imgPil, sigmaS=3, sigmaR=30, tamanoMascara=7):
    imgPil = imgPil.convert("RGB")
    ancho, alto = imgPil.size
    radioMascara = tamanoMascara // 2
    resultado = Image.new("RGB", (ancho, alto))

    for y in range(alto):           # Recorremos todas las filas
        for x in range(ancho):      # Recorremos todas las columnas

            r0, g0, b0 = imgPil.getpixel((x, y))   # Valor del pixel central

            sumaR = 0.0
            sumaG = 0.0
            sumaB = 0.0
            # Acumuladores del numerador (pesos * valor)

            pesoTotalR = 0.0
            pesoTotalG = 0.0
            pesoTotalB = 0.0

            for dy in range(-radioMascara, radioMascara + 1):
                for dx in range(-radioMascara, radioMascara + 1):

                    xi = x + dx
                    yi = y + dy
                    if xi < 0:
                        xi = 0
                    if xi > ancho - 1:
                        xi = ancho - 1
                    if yi < 0:
                        yi = 0
                    if yi > alto - 1:
                        yi = alto - 1

                    ri, gi, bi = imgPil.getpixel((xi, yi))

                    pesoEspacial = math.exp(-((dx ** 2 + dy ** 2) / (2 * sigmaS ** 2)))

                    pesoR = pesoEspacial * math.exp(-(((ri - r0) ** 2) / (2 * sigmaR ** 2)))
                    pesoG = pesoEspacial * math.exp(-(((gi - g0) ** 2) / (2 * sigmaR ** 2)))
                    pesoB = pesoEspacial * math.exp(-(((bi - b0) ** 2) / (2 * sigmaR ** 2)))

                    sumaR = sumaR + ri * pesoR
                    sumaG = sumaG + gi * pesoG
                    sumaB = sumaB + bi * pesoB

                    pesoTotalR = pesoTotalR + pesoR
                    pesoTotalG = pesoTotalG + pesoG
                    pesoTotalB = pesoTotalB + pesoB

            # Dividimos por la suma de los pesos (Wx) para normalizar
            r = int(sumaR / pesoTotalR)
            g = int(sumaG / pesoTotalG)
            b = int(sumaB / pesoTotalB)

            resultado.putpixel((x, y), (r, g, b))

    return resultado



def convertir_a_gris(imgPil):
    imgPil = imgPil.convert("RGB")
    ancho, alto = imgPil.size
    gris = []
    for i in range(alto):
        fila = [0] * ancho
        gris.append(fila)

    for y in range(alto):
        for x in range(ancho):
            r, g, b = imgPil.getpixel((x, y))
            gris[y][x] = int((r + g + b) / 3)

    return gris, ancho, alto


def umbral_optimo_iterativo(imgPil, deltaT=0.5):
    gris, ancho, alto = convertir_a_gris(imgPil)

    #umbral inicial, tomamos el promedio de toda la imagen
    sumaTotal = 0
    for y in range(alto):
        for x in range(ancho):
            sumaTotal = sumaTotal + gris[y][x]

    T = sumaTotal / (ancho * alto)

    while True:
        sumaG1 = 0
        cantidadG1 = 0
        sumaG2 = 0
        cantidadG2 = 0

        #separamos los pixels en dos grupos según el umbral T
        for y in range(alto):
            for x in range(ancho):
                valor = gris[y][x]
                if valor > T:
                    sumaG2 = sumaG2 + valor
                    cantidadG2 = cantidadG2 + 1
                else:
                    sumaG1 = sumaG1 + valor
                    cantidadG1 = cantidadG1 + 1

        #calculamos la media de cada grupo
        if cantidadG1 > 0:
            m1 = sumaG1 / cantidadG1
        else:
            m1 = 0

        if cantidadG2 > 0:
            m2 = sumaG2 / cantidadG2
        else:
            m2 = 0

        #calculamos el nuevo umbral
        nuevoT = (m1 + m2) / 2

        #repetimos hasta que el umbral deje de cambiar significativamente
        diferencia = nuevoT - T
        if diferencia < 0:
            diferencia = -diferencia

        if diferencia < deltaT:
            T = nuevoT
            break

        T = nuevoT

    return T


def aplicar_umbral(imgPil, umbral):
    gris, ancho, alto = convertir_a_gris(imgPil)
    resultado = Image.new("RGB", (ancho, alto))

    for y in range(alto):
        for x in range(ancho):
            if gris[y][x] > umbral:
                resultado.putpixel((x, y), (255, 255, 255))
            else:
                resultado.putpixel((x, y), (0, 0, 0))

    return resultado


def metodo_otsu(imgPil):
    gris, ancho, alto = convertir_a_gris(imgPil)
    totalPixeles = ancho * alto

    histograma = [0] * 256
    for y in range(alto):
        for x in range(ancho):
            histograma[gris[y][x]] = histograma[gris[y][x]] + 1

    p = []
    for i in range(256):
        p.append(histograma[i] / totalPixeles)

    #suma acumulada P1(t)
    P1 = [0.0] * 256
    acumulado = 0.0
    for i in range(256):
        acumulado = acumulado + p[i]
        P1[i] = acumulado

    #promedio ponderado acumulado m(t)
    m = [0.0] * 256
    acumuladoM = 0.0
    for i in range(256):
        acumuladoM = acumuladoM + i * p[i]
        m[i] = acumuladoM

    #El promedio ponderado global es el último valor de m
    mG = m[255]

    #varianza entre clases para cada posible umbral t
    varianzaEntreClases = [0.0] * 256
    for t in range(256):
        denominador = P1[t] * (1 - P1[t])
        if denominador == 0:
            varianzaEntreClases[t] = 0
        else:
            varianzaEntreClases[t] = ((mG * P1[t] - m[t]) ** 2) / denominador

    # el umbral óptimo es el que maximiza esa varianza
    umbralOptimo = 0
    mayorVarianza = varianzaEntreClases[0]
    for t in range(1, 256):
        if varianzaEntreClases[t] > mayorVarianza:
            mayorVarianza = varianzaEntreClases[t]
            umbralOptimo = t

    return umbralOptimo


def obtener_canal(imgPil, canal):
    ancho, alto = imgPil.size
    imagenCanal = Image.new("RGB", (ancho, alto))

    for y in range(alto):
        for x in range(ancho):
            pixel = imgPil.getpixel((x, y))
            valor = pixel[canal]
            imagenCanal.putpixel((x, y), (valor, valor, valor))

    return imagenCanal


def segmentacion_color_por_bandas(imgPil):
    imgPil = imgPil.convert("RGB")
    ancho, alto = imgPil.size

    # Separamos la imagen en sus tres bandas
    imagenR = obtener_canal(imgPil, 0)
    imagenG = obtener_canal(imgPil, 1)
    imagenB = obtener_canal(imgPil, 2)

    # Calculamos el umbral óptimo de Otsu para cada banda por separado
    umbralR = metodo_otsu(imagenR)
    umbralG = metodo_otsu(imagenG)
    umbralB = metodo_otsu(imagenB)

    resultado = Image.new("RGB", (ancho, alto))

    for y in range(alto):
        for x in range(ancho):
            r, g, b = imgPil.getpixel((x, y))

            # Umbralizamos cada banda: si supera su propio umbral, queda en 255, sino en 0
            if r > umbralR:
                rBin = 255
            else:
                rBin = 0

            if g > umbralG:
                gBin = 255
            else:
                gBin = 0

            if b > umbralB:
                bBin = 255
            else:
                bBin = 0

            resultado.putpixel((x, y), (rBin, gBin, bBin))

    return resultado