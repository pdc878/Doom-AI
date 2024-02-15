from sprite_object import *
from npc import *



class ObjectHandler:
    def __init__(self, game):
        self.game = game
        self.sprite_list = []
        self.npc_list = []
        self.npc_sprite_path = 'resources/sprites/npc/'
        self.static_sprite_path = 'resources/sprites/static_sprites/'
        self.animated_sprite_path = 'resources/sprites/animated_sprites/'
        add_sprite = self.add_sprite
        add_npc = self.add_npc
        self.npc_positions = {}

        #add_sprite(SpriteObject(game))
        #add_sprite(AnimatedSprite(game))
        

        add_npc(NPC(game, pos=(1.5, 6)))
        # add_npc(NPC(game, pos=(4.5, 2.5)))
        # add_npc(NPC(game, pos=(2.5, 3.5)))
        # add_npc(NPC(game, pos=(2.5, 5.5)))
        

    def update(self):
        self.npc_positions = {npc.map_pos for npc in self.npc_list if npc.alive}
        [sprite.update() for sprite in self.sprite_list]
        [npc.update() for npc in self.npc_list]
        self.check_win()

    def check_win(self):
        if not len(self.npc_positions):
            self.game.object_renderer.win()
            self.game.player.done = True
            pg.display.flip()
            pg.time.delay(1500)
            #self.game.new_game()

    def add_npc(self, npc):
        self.npc_list.append(npc)

    def add_sprite(self, sprite):
        self.sprite_list.append(sprite)