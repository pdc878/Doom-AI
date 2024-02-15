import pygame as pg
import sys
from settings import *
from map import *
from player import *
from raycasting import *
from object_renderer import *
from sprite_object import *
from object_handler import *
from weapon import *
from sound import *
from pathfinding import *
from agent import *
from helper import plot

import time

import matplotlib.pyplot as plt


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_visible(False)
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.delta_time = 1
        self.global_trigger = False
        self.global_event = pg.USEREVENT + 0
        pg.time.set_timer(self.global_event, 40)
        self.start_time = 0 
        self.plot_scores = []
        self.plot_mean_scores = []
        self.total_score = 0
        self.record = -1000
        self.action_history = []
        self.new_game()

    def new_game(self):
        self.start_time = time.time()
        self.map = Map(self)
        self.player = Player(self)
        self.object_renderer = ObjectRenderer(self)
        self.raycasting = RayCasting(self)
        self.object_handler = ObjectHandler(self)
        self.weapon = Weapon(self)
        self.sound = Sound(self)
        self.pathfinding = Pathfinding(self)
        self.agent = Agent(self)
        

    def update(self):
        self.player.update()
        self.raycasting.update()
        self.object_handler.update()
        self.weapon.update()
        pg.display.flip()
        self.delta_time = self.clock.tick(FPS)
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))

    def draw(self):
        # self.screen.fill('black')
        self.object_renderer.draw()
        self.weapon.draw()
        # self.map.draw()
        # self.player.draw()

    def check_events(self):
        self.global_trigger = False
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()

            elif event.type == self.global_event:
                self.global_trigger = True

            self.player.single_fire_event(event)


    def run(self, on_update):
        while True:
            self.check_events()
            self.draw()
            self.update()
            on_update()  # Call the training function
            
# Define the training function
def train_step():

    # Access global game and agent variables
    global game, agent
    state_old = agent.get_state(game)
    if state_old[0] < 0 or state_old[1] < 0 or state_old[0] > 5 or state_old[1] > 8:
        game.new_game()
        pg.time.delay(1000)
    else:
        final_move = agent.get_action(state_old)
        reward, done, score = game.player.play_step(final_move)
        #print("reward: ", reward)
        # print("done: ", done)
        # print("score: ", score)   
        state_new = agent.get_state(game)
        if len(state_new) > 500:
            game.action_history.append(final_move)
            agent.train_short_memory(state_old, final_move, reward, state_new, done)
            agent.remember(state_old, final_move, reward, state_new, done)
            
            t0 = time.time()
            # print(t0 - game.start_time)
            if t0 - game.start_time > 20 or state_old[0] < 0 or state_old[1] < 0 or state_old[0] > 5 or state_old[1] > 9:
                #print(pg.time.get_ticks() - current_time)
                done = True

            if done:
                # game.new_game()
                # agent.n_games += 1
                # agent.train_long_memory()


                # train long memory, plot result
                game.new_game()
                pg.time.delay(1000)
                agent.n_games += 1
                #agent.train_long_memory()

                if score > game.record:
                    record = score
                    agent.model.save()

                print('Game', agent.n_games, 'Score', score, 'Record:', record)
                game.plot_scores.append(reward)
                game.total_score += score
                mean_score = game.total_score / agent.n_games
                game.plot_mean_scores.append(mean_score)
                plot(game.plot_scores, game.plot_mean_scores)


                #plot_histogram(game.action_history)


def plot_histogram(action_history):
    plt.hist(action_history, bins=range(len(set(action_history)) + 1), align='left')
    plt.xlabel('Actions')
    plt.ylabel('Frequency')
    plt.title('Histogram of Actions Used')
    plt.show() 


if __name__ == '__main__':
    game = Game()
    agent = Agent(game)
    game.run(train_step)