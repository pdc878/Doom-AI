from player import *
from settings import *
import numpy as np
import os
from collections import deque
import torch
from helper import plot
# from main import Game
import random
from model import Linear_QNet, QTrainer
from object_handler import ObjectHandler

class Agent:
    def __init__(self, game):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(508, 512, 4)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.player = game.player

        self.action_space = {
            0: [],  # No action
            1: ['F'],  # Move Forward
            # 2: ['B'],  # Move Backward
            # 3: ['L'],  # Move Left
            # 4: ['R'],  # Move Right
            2: ['RL'],  # Rotate Left
            3: ['RR'],  # Rotate Right
            # 3: ['S'],  # Shoot
            # 8: ['F', 'RL'],  # Move Forward and Rotate Left
            # 9: ['F', 'RR'],  # Move Forward and Rotate Right
        }


    def get_state(self, game):
        player = game.player
        state = [
            player.x,  # Player X position
            player.y,  # Player Y position
            player.angle,  # Player angle
            player.health,  # Player health
        ]
        if player.x < 0 or player.y < 0 or player.x > 5 or player.y > 9:
            game.new_game()

        
        # Include NPC information
        for npc in game.object_handler.npc_list:  # Assuming you have a list of NPCs in your game object
            if npc.alive:
                state.extend([npc.x, npc.y, npc.health, 1])  # NPC's position, health, and alive status
            else:
                state.extend([0, 0, 0, 0])  # If NPC is not alive, you might choose to include zeros or some other placeholder

        state.extend(game.raycasting.get_state_from_raycasting())

        return state

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        # states, actions, rewards, next_states, dones = zip(*mini_sample)
        # self.trainer.train_step(states, actions, rewards, next_states, dones)

        for memory in mini_sample:
            states, actions, rewards, next_states, dones = memory
            self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)


    def get_action(self, state):
        self.epsilon = 50 - self.n_games  # Adjust epsilon as needed
        if random.randint(0, 200) < self.epsilon:
            # Exploration: Random action
            action = random.randint(0, len(self.action_space) - 1)
        else:
            # Exploitation: Choose best action based on model prediction
            state_tensor = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state_tensor)
            action = torch.argmax(prediction).item()
            
        return action

# def train():
#     plot_scores = []
#     plot_mean_scores = []
#     total_score = 0
#     record = 0
#     game = Game()
#     print("HIIIIIIII")
#     agent = Agent(game)
#     print("HIIIIIIII")
        
#     game.run()
#     print("HIIIIIIII")
#     while True:
#         # get old state
#         state_old = agent.get_state(game)

#         # get move
#         final_move = agent.get_action(state_old)

#         # perform move and get new state
#         reward, done, score = game.player.play_step(final_move)
#         state_new = agent.get_state(game)

#         # train short memory
#         agent.train_short_memory(state_old, final_move, reward, state_new, done)

#         # remember
#         agent.remember(state_old, final_move, reward, state_new, done)

#         if done:
#             # train long memory, plot result
#             game.new_game()
#             agent.n_games += 1
#             agent.train_long_memory()

#             if score > record:
#                 record = score
#                 agent.model.save()

#             print('Game', agent.n_games, 'Score', score, 'Record:', record)

#             plot_scores.append(score)
#             total_score += score
#             mean_score = total_score / agent.n_games
#             plot_mean_scores.append(mean_score)
#             plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train()