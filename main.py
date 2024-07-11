import pygame
import pygame_gui
import math

# Inicializa o pygame
pygame.init()

# Dimensões da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulação de Rotação de Pneu")

# Definições de cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (169, 169, 169)

# Carregar som
pygame.mixer.init()
beep_sound = pygame.mixer.Sound('pneu-som.wav')

# Inicializar fonte
pygame.font.init()
font = pygame.font.SysFont('Arial', 25)

# Configurar a interface do usuário
manager = pygame_gui.UIManager((WIDTH, HEIGHT))
speed_input = pygame_gui.elements.UITextEntryLine(
    relative_rect=pygame.Rect((10, 550), (100, 30)),
    manager=manager
)
speed_input.set_text("10")  # Valor inicial

# Variáveis do pneu
actual_diameter_cm = 64.68  # Diâmetro real do pneu em centímetros
display_diameter = HEIGHT * 0.8  # Diâmetro para exibição, ocupando 80% da altura da tela
display_radius = display_diameter / 2
circumference_m = math.pi * (actual_diameter_cm / 100)  # Circunferência em metros
angle = 0  # Ângulo inicial de rotação
speed_kmh = 10  # Velocidade inicial em km/h
speed_rps = speed_kmh / (3.6 * circumference_m)  # Converter km/h para rotações por segundo (RPS)

# Posição inicial do centro do pneu
x_center = WIDTH // 2
y_center = HEIGHT // 2

clock = pygame.time.Clock()
last_contact = False  # Flag para detectar o contato com o solo
contact_tolerance = 15  # Tolerância para detectar contato (em pixels)

# Função para calcular a velocidade em km/h
def calculate_speed_kmh(speed_rps):
    speed_m_s = speed_rps * circumference_m
    speed_kmh = speed_m_s * 3.6
    return speed_kmh

# Função para exibir a velocidade na tela
def display_speed(speed_kmh):
    speed_text = font.render(f'Velocidade: {speed_kmh:.2f} km/h', True, BLACK)
    screen.blit(speed_text, (10, 10))

# Função para desenhar a banda de rodagem do pneu
def draw_tread(surface, center_x, center_y, radius, angle):
    tread_width = 40  # Aumentar a largura da banda de rodagem
    for i in range(0, 360, 30):  # Desenha marcas da banda de rodagem a cada 30 graus
        start_x = center_x + (radius - tread_width) * math.cos(math.radians(angle + i))
        start_y = center_y + (radius - tread_width) * math.sin(math.radians(angle + i))
        end_x = center_x + radius * math.cos(math.radians(angle + i))
        end_y = center_y + radius * math.sin(math.radians(angle + i))
        pygame.draw.line(surface, BLACK, (start_x, start_y), (end_x, end_y), 5)

# Loop principal
running = True
while running:
    time_delta = clock.tick(60) / 1000.0  # Controlar a velocidade do loop

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        manager.process_events(event)

    manager.update(time_delta)

    # Atualizar a velocidade com o valor do campo de entrada de texto
    try:
        speed_kmh = float(speed_input.get_text())
        if speed_kmh < 0:
            speed_kmh = 0
    except ValueError:
        speed_kmh = 0

    # Converter a velocidade de km/h para rotações por segundo (RPS)
    speed_rps = speed_kmh / (3.6 * circumference_m)

    # Limpar a tela
    screen.fill(WHITE)

    # Calcular a posição do pito
    pito_x = x_center + (display_radius * math.cos(math.radians(angle)))
    pito_y = y_center + (display_radius * math.sin(math.radians(angle)))

    # Desenhar o pneu
    pygame.draw.circle(screen, BLACK, (x_center, y_center), int(display_radius), 5)
    pygame.draw.circle(screen, BLACK, (x_center, y_center), int(display_radius - 40), 0)  # Banda de rodagem
    draw_tread(screen, x_center, y_center, display_radius - 20, angle)  # Marcas da banda de rodagem

    # Desenhar o pito
    pygame.draw.circle(screen, BLACK, (int(pito_x), int(pito_y)), 15)

    # Verificar se o pito tocou o solo
    if abs(pito_y - (y_center + display_radius)) < contact_tolerance and not last_contact:
        beep_sound.play()
        last_contact = True
    elif abs(pito_y - (y_center + display_radius)) >= contact_tolerance:
        last_contact = False

    # Atualizar o ângulo de rotação
    angle -= speed_rps * 360 / 60  # Converte RPS para ângulo por frame (360 graus por rotação, 60 frames por segundo)
    if angle <= -360:
        angle += 360

    # Exibir a velocidade na tela
    display_speed(speed_kmh)

    # Desenhar a interface do usuário
    manager.draw_ui(screen)

    # Atualizar a tela
    pygame.display.flip()

pygame.quit()
