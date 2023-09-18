import pygame, math, random, sys
from pygame import mixer
from Paddle import Paddle
from Ball import Ball

WIDTH = 1280
HEIGHT = 720

PADDLE_SPEED = 600

WINNING_SCORE = 3

TIMER_INTERVAL = 1000

class GameMain:
    def __init__(self):
        pygame.init()
        # Set up the timer
        pygame.time.set_timer(pygame.USEREVENT, TIMER_INTERVAL)

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        self.music_channel = mixer.Channel(0)
        self.music_channel.set_volume(0.2)

        self.sounds_list = {
            'paddle_hit': mixer.Sound('sounds/paddle_hit.wav'),
            'score': mixer.Sound('sounds/score.wav'),
            'wall_hit': mixer.Sound('sounds/wall_hit.wav')
        }

        self.player1 = Paddle(self.screen, 30, 90, 15, 120, WIDTH, HEIGHT)
        self.player2 = Paddle(self.screen, WIDTH - 30, HEIGHT - 90, 15, 120, WIDTH, HEIGHT)

        self.ball = Ball(self.screen, WIDTH / 2 - 2, HEIGHT / 2 - 2, 12, 12, WIDTH, HEIGHT)

        self.player1_score = 0
        self.player2_score = 0

        self.serving_player = 1
        self.winning_player = 0

        #1. 'start' (the beginning of the game, before first serve)
        #2. 'serve' (waiting on a key press to serve the ball)
        #3. 'play' (the ball is in play, bouncing between paddles)
        #4. 'done' (the game is over, with a victor, ready for restart)

        self.game_state = 'start'
        self.ai_choice = 1
        self.ai_random_win_last_round = False

        self.small_font = pygame.font.Font('./font.ttf', 24)
        self.large_font = pygame.font.Font('./font.ttf', 48)
        self.score_font = pygame.font.Font('./font.ttf', 96)

        #text
        self.t_welcome = self.small_font.render("Welcome to Pong!", False, (255, 255, 255))
        self.t_press_enter_begin = self.small_font.render('Press Enter to begin!', False, (255, 255, 255))
        # self.t_press_choice_ai = self.small_font.render('Press 1 or 2 to pick AI for player 2', False, (255, 255, 255))
        self.t_player_turn = self.small_font.render("player" + str(self.serving_player) + "'s serve!", False, (255, 255, 255))
        self.t_press_enter_serve = self.small_font.render('Press Enter to serve!', False, (255, 255, 255))
        self.t_player_win = self.large_font.render("player" + str(self.serving_player) + "'s wins!", False, (255, 255, 255))
        self.t_press_restart = self.small_font.render("Press Enter to restart", False, (255, 255, 255))
        self.t_p1_score = self.score_font.render(str(self.player1_score), False, (255, 255, 255))
        self.t_p2_score = self.score_font.render(str(self.player2_score), False, (255, 255, 255))

        self.max_frame_rate = 60

    def update(self, dt):

        ##! Random speed of the ball each `serve`
        if self.game_state == "serve":
            self.ball.dy = random.uniform(-150, 150)
            if (self.ball.dx == 0):
                ##! IF player_1 => Left to Right
                if self.serving_player == 1:
                    self.ball.dx = random.uniform(420, 600) # Define the speed of the ball 
                    # print('[ serve-state ] SET self.ball.dx =', self.ball.dx)
                ##! IF player_2 => Right to Left
                else:
                    self.ball.dx = -random.uniform(420, 600)
                    # print('[ serve-state ] SET self.ball.dx =', self.ball.dx)



        elif self.game_state == 'play':
            if self.ball.Collides(self.player1):
                self.ball.dx = -self.ball.dx * 1.03 #reflect speed multiplier
                self.ball.rect.x = self.player1.rect.x + 15
                if self.ball.dy < 0:
                    self.ball.dy = -random.uniform(30, 450)
                    # print('[ play-state ] SET (player1) self.ball.dy =', self.ball.dy)
                else:
                    self.ball.dy = random.uniform(30, 450)
                    # print('[ play-state ] SET (player1) self.ball.dy =', self.ball.dy)
                self.music_channel.play(self.sounds_list['paddle_hit'])

            if self.ball.Collides(self.player2):
                self.ball.dx = -self.ball.dx * 1.03
                self.ball.rect.x = self.player2.rect.x - 12
                if self.ball.dy < 0:
                    self.ball.dy = -random.uniform(30, 450)
                    # print('[ play-state ] SET (player2) self.ball.dy =', self.ball.dy)
                else:
                    self.ball.dy = random.uniform(30, 450)
                    # print('[ play-state ] SET (player2) self.ball.dy =', self.ball.dy)
                self.music_channel.play(self.sounds_list['paddle_hit'])

            # ball hit top wall
            if self.ball.rect.y <= 0:
                self.ball.rect.y = 0
                self.ball.dy = -self.ball.dy
                self.music_channel.play(self.sounds_list['wall_hit'])

            # ball hit bottom wall
            if  self.ball.rect.y >= HEIGHT - 12:
                self.ball.rect.y = HEIGHT - 12
                self.ball.dy = -self.ball.dy
                self.music_channel.play(self.sounds_list['wall_hit'])

            ##! AI-002
            if self.ai_choice == 2:
                ##! AI CONTROL PADDLE ONLY WHEN THE BALL PASS HALF OF THE SCREEN
                if self.ball.rect.x >= WIDTH//2 - 12 and self.ball.dx > 0:
                    # print('------------------------------------------------------------------------------------------')
                    # print('[ AI-002 ] ball-X={}, ball-Y={}'.format(self.ball.rect.x, self.ball.rect.y))
                    # print('[ AI-002 ] dy={}, paddle-x={}, paddle-y={}'.format(self.player2.dy, self.player2.rect.x, self.player2.rect.y))
                    # print(self.player2.rect.y, self.player2.height, self.ball.rect.y)
                    # print('------------------------------------------------------------------------------------------')
                    if self.player2.rect.y + self.player2.height//2 >= self.ball.rect.y:
                        self.player2.dy = -PADDLE_SPEED
                    else:
                        self.player2.dy = PADDLE_SPEED
                else:
                    ##! MOVE AI PADDLE TO THE MIDDLE
                    if self.player2.rect.y > HEIGHT//2 - 50 and self.player2.rect.y < HEIGHT//2 + 50:
                        ##! PADDLE STAY IDLE
                        pass
                    else:
                        if self.player2.rect.y >= HEIGHT//2:
                            self.player2.dy = -PADDLE_SPEED
                        else:
                            self.player2.dy = PADDLE_SPEED

            # if self.ai_choice == 2:
            #     self.ai_choice = 1
            ##! COUNT SCORE
            ##! IF player_1 lose
            if self.ball.rect.x < 0:
                self._SwitchPlayer(1)
                self.player2_score +=1
                self.music_channel.play(self.sounds_list['score'])
                ##! Check WIN CONDITION
                if self.player2_score == WINNING_SCORE:
                    self._WinningPlayer(2)
                    self.game_state = 'done'
                else:
                    ##! RESET BALL
                    self.game_state = 'serve'
                    self.ball.Reset()
            ##! IF player_2 lose
            if self.ball.rect.x > WIDTH:
                self._SwitchPlayer(2)
                self.player1_score += 1
                self.music_channel.play(self.sounds_list['score'])
                if self.player1_score == WINNING_SCORE:
                    self._WinningPlayer(1)
                    self.game_state = 'done'
                else:
                    self.game_state = 'serve'
                    self.ball.Reset()
                
                if self.ai_choice == 1:
                    # self.ai_choice = 2
                    self.ai_random_win_last_round = True
            
            

        if self.game_state == 'play':
            self.ball.update(dt)

        self.player1.update(dt)
        self.player2.update(dt)

    ##! GET KEYBOARDS F/ USER
    def process_input(self):
        #one time input
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                print('Goodbye! See you again :)')
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.game_state == 'start':
                        self.game_state = 'serve'
                    elif self.game_state == 'serve':
                        if self.ai_random_win_last_round:
                            self.ai_choice = 2
                            self.ai_random_win_last_round = False
                        else:
                            self.ai_choice = 1

                        self.game_state = 'play'
                    elif self.game_state == 'done':
                        self.game_state = 'serve'
                        self.ball.Reset()

                        #reset score
                        self.player1_score = 0
                        self.player2_score = 0

                        if self.winning_player == 1:
                            self._SwitchPlayer(2)
                        else:
                            self._SwitchPlayer(1)

                ##! GET KEYBOARDS F/ USER, SET ai_choice TOO
                if event.key == pygame.K_1:
                    print("Key '1' pressed!, set ai_choice to 1")
                    self.ai_choice = 1
                elif event.key == pygame.K_2:
                    print("Key '2' pressed!, set ai_choice to 2")
                    self.ai_choice = 2

            ##! Control AI
            ##! Trigger Event of every second
            if event.type == pygame.USEREVENT and self.game_state == 'play' and self.ai_choice > 0:

                ##! AI-001
                if self.ai_choice == 1:
                    randDirection = random.randint(0, 1)
                    speedPaddleResult = 0
                    if randDirection == 0:
                        speedPaddleResult = -PADDLE_SPEED
                        # speedPaddleResult = -PADDLE_SPEED * (random.randint(1, 2))
                        self.player2.dy = speedPaddleResult
                    elif randDirection == 1:
                        speedPaddleResult = PADDLE_SPEED
                        # speedPaddleResult = PADDLE_SPEED * (random.randint(1, 2))
                        self.player2.dy = speedPaddleResult
                    new_timer_interval = TIMER_INTERVAL * random.randint(1, 2)
                    print('[ timer-triggered ] self.player2.dy =', speedPaddleResult, 'new_timer_interval =', new_timer_interval)
                    pygame.time.set_timer(pygame.USEREVENT, new_timer_interval)
                        
                    

        #continuous input 
        ##! ( PADDLE CONTROL )
        key = pygame.key.get_pressed()
        if key[pygame.K_w]:
            self.player1.dy = -PADDLE_SPEED
        elif key[pygame.K_s]:
            self.player1.dy = PADDLE_SPEED
        else:
            self.player1.dy = 0

        if self.ai_choice == 0:
            if key[pygame.K_UP]:
                self.player2.dy = -PADDLE_SPEED
            elif key[pygame.K_DOWN]:
                self.player2.dy = PADDLE_SPEED
            else:
                self.player2.dy = 0

    def _SwitchPlayer(self, player_number):
        self.serving_player = player_number
        self.t_player_turn = self.small_font.render("player" + str(player_number) + "'s serve!", False, (255, 255, 255))

    def _WinningPlayer(self, player_number):
        self.winning_player = player_number
        self.t_player_win = self.large_font.render("player" + str(player_number) + "'s wins!", False, (255, 255, 255))


    def draw(self):
        self.screen.fill((40, 45, 52))


        # FOR TEXT CONTROL PROCESS
        if self.game_state == "start":
            text_rect = self.t_welcome.get_rect(center=(WIDTH/2, 20))
            self.screen.blit(self.t_welcome, text_rect)
            text_rect = self.t_press_enter_begin.get_rect(center=(WIDTH / 2, 40))
            self.screen.blit(self.t_press_enter_begin, text_rect)
            # text_rect = self.t_press_choice_ai.get_rect(center=(WIDTH / 2, 60))
            # self.screen.blit(self.t_press_choice_ai, text_rect)

            ##! Write ai_choice TEXT
            text_rect = self.small_font.render('Current AI mode: {}'.format(self.ai_choice), False, (255, 255, 255)).get_rect(center=(WIDTH / 2, 60))
            self.screen.blit(self.small_font.render('Current AI mode: {}'.format(self.ai_choice), False, (255, 255, 255)), text_rect)
        elif self.game_state == "serve":
            text_rect = self.t_player_turn.get_rect(center=(WIDTH / 2, 20))
            self.screen.blit(self.t_player_turn, text_rect)
            text_rect = self.t_press_enter_serve.get_rect(center=(WIDTH / 2, 40))
            self.screen.blit(self.t_press_enter_serve, text_rect)
        elif self.game_state == "play":
            # tmp='RandomAI' if self.ai_choice == 1 else 'HardAI'
            # print(tmp)
            text_rect = self.small_font.render('Current AI mode: {} (SUPERAI)'.format(self.ai_choice, 'TEXT'), False, (255, 255, 255)).get_rect(center=(WIDTH / 2, 20))
            self.screen.blit(self.small_font.render('Current AI mode: {} ({})'.format(self.ai_choice, 'RandomAI' if self.ai_choice == 1 else 'HardAI'), False, (255, 255, 255)), text_rect)
            pass
        elif self.game_state == "done":
            text_rect = self.t_player_win.get_rect(center=(WIDTH / 2, 30))
            self.screen.blit(self.t_player_win, text_rect)
            text_rect = self.t_press_restart.get_rect(center=(WIDTH / 2, 70))
            self.screen.blit(self.t_press_restart, text_rect)

        self.DisplayScore()

        ##! DRAW BALL AND PADDLES
        self.player1.render()
        self.player2.render()
        self.ball.render()

    def DisplayScore(self):
        self.t_p1_score = self.score_font.render(str(self.player1_score), False, (255, 255, 255))
        self.t_p2_score = self.score_font.render(str(self.player2_score), False, (255, 255, 255))
        self.screen.blit(self.t_p1_score, (WIDTH/2 - 50, HEIGHT/3))
        self.screen.blit(self.t_p2_score, (WIDTH / 2 + 30, HEIGHT / 3))



if __name__ == '__main__':
    main = GameMain()

    clock = pygame.time.Clock()

    while True:
        pygame.display.set_caption("Pong game running with {:d} FPS".format(int(clock.get_fps())))

        # elapsed time from the last call
        dt = clock.tick(main.max_frame_rate)/1000.0

        main.process_input()
        main.update(dt)
        main.draw()

        pygame.display.update()


