import math
import sys

import pygame

# ============================================================
#  CONFIGURACIÓN
# ============================================================
ANCHO_VENTANA, ALTO_VENTANA = 900, 700
TAMANO_HEX = 40
FILAS = 25
COLUMNAS = 30
MARGEN_X = 80
MARGEN_Y = 80
FPS = 60
VELOCIDAD_CAMARA = 8

# Zoom
ZOOM_MIN = 0.3
ZOOM_MAX = 3.0
PASO_ZOOM = 1.1

# Colores
NEGRO       = (0, 0, 0)
BLANCO      = (255, 255, 255)
GRIS        = (90, 90, 90)
VERDE       = (40, 80, 40)
AMARILLO    = (255, 220, 0)

# ============================================================
#  GEOMETRÍA DE HEXÁGONOS (pointy-top, offset)
# ============================================================
ANCHO_HEX = math.sqrt(3) * TAMANO_HEX
ALTO_HEX  = 2 * TAMANO_HEX

def hex_a_pixel(fila, columna):
    """Centro del hexágono en coordenadas del MUNDO."""
    x = columna * ANCHO_HEX
    y = fila * (ALTO_HEX * 0.75)
    if fila % 2 == 1:
        x += ANCHO_HEX / 2
    return x + MARGEN_X, y + MARGEN_Y

def dibujar_hexagono(superficie, color, cx, cy, tamano, grosor=0):
    """Dibuja hexágono pointy-top centrado en (cx, cy), radio 'tamano'."""
    puntos = []
    for i in range(6):
        angulo = math.radians(60 * i - 90)
        x = cx + tamano * math.cos(angulo)
        y = cy + tamano * math.sin(angulo)
        puntos.append((x, y))
    pygame.draw.polygon(superficie, color, puntos, grosor)

def mundo_a_pantalla(mx, my, cam_x, cam_y, z):
    """Convierte coordenadas del mundo a coordenadas de pantalla."""
    return (mx - cam_x) * z, (my - cam_y) * z

def pantalla_a_mundo(px, py, cam_x, cam_y, z):
    """Convierte coordenadas de pantalla a coordenadas del mundo."""
    return px / z + cam_x, py / z + cam_y

def pixel_a_hex(px, py, cam_x, cam_y, z):
    """Coordenadas de pantalla -> (fila, col) del hexágono, o None."""
    mx, my = pantalla_a_mundo(px, py, cam_x, cam_y, z)

    fila_aprox = int((my - MARGEN_Y) / (ALTO_HEX * 0.75))
    col_aprox  = int((mx - MARGEN_X) / ANCHO_HEX)

    for fila in range(fila_aprox - 2, fila_aprox + 3):
        for col in range(col_aprox - 2, col_aprox + 3):
            if 0 <= fila < FILAS and 0 <= col < COLUMNAS:
                cx, cy = hex_a_pixel(fila, col)
                if math.hypot(mx - cx, my - cy) <= TAMANO_HEX:
                    return fila, col
    return None

def tamano_mundo():
    """Ancho y alto totales del mapa en píxeles del mundo."""
    ancho = MARGEN_X * 2 + COLUMNAS * ANCHO_HEX
    alto  = MARGEN_Y * 2 + (FILAS - 1) * ALTO_HEX * 0.75 + ALTO_HEX
    return ancho, alto

# ============================================================
#  CÁMARA
# ============================================================
def limitar_camara(cx, cy, z):
    """Evita que la cámara se salga del mundo (teniendo en cuenta el zoom)."""
    mundo_visible_ancho = ANCHO_VENTANA / z
    mundo_visible_alto  = ALTO_VENTANA / z
    max_x = max(0, MUNDO_ANCHO - mundo_visible_ancho)
    max_y = max(0, MUNDO_ALTO  - mundo_visible_alto)
    return max(0, min(cx, max_x)), max(0, min(cy, max_y))

def zoom_anclado(cam_x, cam_y, z_viejo, z_nuevo, punto_pantalla):
    """Recalcula la cámara para que el punto de pantalla no se mueva al cambiar el zoom."""
    mx, my = punto_pantalla
    mundo_x = mx / z_viejo + cam_x
    mundo_y = my / z_viejo + cam_y
    return (mundo_x - mx / z_nuevo,
            mundo_y - my / z_nuevo)

