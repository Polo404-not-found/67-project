import math
import random
import sys

import pygame

# ============================================================
#  CONFIGURACIÓN
# ============================================================
ANCHO_VENTANA, ALTO_VENTANA = 900, 700
TAMANO_HEX = 40
MAPA_ANCHO = 30         # ancho del mapa en "columnas" (para la generación)
MAPA_ALTO  = 25         # alto del mapa en "filas" (para la generación)
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
VERDE       = (40, 80, 40)
AMARILLO    = (255, 220, 0)

# ============================================================
#  GEOMETRÍA DE HEXÁGONOS (axial, pointy-top)
# ============================================================
# En axial, cada hexágono se identifica por (q, r).
# Los 6 vecinos son siempre los mismos desplazamientos, sin casos especiales.

DIRECCIONES = [ #(q,r)
    (+1,  0),   # E
    (+1, -1),   # NE
    ( 0, -1),   # NW
    (-1,  0),   # W
    (-1, +1),   # SW
    ( 0, +1),   # SE
]

# Biomas hexagonos
BIOMAS = ["llanura", "bosque", "colina", "agua"]
PESOS_BIOMAS = [0.5, 0.25, 0.15, 0.10]
COLORES_BIOMA = {
    "llanura": (100, 160, 80),
    "bosque":  (40, 90, 50),
    "colina":  (140, 120, 80),
    "agua":    (60, 100, 160),
}

def vecinos(q, r):
    """Devuelve los 6 vecinos de (q, r) en axial."""
    return [(q + dq, r + dr) for dq, dr in DIRECCIONES]

def distancia(q1, r1, q2, r2):
    """Distancia en hexágonos entre dos casillas axiales."""
    return (abs(q1 - q2) + abs(q1 + r1 - q2 - r2) + abs(r1 - r2)) // 2

def axial_a_pixel(q, r, tamano):
    """Centro del hexágono en coordenadas del MUNDO (sin cámara)."""
    x = math.sqrt(3) * tamano * (q + r / 2)
    y = tamano * 1.5 * r
    return x, y

def pixel_a_axial(mx, my, tamano):
    """Punto del mundo -> (q, r) axial."""
    x = mx / tamano
    y = my / tamano

    q_float = (math.sqrt(3) / 3) * x - (1 / 3) * y
    r_float = (2 / 3) * y

    # Redondeo hexagonal (usando coordenadas cúbicas)
    s_float = -q_float - r_float
    q_int = round(q_float)
    r_int = round(r_float)
    s_int = round(s_float)

    dq = abs(q_int - q_float)
    dr = abs(r_int - r_float)
    ds = abs(s_int - s_float)

    if dq > dr and dq > ds:
        q_int = -r_int - s_int
    elif dr > ds:
        r_int = -q_int - s_int

    return q_int, r_int

def dibujar_hexagono(superficie, color, cx, cy, tamano, grosor=0):
    """Dibuja hexágono pointy-top centrado en (cx, cy), radio 'tamano'."""
    puntos = []
    for k in range(6):
        angulo = math.radians(60 * k - 90)
        x = cx + tamano * math.cos(angulo)
        y = cy + tamano * math.sin(angulo)
        puntos.append((x, y))
    pygame.draw.polygon(superficie, color, puntos, grosor)

def generar_mapa_rectangular(ancho, alto):
    """Genera las coordenadas axiales (q, r) de un mapa rectangular.
       Usa offset internamente SOLO para la generación inicial."""
    coords = []
    for fila in range(alto):
        for col in range(ancho):
            q = col - (fila - (fila & 1)) // 2
            r = fila
            coords.append((q, r))
    return coords

def oscurecer(color, factor=0.6):
    """Devuelve un color más oscuro."""
    return (int(color[0] * factor), int(color[1] * factor), int(color[2] * factor))

# ============================================================
#  MUNDO ↔ PANTALLA (cámara + zoom)
# ============================================================
def mundo_a_pantalla(mx, my, cam_x, cam_y, zoom):
    return (mx - cam_x) * zoom, (my - cam_y) * zoom

def pantalla_a_mundo(px, py, cam_x, cam_y, zoom):
    return px / zoom + cam_x, py / zoom + cam_y

# ============================================================
#  CÁMARA
# ============================================================
def limitar_camara(cx, cy, zoom):
    """Evita que la cámara se salga del mundo (teniendo en cuenta el zoom)."""
    mundo_visible_ancho = ANCHO_VENTANA / zoom
    mundo_visible_alto  = ALTO_VENTANA / zoom
    max_x = max(0, MUNDO_ANCHO - mundo_visible_ancho)
    max_y = max(0, MUNDO_ALTO  - mundo_visible_alto)
    return max(0, min(cx, max_x)), max(0, min(cy, max_y))

