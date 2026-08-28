import random

def generador_gaussiano(mu, sigma, cantidad):
    return [random.gauss(mu, sigma) for _ in range(cantidad)]

def generador_exponencial(lambd, cantidad):
    return [random.expovariate(lambd) for _ in range(cantidad)]