# ============================================================
#  INICIALIZACIÓN
# ============================================================
pygame.init()
pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Juego de Hexágonos — cámara + zoom")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont("consolas", 16)

MUNDO_ANCHO, MUNDO_ALTO = tamano_mundo()

camara_x, camara_y = 0.0, 0.0
zoom = 1.0

# ============================================================
#  BUCLE PRINCIPAL
# ============================================================
ejecutando = True
hex_bajo_raton = None

while ejecutando:
    # --- Eventos ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                ejecutando = False
            elif evento.key == pygame.K_r:      # reset de cámara y zoom
                camara_x, camara_y = 0.0, 0.0
                zoom = 1.0

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if hex_bajo_raton is not None:
                print(f"Clic en hex: fila={hex_bajo_raton[0]}, col={hex_bajo_raton[1]}")

        elif evento.type == pygame.MOUSEWHEEL:
            if evento.y > 0:
                nuevo_zoom = zoom * PASO_ZOOM
            else:
                nuevo_zoom = zoom / PASO_ZOOM

            nuevo_zoom = max(ZOOM_MIN, min(nuevo_zoom, ZOOM_MAX))

            if nuevo_zoom != zoom:
                camara_x, camara_y = zoom_anclado(
                    camara_x, camara_y, zoom, nuevo_zoom,
                    pygame.mouse.get_pos()
                )
                zoom = nuevo_zoom
                camara_x, camara_y = limitar_camara(camara_x, camara_y, zoom)

    # --- Movimiento de la cámara (teclado) ---
    teclas = pygame.key.get_pressed()
    dx = dy = 0
    if teclas[pygame.K_LEFT]  or teclas[pygame.K_a]: dx -= VELOCIDAD_CAMARA / zoom
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: dx += VELOCIDAD_CAMARA / zoom
    if teclas[pygame.K_UP]    or teclas[pygame.K_w]: dy -= VELOCIDAD_CAMARA / zoom
    if teclas[pygame.K_DOWN]  or teclas[pygame.K_s]: dy += VELOCIDAD_CAMARA / zoom

    camara_x, camara_y = limitar_camara(camara_x + dx, camara_y + dy, zoom)

    # --- Ratón -> hex ---
    raton_x, raton_y = pygame.mouse.get_pos()
    hex_bajo_raton = pixel_a_hex(raton_x, raton_y, camara_x, camara_y, zoom)

    # --- Dibujo ---
    pantalla.fill(NEGRO)

    tamano_pant = TAMANO_HEX * zoom

    # 1) Hexágonos visibles
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            cx_mundo, cy_mundo = hex_a_pixel(fila, col)
            cx_pant, cy_pant = mundo_a_pantalla(cx_mundo, cy_mundo, camara_x, camara_y, zoom)

            # Culling
            if (cx_pant < -tamano_pant * 2 or cx_pant > ANCHO_VENTANA + tamano_pant * 2 or
                cy_pant < -tamano_pant * 2 or cy_pant > ALTO_VENTANA + tamano_pant * 2):
                continue

            dibujar_hexagono(pantalla, VERDE, cx_pant, cy_pant, tamano_pant)
            dibujar_hexagono(pantalla, GRIS,  cx_pant, cy_pant, tamano_pant, 2)

    # 2) Resaltado bajo el ratón
    if hex_bajo_raton is not None:
        cx_mundo, cy_mundo = hex_a_pixel(*hex_bajo_raton)
        cx_pant, cy_pant = mundo_a_pantalla(cx_mundo, cy_mundo, camara_x, camara_y, zoom)
        dibujar_hexagono(pantalla, AMARILLO, cx_pant, cy_pant, tamano_pant, 3)

    # 3) HUD
    if hex_bajo_raton is not None:
        texto = f"Hex: fila={hex_bajo_raton[0]} col={hex_bajo_raton[1]}"
    else:
        texto = "Hex: (fuera del mapa)"
    texto += f"   |   Cam: ({int(camara_x)}, {int(camara_y)})"
    texto += f"   |   Zoom: {zoom:.2f}"
    texto += "   |   Flechas/WASD: mover · Rueda: zoom · R: reset"
    pantalla.blit(fuente.render(texto, True, BLANCO), (10, 10))

    pygame.display.flip()
    reloj.tick(FPS)

# ============================================================
#  SALIDA
# ============================================================
pygame.quit()
sys.exit()