import pygame
import random
import copy

# O jogo é simple, se trata de um quadrado que sempre segue em frente, com o unico objetivo de pular os obtaculos

# importando os objetos e as funções de outros arquivos
from Enemy import Enemy
import Player as Player
from Collision import check_collision_between_polygons

# variaveis estaticas
enemy_prob = 100
enemies = []
min_time_between_enemies = 200
current_time_since_last_enemy = 0

# variaveis estaticas
JUMP = 1
DO_NOTHING = 0

score = 0

gameEnded = False

controlled = False

increase_counter_divide = 2
increase_counter_max = ((Player.Player.jump_height / Player.Player.jump_speed) * 2 + 2) / increase_counter_divide
increase_counter = 0

# calculo do tempo que uma ação leva para ser completada, poís é o tempo de espera para que a pessoa possa pular
# novamente
action_duration = ((Player.Player.jump_height / Player.Player.jump_speed) * 2 + 2) / increase_counter_divide
action_counter = 0

clock_tick = 250


# funcao para ver se teve ou nao colisao
def check_collisions(player, enemies):
    for enemy in enemies:
        collision(player, enemy)


def collision(player, enemy):
    global gameEnded
    # formula para calcular a o tamanho dos 2 objetos
    polygon1 = [(player.x, player.y), (player.x + player.width, player.y),
                (player.x + player.width, player.y + player.height), (player.x, player.y + player.height)]
    polygon2 = [(enemy.x, enemy.y), (enemy.x - enemy.base / 2, enemy.y + enemy.height),
                (enemy.x + enemy.base / 2, enemy.y + enemy.height)]

    # chamada da funcao para verificar se exitiu colisão, se sim, fim de jogo.
    if check_collision_between_polygons(polygon1, polygon2):
        gameEnded = True


def check_if_enemy_passed_player(player, enemies):
    global score

    # caso o jogador pular inimigo, ele ganha um ponto
    # quando o inimigo passar e ir para o fundo da tela, ele desaparece
    for enemy in enemies:
        if player.x > enemy.x + Enemy.base:
            if not enemy.scoreUpdated:
                score += 1
                enemy.scoreUpdated = True
        if enemy.x < 0:
            enemies.remove(enemy)


# definindo o update, o qual faz a atulização da tela sempre constante com as imagens do jogo
def update(display, player):
    global current_time_since_last_enemy
    global score
    global increase_counter
    global increase_counter_max

    # TODO: player.inair is broken
    # o jogador nao ganha ponto no ar, apenas quando pula inimigo e quando esta no chao
    if player.inair:
        increase_counter = 0

    if not player.inair and len(enemies) >= 0:
        if increase_counter < increase_counter_max:
            increase_counter += 1
        else:
            increase_counter = 0
            score += 1

    # chamando a funcao de colisao
    check_collisions(player, enemies)

    # ocorre o desenho do inimigo, para aparecer no jogo
    draw_static(display, player)
    player.draw_it(display)
    for e in enemies:
        e.draw_it(display)

    # intervalor de aparição entre os inimigos
    if current_time_since_last_enemy > min_time_between_enemies:
        if random.randint(0, enemy_prob - 1) == 0:
            e = Enemy()
            enemies.append(e)
            current_time_since_last_enemy = 0
    else:
        current_time_since_last_enemy += 1

    # manter atualizado a apaarencia do inimigo e jogador
    player.update()
    for e in enemies:
        e.update()

    # chamada da funcao para ver se o inimigo passou do jogador
    check_if_enemy_passed_player(player, enemies)

    # texto que mostra no jogo a pontuação do jogado
    myfont = pygame.font.SysFont('Comic Sans MS', 30)
    textsurface = myfont.render(str(score), False, (0, 0, 0))
    display.blit(textsurface, (0, 0))


# desenho da fase
def draw_static(display, player):
    display.fill(white)

    pygame.draw.rect(display, red, (0, 400 + player.height, width, height - 400))


