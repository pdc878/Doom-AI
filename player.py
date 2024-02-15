from settings import *
import pygame as pg
import math

class Player:
    def __init__(self, game):
        self.game = game
        self.x, self.y = PLAYER_POS
        self.angle = PLAYER_ANGLE
        self.rel = 0
        self.shot = False
        self.health = PLAYER_MAX_HEALTH
        self.rel = 0
        self.health_recovery_delay = 700
        self.time_prev = pg.time.get_ticks()
        
        # Agent settings
        self.reward = 0
        self.score = 0
        self.done = False
        self.enemies_defeated = 0


    def recover_health(self):
        if self.check_health_recovery_delay() and self.health < PLAYER_MAX_HEALTH:
            self.health += 1

    def check_health_recovery_delay(self):
        time_now = pg.time.get_ticks()
        if time_now - self.time_prev > self.health_recovery_delay:
            self.time_prev = time_now
            return True
        
    def check_game_over(self):
        if self.health <= 1:
            self.game.object_renderer.game_over()
            pg.display.flip()
            pg.time.delay(1500)
            #self.reward -= 100
            self.done = True
            #self.game.new_game()

    def get_damage(self, damage):
        self.health -= damage
        self.game.object_renderer.player_damage()
        # self.reward -= 10
        self.game.sound.player_pain.play()
        self.check_game_over()

    def single_fire_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1 and not self.shot and not self.game.weapon.reloading:
                #self.game.sound.shotgun.play()
                self.shot = True
                self.game.weapon.reloading = True


    def movement(self, forward = False, backward = False, left = False, right = False):
        sin_a = math.sin(self.angle)
        cos_a = math.cos(self.angle)

        dx, dy = 0, 0

        speed = PLAYER_SPEED * self.game.delta_time

        speed_sin = speed * sin_a
        speed_cos = speed * cos_a

        # PLAYER CONTROLS
        # keys = pg.key.get_pressed()
        # if keys[pg.K_w]:
        #     dx += speed_cos
        #     dy += speed_sin
        # if keys[pg.K_s]:
        #     dx -= speed_cos
        #     dy -= speed_sin
        # if keys[pg.K_a]:
        #     dx += speed_sin
        #     dy -= speed_cos
        # if keys[pg.K_d]:
        #     dx -= speed_sin
        #     dy += speed_cos

        ## AGENT
        if forward:
            #self.reward += .01
            dx += speed_cos
            dy += speed_sin
        if backward:
            #self.reward += .01
            dx -= speed_cos
            dy -= speed_sin
        if left:
            #self.reward += .01
            dx += speed_sin
            dy -= speed_cos
        if right:
            #self.reward += .01
            dx -= speed_sin
            dy += speed_cos


        self.check_wall_collision(dx, dy)

        # if keys[pg.K_LEFT]:
        #     self.angle -= PLAYER_ROT_SPEED * self.game.delta_time
        # if keys[pg.K_RIGHT]:
        #     self.angle += PLAYER_ROT_SPEED * self.game.delta_time
        self.angle %= math.tau


        

    def check_wall(self,x,y):
        if (int(x),int(y)) in self.game.map.world_map:
            self.reward -= 1
        return (int(x),int(y)) not in self.game.map.world_map
    
    def check_wall_collision(self, dx, dy):
        scale = PLAYER_SIZE_SCALE / self.game.delta_time
        if self.check_wall(self.x + dx * scale, self.y):
            self.x += dx
            self.reward -= 1
            
        if self.check_wall(self.x, self.y + dy * scale):
            self.y += dy
            self.reward -= 1
        
    
    def play_step(self, action):
        # Convert the action to control commands
        controls = self.translate_action_to_controls(action)

        # Apply the controls
        self.movement(controls.get('forward', False), 
            controls.get('backward', False), 
            controls.get('left', False), 
            controls.get('right', False))


        # Rotate player based on control
        if controls.get('rotate_left', False):
            #self.reward += .01
            self.angle -= PLAYER_ROT_SPEED * self.game.delta_time
        elif controls.get('rotate_right', False):
            #self.reward += .01
            self.angle += PLAYER_ROT_SPEED * self.game.delta_time
        self.angle %= math.tau  # Keep angle within a valid range

        # Shooting
        if controls.get('shoot', False) and not self.shot and not self.game.weapon.reloading:
            self.shot = True
            self.game.weapon.reloading = True
            #self.game.sound.shotgun.play()

            

        # Update the player's state
        self.update()
        if self.health <= 1:
            #self.reward = -100  # Negative reward for losing
            self.done = True
            self.check_game_over()

        # Calculate the score
        self.score = self.calculate_score()

        return self.reward, self.done, self.score


    def translate_action_to_controls(self, action):
        controls = {'forward': False, 'backward': False, 'left': False, 'right': False, 'rotate_left': False, 'rotate_right': False, 'shoot': False}
        action_commands = self.game.agent.action_space[action]  # Access action space from the agent

        for command in action_commands:
            if 'F' == command:
                controls['forward'] = True
            if 'B' == command:
                controls['backward'] = True
            if 'L' == command:
                controls['left'] = True
            if 'R' == command:
                controls['right'] = True
            if 'RL' == command:
                controls['rotate_left'] = True
            if 'RR' == command:
                controls['rotate_right'] = True
            if 'S' == command:
                controls['shoot'] = True

        return controls


    def calculate_score(self):
        self.score += self.enemies_defeated * SCORE_PER_ENEMY
        # score += self.areas_explored * SCORE_PER_AREA

        # Add/subtract points for health (e.g., bonus for high health)
        # if self.health > HEALTH_THRESHOLD:
        #     score += HEALTH_BONUS

        w = self.game.object_handler.npc_positions
        w = list(w)
        

        dis_score = math.sqrt((self.pos[0] - w[0][0])**2 + (self.pos[1] - w[0][1])**2)
        self.reward += 50 * math.exp(-0.1 * dis_score)

        if dis_score < 0.5:
            self.score += 10

        return self.score


    def draw(self):
        pg.draw.line(self.game.screen, 'yellow', (self.x * 100, self.y * 100),
                    (self.x * 100 + WIDTH * math.cos(self.angle),
                     self.y * 100 + WIDTH * math. sin(self.angle)), 2)
        pg.draw.circle(self.game.screen, 'green', (self.x * 100, self.y * 100), 15)

    def mouse_control(self):
        mx, my = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        self.angle += self.rel * MOUSE_SENSITIVITY * self.game.delta_time

    def update(self):
        self.movement()
        # self.mouse_control()
        self.recover_health()

    @property
    def pos(self):
        return (self.x, self.y)
    
    @property
    def map_pos(self):
        return (int(self.x), int(self.y))
    
    @property
    def kill_count(self):
        return self.enemies_defeated
    
    ### AGENT
    # Things that can change: W, A, S, D, MOUSE_angle mx, and shoot MOUSE_BUTTONDOWN
    
    # Reset
    # Reward
    # Play Action
    # Game Iteration
    # is dead