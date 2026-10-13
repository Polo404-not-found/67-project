import pygame
import sys
import math

ANCHO_VENTANA, ALTO_VENTANA = 1280, 720
TAMANO_HEX = 40      
FILAS = 10
COLUMNAS = 12
MARGEN_X = 80       
MARGEN_Y = 80
FPS = 60

NEGRO       = (0, 0, 0)
BLANCO      = (255, 255, 255)
GRIS        = (90, 90, 90)
VERDE       = (40, 80, 40)
AMARILLO    = (255, 220, 0)

ANCHO_HEX = math.sqrt(3) * TAMANO_HEX  
ALTO_HEX  = 2 * TAMANO_HEX            

def hex_a_pixel(fila, columna):
    """Devuelve el centro (x, y) en píxeles de un hexágono (fila, columna)."""
    x = columna * ANCHO_HEX
    y = fila * (ALTO_HEX * 0.75)
    if fila % 2 == 1:              
        x += ANCHO_HEX / 2
    return x + MARGEN_X, y + MARGEN_Y

def dibujar_hexagono(superficie, color, cx, cy, grosor=0):
    """Dibuja un hexágono 'pointy-top' centrado en (cx, cy)."""
    puntos = []
    for i in range(6):
        angulo = math.radians(60 * i - 90)
        x = cx + TAMANO_HEX * math.cos(angulo)
        y = cy + TAMANO_HEX * math.sin(angulo)
        puntos.append((x, y))
    pygame.draw.polygon(superficie, color, puntos, grosor)

def pixel_a_hex(px, py):
    """Convierte un punto en píxeles a coordenadas (fila, columna) de hexágono.
       Devuelve None si el punto no cae dentro del mapa."""
    px -= MARGEN_X
    py -= MARGEN_Y

    fila_aprox = int(py / (ALTO_HEX * 0.75))
    col_aprox  = int(px / ANCHO_HEX)

    for fila in range(fila_aprox - 2, fila_aprox + 3):
        for col in range(col_aprox - 2, col_aprox + 3):
            if 0 <= fila < FILAS and 0 <= col < COLUMNAS:
                cx, cy = hex_a_pixel(fila, col)
                if math.hypot(px + MARGEN_X - cx, py + MARGEN_Y - cy) <= TAMANO_HEX:
                    return fila, col
    return None

pygame.init()
pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Juego de Hexágonos")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont("consolas", 16)

ejecutando = True
hex_bajo_raton = None

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:  # noqa: SIM114
            ejecutando = False
        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            ejecutando = False
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:  # noqa: SIM102
            if hex_bajo_raton is not None:
                print(f"Has hecho clic en el hexágono: fila={hex_bajo_raton[0]}, columna={hex_bajo_raton[1]}")

    raton_x, raton_y = pygame.mouse.get_pos()
    hex_bajo_raton = pixel_a_hex(raton_x, raton_y)

    pantalla.fill(NEGRO)

    for fila in range(FILAS):
        for col in range(COLUMNAS):
            cx, cy = hex_a_pixel(fila, col)
            dibujar_hexagono(pantalla, VERDE, cx, cy)         
            dibujar_hexagono(pantalla, GRIS,  cx, cy, 2)       

    if hex_bajo_raton is not None:
        cx, cy = hex_a_pixel(*hex_bajo_raton)
        dibujar_hexagono(pantalla, AMARILLO, cx, cy, 3)

    if hex_bajo_raton is not None:
        texto = f"Hex: fila={hex_bajo_raton[0]}  col={hex_bajo_raton[1]}"
    else:
        texto = "Hex: (fuera del mapa)"
    superficie_texto = fuente.render(texto, True, BLANCO)
    pantalla.blit(superficie_texto, (10, 10))

    pygame.display.flip()
    reloj.tick(FPS)

pygame.quit()
sys.exit()