import random
import math

def generador_gaussiano(mu, sigma, cantidad):
    resultado = []
    
    while len(resultado) < cantidad:
        # tomamos dos numeros al azar entre 0 y 1
        x1 = random.random()
        x2 = random.random()

        z = math.sqrt(-2 * math.log(x1)) * math.cos(2 * math.pi * x2)
        
        # "z" tiene media 0 y desvío 1 (gaussiana estándar)
        # lo reescalamos para que tenga la media (mu) y desvío (sigma) que se pidió
        valor = mu + sigma * z
        
        resultado.append(valor)
    
    return resultado


def generador_exponencial(lambd, cantidad):
    resultado = []
    for _ in range(cantidad):
        x = random.random()  # x ~ U(0,1)
        y = -math.log(x) / lambd
        resultado.append(y)
    return resultado