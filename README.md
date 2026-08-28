# TP1: Operadores Puntuales y Operadores en el Dominio Espacial

**Materia:** Procesamiento de Imágenes y Visión por Computadora  
**Universidad:** Universidad Nacional de Hurlingham  
**Profesora:** Dra. Juliana Gambini  
**Estudiantes:** Ernestina Campos Llanos, Rocio Rodriguez
---

## Descripción del Trabajo Práctico

Este proyecto contiene la implementación en Python de algoritmos de procesamiento digital de imágenes (operadores puntuales, histogramas, generadores de ruido aleatorio y filtros espaciales) con una interfaz gráfica basada en Tkinter.

---

## Estructura del Repositorio (Organigrama)

```text
TP1-Procesamiento-De-Imagenes/
│
├── main.py                  # Punto de entrada principal de la aplicación
├── appProcesamiento.py      # Clase principal de la interfaz gráfica (Controles y Canvas)
├── ventana_resultado.py     # Ventana emergente secundaria para mostrar resultados y gráficos
├── procesamiento.py         # Algoritmos de procesamiento de imágenes (Filtros, Ruidos, Histograma)
├── generadores.py           # Funciones para generación de ruido (Gaussiano y Exponencial)
└── README.md                # Documentación del proyecto
```

---

## Descripción de Módulos

* **`main.py`**: Archivo ejecutable que arranca el bucle principal (`mainloop`) de Tkinter.
* **`appProcesamiento.py`**: Define la clase `AppProcesamiento` con los botones de control, la lógica de carga de archivos (formatos estándar y RAW) y la selección de regiones con mouse.
* **`ventana_resultado.py`**: Define la clase `VentanaResultado` encargada de abrir ventanas auxiliares para guardar imágenes y realizar comparaciones de histogramas con Matplotlib.
* **`procesamiento.py`**: Implementación de algoritmos matemáticos:
  * Operadores de potencia, negativo y umbralización.
  * Cálculo y ecualización de histograma.
  * Inyección de ruido (Gaussiano, Exponencial y Sal y Pimienta).
  * Filtros espaciales (Media, Mediana, Mediana Ponderada, Gaussiano y Realce de bordes).
* **`generadores.py`**: Implementación de las funciones para generar variables aleatorias gaussianas y exponenciales.

---

## Requisitos e Instalación

2. Instalar las dependencias necesarias:
   ```bash
   pip install pillow matplotlib
   ```

## Ejecución

Para iniciar la aplicación, ejecutá desde la terminal:
```bash
python main.py
```