def zoom_anclado(cam_x, cam_y, zoom_viejo, zoom_nuevo, punto_pantalla):
    """Recalcula la cámara para que el punto de pantalla no se mueva al cambiar el zoom."""
    mx, my = punto_pantalla
    mundo_x = mx / zoom_viejo + cam_x
    mundo_y = my / zoom_viejo + cam_y
    return (mundo_x - mx / zoom_nuevo,
            mundo_y - my / zoom_nuevo)

# ============================================================
#  GENERACIÓN DEL MAPA
# ============================================================
mapa = {}   # {(q, r): {"terreno": ...}}

for q, r in generar_mapa_rectangular(MAPA_ANCHO, MAPA_ALTO):
    mapa[(q, r)] = {"bioma": random.choices(BIOMAS, PESOS_BIOMAS)[0]}

# Tamaño del mundo en píxeles (para limitar la cámara)
if mapa:
    xs = []
    ys = []
    for (q, r) in mapa:
        x, y = axial_a_pixel(q, r, TAMANO_HEX)
        xs.append(x)
        ys.append(y)
    MUNDO_ANCHO = max(xs) - min(xs) + MARGEN_X * 2 + TAMANO_HEX * 2
    MUNDO_ALTO  = max(ys) - min(ys) + MARGEN_Y * 2 + TAMANO_HEX * 2
    OFFSET_MUNDO_X = -min(xs) + MARGEN_X + TAMANO_HEX
    OFFSET_MUNDO_Y = -min(ys) + MARGEN_Y + TAMANO_HEX
else:
    MUNDO_ANCHO = ANCHO_VENTANA
    MUNDO_ALTO = ALTO_VENTANA
    OFFSET_MUNDO_X = 0
    OFFSET_MUNDO_Y = 0

# ============================================================
#  INICIALIZACIÓN
# ============================================================
pygame.init()
pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Juego de Hexágonos — axial")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont("consolas", 16)

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
            elif evento.key == pygame.K_r:
                camara_x, camara_y = 0.0, 0.0
                zoom = 1.0

        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if hex_bajo_raton is not None:
                print(f"Clic en hex: q={hex_bajo_raton[0]}, r={hex_bajo_raton[1]}")

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
    mundo_x, mundo_y = pantalla_a_mundo(raton_x, raton_y, camara_x, camara_y, zoom)

    # Quitamos el offset del mundo antes de convertir a axial
    hex_bajo_raton = pixel_a_axial(mundo_x - OFFSET_MUNDO_X,
                                   mundo_y - OFFSET_MUNDO_Y,
                                   TAMANO_HEX)

    if hex_bajo_raton not in mapa:
        hex_bajo_raton = None

    # --- Dibujo ---
    pantalla.fill(NEGRO)

    tamano_pant = TAMANO_HEX * zoom

    # 1) Hexágonos visibles
    for (q, r) in mapa:
        mundo_cx, mundo_cy = axial_a_pixel(q, r, TAMANO_HEX)
        mundo_cx += OFFSET_MUNDO_X
        mundo_cy += OFFSET_MUNDO_Y

        pant_cx, pant_cy = mundo_a_pantalla(mundo_cx, mundo_cy, camara_x, camara_y, zoom)

        # Culling
        if (pant_cx < -tamano_pant * 2 or pant_cx > ANCHO_VENTANA + tamano_pant * 2 or
            pant_cy < -tamano_pant * 2 or pant_cy > ALTO_VENTANA + tamano_pant * 2):
            continue

        coordenadas_hexagono = mapa[(q, r)]
        bioma = coordenadas_hexagono["bioma"]
        color = COLORES_BIOMA[bioma]
        dibujar_hexagono(pantalla, color, pant_cx, pant_cy, tamano_pant)
        dibujar_hexagono(pantalla, oscurecer(color),  pant_cx, pant_cy, tamano_pant, 2)

    # 2) Resaltado bajo el ratón
    if hex_bajo_raton is not None:
        q, r = hex_bajo_raton
        mundo_cx, mundo_cy = axial_a_pixel(q, r, TAMANO_HEX)
        mundo_cx += OFFSET_MUNDO_X
        mundo_cy += OFFSET_MUNDO_Y
        pant_cx, pant_cy = mundo_a_pantalla(mundo_cx, mundo_cy, camara_x, camara_y, zoom)
        dibujar_hexagono(pantalla, AMARILLO, pant_cx, pant_cy, tamano_pant, 3)

    # 3) HUD
    if hex_bajo_raton is not None:
        q, r = hex_bajo_raton
        bioma = mapa[(q, r)]["bioma"]
        texto =f"Hex: q={q} r={r} | Bioma: {bioma}"
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