#  Cores
red = (255, 0, 0)
white = (255, 255, 255)
black = (0, 0, 0)

# tamanho da tela
width, height = 800, 600


def run():
    global score
    global gameEnded
    global player
    global enemies

    global clock_tick

    enemies = []

    # Inicializando o jogo normal de jogador pelo game.py
    gameEnded = False
    pygame.init()
    pygame.font.init()
    caption = 'Jogo basico desenvolvido por Sanil Khurana'
    gameDisplay = pygame.display.set_mode((width, height))
    pygame.display.set_caption(caption)
    clock = pygame.time.Clock()
    crashed = False

    player = Player.Player()

    # Initial filling
    gameDisplay.fill(white)
    score = 0

    # Main game loop
    while not crashed and not gameEnded:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            elif event.type == pygame.KEYDOWN:
                if event.key == 32:
                    player.jump()
                elif event.key == 119:
                    clock_tick += 25
                elif event.key == 115:
                    clock_tick -= 25

        update(gameDisplay, player)

        pygame.display.update()
        clock.tick(clock_tick)

    pygame.quit()
    quit()


old_response = None


def controlled_run(wrapper, counter):
    global score
    global gameEnded
    global player
    global enemies

    global action_counter
    global action_duration

    global clock_tick

    enemies = []

    # Inicializando o jogo pela rede neural nn.py
    gameEnded = False
    pygame.init()
    pygame.font.init()
    caption = 'Jogo basico desenvolvido por Sanil Khurana' + str(counter)
    gameDisplay = pygame.display.set_mode((width, height))
    pygame.display.set_caption(caption)
    clock = pygame.time.Clock()
    crashed = False

    player = Player.Player()

    # Tela inicial com score 0 e fundo branco
    gameDisplay.fill(white)
    score = 0

    # para cada ação recebida, o score é salvo, e usado quando uma nova ação ocorre
    old_score = 0

    old_action = None
    old_closest_enemy = None

    # Jogo em loop
    while not crashed and not gameEnded:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
            elif event.type == pygame.KEYDOWN:
                if event.key == 119:
                    clock_tick += 25
                elif event.key == 115:
                    clock_tick -= 25

        # 1. Checar que uma ação foi tomada ou nao
        if action_counter < action_duration or player.inair:
            # nao é possivel efetuar uma acao, enquanto estiver fazendo uma
            action_counter += 1

            update(gameDisplay, player)
            pygame.display.update()
            clock.tick(clock_tick)

        else:
            # Uma ação pode ser feita
            action_counter = 0

            update(gameDisplay, player)

            new_score = copy.deepcopy(score)
            score_increased = 0

            if new_score > old_score:
                score_increased = 1

            values = dict()

            # Aqui é a parte em que a rede neural utiliza para controlar o personagem, mandando ações como "fazer nada",
            # e "pular", e ao mesmo tempo ele recebe os valores necessário para observar se o inimigo esrá perto ou não.

            if old_action is None:
                values['action'] = DO_NOTHING
            else:
                values['action'] = old_action

            if old_closest_enemy is None:
                values['old_closest_enemy'] = -1
            else:
                values['old_closest_enemy'] = old_closest_enemy

            if len(enemies) > 0:
                closest_enemy = 1000
                for enemy in enemies:
                    if enemy.x > player.x and enemy.x < closest_enemy:
                        closest_enemy = enemy.x
                values['closest_enemy'] = closest_enemy
            else:
                values['closest_enemy'] = -1

            values['score_increased'] = score_increased

            response = wrapper.control(values)

            # Somente é possivel fazer uma acao se o jogador nao estiver no ar
            if not player.inair:
                old_action = response

            if response == JUMP:
                player.jump()
            elif response == DO_NOTHING:
                pass

            old_score = new_score
            old_closest_enemy = values['closest_enemy']

    # pygame.quit()
    # quit()

    wrapper.gameover(score)


if __name__ == '__main__':
    run()
