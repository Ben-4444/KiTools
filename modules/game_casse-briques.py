import curses
import time
import random


resume = "Jeu de casse-briques interactif en console"
description = """Un jeu de casse-briques classique jouable dans le terminal.
Utilisez les flèches gauche/droite pour déplacer la raquette et essayez de détruire toutes les briques.
Best score : 40"""

def init_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)

def draw_paddle(win, paddle_pos, paddle_width, max_y):
    win.addstr(max_y-2, paddle_pos, "▄" * paddle_width, curses.color_pair(4))

def draw_ball(win, ball_y, ball_x):
    # Choisissez l'un de ces caractères : ● ○ ◉ ◎ ⚪ ⬤ ◯ 
    win.addch(int(ball_y), int(ball_x), "⬤", curses.color_pair(3))

def draw_bricks(win, bricks):
    for i, row in enumerate(bricks):
        for j, brick in enumerate(row):
            if brick == 1:
                win.addstr(i+2, j*8, "▰▰▰▰", curses.color_pair(5))
            elif brick == 2:
                win.addstr(i+2, j*8, "▰▰▰▰", curses.color_pair(6))
            elif brick == 3:
                win.addstr(i+2, j*8, "▰▰▰▰", curses.color_pair(7))

def update_best_score(new_score):
    with open(__file__, 'r') as f:
        lines = f.readlines()
    for line in lines:
        if "Best score :" in line:
            best_score = int(line.split(':')[1].strip()[:-3])
            break
    if new_score > best_score:
        best_score = new_score
        # Mettre à jour le fichier
        with open(__file__, 'r') as f:
            lines = f.readlines()
        
        # Trouver et mettre à jour la ligne contenant best_score
        for i, line in enumerate(lines):
            if line.strip().startswith('Best score :'):
                lines[i] = f'Best score : {best_score}"""\n'
                break
        
        # Réécrire le fichier
        with open(__file__, 'w') as f:
            f.writelines(lines)

def play_game(stdscr):
    curses.curs_set(0)
    init_colors()
    
    # Obtenir dimensions du terminal
    max_y, max_x = stdscr.getmaxyx()
    
    # Initialisation adaptée à la taille
    paddle_width = max_x // 10
    paddle_pos = (max_x - paddle_width) // 2
    ball_x = max_x // 2
    ball_y = max_y - 3
    dx = 0.5
    dy = -0.5
    score = 0
    
    # Création des briques adaptée à la largeur et hauteur
    brick_cols = (max_x - 2) // 8  # Divisé par 8 au lieu de 2 pour les briques plus larges
    brick_rows = max_y // 2 - 2  # Remplir la moitié du terminal
    bricks = [[1 for _ in range(brick_cols)] for _ in range(brick_rows)]
    
    # Ajout des briques spéciales
    for i in range(brick_rows):
        for j in range(brick_cols):
            rand = random.random()
            if rand < 0.10:  # 10% de briques solides
                bricks[i][j] = 2
            elif rand < 0.13:  # 3% de briques incassables
                bricks[i][j] = 3
    
    # Calculer la limite droite pour la balle
    max_ball_x = brick_cols * 8
    
    while True:
        stdscr.clear()
        
        # Affichage
        draw_paddle(stdscr, paddle_pos, paddle_width, max_y)
        draw_ball(stdscr, ball_y, ball_x)
        draw_bricks(stdscr, bricks)
        stdscr.addstr(0, 0, f"Score: {score}", curses.color_pair(3))
        
        # Déplacement de la balle
        ball_x += dx
        ball_y += dy
        
        # Collision avec les murs et limite droite
        if ball_x <= 0:
            dx = -dx
        elif ball_x >= max_ball_x:
            ball_x = max_ball_x - 1
            dx = -dx
        if ball_y <= 0:
            dy = -dy
            
        # Collision avec la raquette
        if int(ball_y) == max_y-2 and paddle_pos <= ball_x < paddle_pos + paddle_width:
            # Si la balle touche le bord gauche de la raquette
            if abs(ball_x - paddle_pos) < 2:
                dx = -abs(dx)  # Force le rebond vers la gauche
            # Si la balle touche le bord droit de la raquette
            elif abs(ball_x - (paddle_pos + paddle_width)) < 2:
                dx = abs(dx)  # Force le rebond vers la droite
            dy = -dy
            
        # Collision avec les briques
        brick_row = int(ball_y) - 2
        brick_col = int(ball_x) // 8  # Divisé par 8 au lieu de 2 pour les briques plus larges
        if 0 <= brick_row < brick_rows and 0 <= brick_col < brick_cols:
            if bricks[brick_row][brick_col] == 1:
                bricks[brick_row][brick_col] = 0
                dy = -dy
                score += 10
            elif bricks[brick_row][brick_col] == 2:
                bricks[brick_row][brick_col] = 1
                dy = -dy
                score += 5
            elif bricks[brick_row][brick_col] == 3:
                dy = -dy
        
        # Game over
        if ball_y > max_y-1:
            game_over_x = (max_x - 10) // 2
            stdscr.addstr(max_y//2, game_over_x, "GAME OVER!", curses.color_pair(1))
            stdscr.addstr(max_y//2 + 1, game_over_x-5, "Retourne bosser !", curses.color_pair(1))
            stdscr.addstr(max_y//2 + 2, game_over_x-5, f"Score final: {score}", curses.color_pair(3))
            update_best_score(score)
            stdscr.refresh()
            time.sleep(2)
            break
            
        # Contrôles
        stdscr.timeout(50)
        key = stdscr.getch()
        if key == curses.KEY_LEFT and paddle_pos > 0:
            paddle_pos -= 2
        elif key == curses.KEY_RIGHT and paddle_pos < max_x-paddle_width:
            paddle_pos += 2
        elif key == ord('q'):
            break
            
        stdscr.refresh()

def main():
    try:
        curses.wrapper(play_game)
    except KeyboardInterrupt:
        print("Ouais va, on s'arrete là !")


if __name__ == "__main__":
    main()
