import pygame
import sys
import math

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
VELOCIDAD_CAMARA = 8         # píxeles por frame

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
    """Centro del hexágono en coordenadas del MUNDO (no de pantalla)."""
    x = columna * ANCHO_HEX
    y = fila * (ALTO_HEX * 0.75)
    if fila % 2 == 1:
        x += ANCHO_HEX / 2
    return x + MARGEN_X, y + MARGEN_Y

def dibujar_hexagono(superficie, color, cx, cy, grosor=0):
    """Dibuja hexágono pointy-top centrado en (cx, cy) — ya en coord. de PANTALLA."""
    puntos = []
    for i in range(6):
        angulo = math.radians(60 * i - 90)
        x = cx + TAMANO_HEX * math.cos(angulo)
        y = cy + TAMANO_HEX * math.sin(angulo)
        puntos.append((x, y))
    pygame.draw.polygon(superficie, color, puntos, grosor)

def pixel_a_hex(px, py, cam_x, cam_y):
    """Convierte un píxel de PANTALLA a (fila, col) del mundo, teniendo en cuenta la cámara."""
    # Pasamos de pantalla a mundo
    mx = px + cam_x
    my = py + cam_y

    # Estimación inicial
    fila_aprox = int((my - MARGEN_Y) / (ALTO_HEX * 0.75))
    col_aprox  = int((mx - MARGEN_X) / ANCHO_HEX)

    # Búsqueda en vecindario
    for fila in range(fila_aprox - 2, fila_aprox + 3):
        for col in range(col_aprox - 2, col_aprox + 3):
            if 0 <= fila < FILAS and 0 <= col < COLUMNAS:
                cx, cy = hex_a_pixel(fila, col)
                if math.hypot(mx - cx, my - cy) <= TAMANO_HEX:
                    return fila, col
    return None

def tamano_mundo():
    """Devuelve el ancho y alto totales del mapa en píxeles."""
    # Ancho: última columna + ancho de un hex + margen
    ancho = MARGEN_X * 2 + COLUMNAS * ANCHO_HEX
    # Alto: última fila con su factor 0.75 + un hex extra
    alto = MARGEN_Y * 2 + (FILAS - 1) * ALTO_HEX * 0.75 + ALTO_HEX
    return ancho, alto

# ============================================================
#  INICIALIZACIÓN
# ============================================================
pygame.init()
pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Juego de Hexágonos — con cámara")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont("consolas", 16)

# --- Estado de la cámara ---
camara_x, camara_y = 0.0, 0.0
MUNDO_ANCHO, MUNDO_ALTO = tamano_mundo()

def limitar_camara(cx, cy):
    """Impide que la cámara se salga del mundo."""
    # Si el mundo es más pequeño que la pantalla, centramos
    max_x = max(0, MUNDO_ANCHO - ANCHO_VENTANA)
    max_y = max(0, MUNDO_ALTO - ALTO_VENTANA)
    cx = max(0, min(cx, max_x))
    cy = max(0, min(cy, max_y))
    return cx, cy

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
        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            ejecutando = False
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if hex_bajo_raton is not None:
                print(f"Clic en hex: fila={hex_bajo_raton[0]}, col={hex_bajo_raton[1]}")

    # --- Movimiento de la cámara (teclado) ---
    teclas = pygame.key.get_pressed()
    dx = dy = 0
    if teclas[pygame.K_LEFT]  or teclas[pygame.K_a]: dx -= VELOCIDAD_CAMARA
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: dx += VELOCIDAD_CAMARA
    if teclas[pygame.K_UP]    or teclas[pygame.K_w]: dy -= VELOCIDAD_CAMARA
    if teclas[pygame.K_DOWN]  or teclas[pygame.K_s]: dy += VELOCIDAD_CAMARA

    camara_x, camara_y = limitar_camara(camara_x + dx, camara_y + dy)

    # --- Ratón -> mundo -> hex ---
    raton_x, raton_y = pygame.mouse.get_pos()
    hex_bajo_raton = pixel_a_hex(raton_x, raton_y, camara_x, camara_y)

    # --- Dibujo ---
    pantalla.fill(NEGRO)

    # 1) Hexágonos (solo los visibles, para ahorrar)
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            cx_mundo, cy_mundo = hex_a_pixel(fila, col)
            cx_pant = cx_mundo - camara_x
            cy_pant = cy_mundo - camara_y

            # Culling: si está muy fuera de la pantalla, no lo dibujamos
            if (cx_pant < -TAMANO_HEX * 2 or cx_pant > ANCHO_VENTANA + TAMANO_HEX * 2 or
                cy_pant < -TAMANO_HEX * 2 or cy_pant > ALTO_VENTANA + TAMANO_HEX * 2):
                continue

            dibujar_hexagono(pantalla, VERDE, cx_pant, cy_pant)
            dibujar_hexagono(pantalla, GRIS,  cx_pant, cy_pant, 2)

    # 2) Resaltar el hexágono bajo el ratón
    if hex_bajo_raton is not None:
        cx_mundo, cy_mundo = hex_a_pixel(*hex_bajo_raton)
        dibujar_hexagono(pantalla, AMARILLO,
                         cx_mundo - camara_x, cy_mundo - camara_y, 3)

    # 3) HUD
    if hex_bajo_raton is not None:
        texto = f"Hex: fila={hex_bajo_raton[0]} col={hex_bajo_raton[1]}"
    else:
        texto = "Hex: (fuera del mapa)"
    texto += f"   |   Cam: ({int(camara_x)}, {int(camara_y)})   |   Flechas/WASD para mover"
    pantalla.blit(fuente.render(texto, True, BLANCO), (10, 10))

    pygame.display.flip()
    reloj.tick(FPS)

# ============================================================
#  SALIDA
# ============================================================
pygame.quit()
sys.exit()