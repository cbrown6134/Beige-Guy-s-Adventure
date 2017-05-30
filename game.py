#!/usr/bin/env python3

import json
import pygame
import sys

pygame.mixer.pre_init()
pygame.init()

# Window settings
TITLE = "Beige Guy's Adventure"   
WIDTH = 1088
HEIGHT = 640
FPS = 60
GRID_SIZE = 64

# Options
sound_on = True

# Controls
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT
JUMP = pygame.K_SPACE
JUMP_2 = pygame.K_UP
RUN = pygame.K_x
PAUSE = pygame.K_p

# Levels
levels = ["levels/world-1.json",
          "levels/world-2.json",
          "levels/world-3.json",
          "levels/world-4.json"]

# Colors
TRANSPARENT = (0, 0, 0, 0)
DARK_BLUE = (16, 86, 103)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fonts
FONT_SM = pygame.font.Font("assets/fonts/YanoneKaffeesatz-Regular.ttf", 32)
FONT_MD = pygame.font.Font("assets/fonts/YanoneKaffeesatz-Regular.ttf", 64)
FONT_LG = pygame.font.Font("assets/fonts/LoveYaLikeASister.ttf", 72)

# Helper functions
def load_image(file_path, width=GRID_SIZE, height=GRID_SIZE):
    img = pygame.image.load(file_path)
    img = pygame.transform.scale(img, (width, height))

    return img

def play_sound(sound, loops=0, maxtime=0, fade_ms=0):
    if sound_on:
        if maxtime == 0:
            sound.play(loops, maxtime, fade_ms)
        else:
            sound.play(loops, maxtime, fade_ms)

def play_music():
    if sound_on:
        pygame.mixer.music.play(-1)

# Images
hero_walk1 = load_image("assets/character/alienBeige_walk1.png")
hero_walk2 = load_image("assets/character/alienBeige_walk2.png")
hero_jump = load_image("assets/character/alienBeige_jump.png")
hero_idle = load_image("assets/character/alienBeige_stand.png")
hero_images = {"run": [hero_walk1, hero_walk2],
               "jump": hero_jump,
               "idle": hero_idle}

block_images = {"SL": load_image("assets/tiles/snowLeft.png"),
                "SMT": load_image("assets/tiles/snowMid_top.png"),
                "SR": load_image("assets/tiles/snowRight.png"),
                "SCR": load_image("assets/tiles/snowCliff_right.png"),
                "SCL": load_image("assets/tiles/snowCliff_left.png"),
                "ST": load_image("assets/tiles/snow_top.png"),
                "SC": load_image("assets/tiles/snowCenter.png"),
                "SF": load_image("assets/tiles/snow_float.png"),
                "SP": load_image("assets/tiles/special.png"),
                "GL": load_image("assets/tiles/grassLeft.png"),
                "GMT": load_image("assets/tiles/grassMid_top.png"),
                "GR": load_image("assets/tiles/grassRight.png"),
                "GCR": load_image("assets/tiles/grassCliff_right.png"),
                "GCL": load_image("assets/tiles/grassCliff_left.png"),
                "GT": load_image("assets/tiles/grass_top.png"),
                "GC": load_image("assets/tiles/grassCenter.png"),
                "GF": load_image("assets/tiles/grass_float.png"),
                "ML": load_image("assets/tiles/metalLeft.png"),
                "MMT": load_image("assets/tiles/metalMid_top.png"),
                "MR": load_image("assets/tiles/metalRight.png"),
                "MCR": load_image("assets/tiles/metalCliff_right.png"),
                "MCL": load_image("assets/tiles/metalCliff_left.png"),
                "MT": load_image("assets/tiles/metal_top.png"),
                "MC": load_image("assets/tiles/metalCenter.png"),
                "MF": load_image("assets/tiles/metal_float.png"),
                "PCL": load_image("assets/tiles/planetCliff_left.png"),
                "PCR": load_image("assets/tiles/planetCliff_right.png"),
                "PMT": load_image("assets/tiles/planetMid.png"),
                "PC": load_image("assets/tiles/planetCenter.png")}

coin_img = load_image("assets/coins/coinGold.png")
gem_img = load_image("assets/coins/gemBlue.png")
heart_img = load_image("assets/items/hudHeart_full.png")
oneup_img = load_image("assets/items/hudPlayer_beige.png")
reducedspeed_img = load_image("assets/items/hudPlayer_blue.png")
exit_img = load_image("assets/items/signExit.png")
lives_img = load_image("assets/items/life.png", 50, 50)
star_img = load_image("assets/items/star.png")

slimeBlock_img1 = load_image("assets/enemies/slimeBlock.png")
slimeBlock_img2 = load_image("assets/enemies/slimeBlock_move.png")
slimeBlock_images = [slimeBlock_img1, slimeBlock_img2]

snail_walk1 = load_image("assets/enemies/snail.png")
snail_walk2 = load_image("assets/enemies/snail_move.png")
snail_images = [snail_walk1, snail_walk2]

bee_fly1 = load_image("assets/enemies/bee.png")
bee_fly2 = load_image("assets/enemies/bee_move.png")
bee_images = [bee_fly1, bee_fly2]

# Sounds
JUMP_SOUND = pygame.mixer.Sound("assets/sounds/jump.wav")
COIN_SOUND = pygame.mixer.Sound("assets/sounds/pickup_coin.wav")
POWERUP_SOUND = pygame.mixer.Sound("assets/sounds/powerup.wav")
HURT_SOUND = pygame.mixer.Sound("assets/sounds/hurt.ogg")
DIE_SOUND = pygame.mixer.Sound("assets/sounds/death.wav")
LEVELUP_SOUND = pygame.mixer.Sound("assets/sounds/level_up.wav")
GAMEOVER_SOUND = pygame.mixer.Sound("assets/sounds/game_over.wav")

class Entity(pygame.sprite.Sprite):

    def __init__(self, x, y, image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vy = 0
        self.vx = 0

    def apply_gravity(self, level):
        self.vy += level.gravity
        self.vy = min(self.vy, level.terminal_velocity)

class Block(Entity):

    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Character(Entity):

    def __init__(self, images):
        super().__init__(0, 0, images['idle'])

        self.image_idle = images['idle']
        self.images_run_right = images['run']
        self.images_run_left = [pygame.transform.flip(img, 1, 0) for img in self.images_run_right]
        self.image_jump_right = images['jump']
        self.image_jump_left = pygame.transform.flip(self.image_jump_right, 1, 0)

        self.running_images = self.images_run_right
        self.image_index = 0
        self.steps = 0

        self.speed = 6
        self.speed_timer = 0
        self.jump_power = 22

        self.vx = 0
        self.vy = 0
        self.facing_right = True
        self.on_ground = True

        self.score = 0
        self.lives = 3
        self.hearts = 3
        self.max_hearts = 3
        self.invincibility = 0


    def move_left(self):
        if self.speed_timer > 0:
            self.vx = -self.speed / 2
        else:
            self.vx = -self.speed
            
        self.facing_right = False

    def move_right(self):
        if self.speed_timer > 0:
            self.vx = self.speed / 2
        else:
            self.vx = self.speed
            
        self.facing_right = True

    def stop(self):
        self.vx = 0

    def jump(self, blocks):
        self.rect.y += 1

        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        if len(hit_list) > 0:
            self.vy = -1 * self.jump_power
            play_sound(JUMP_SOUND)

        self.rect.y -= 1

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > level.width:
            self.rect.right = level.width

        if self.rect.y > 640:
            self.respawn(level)
            self.score = 0
            self.lives -= 1
            level.reset()

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx = 0
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.vx = 0

        self.on_ground = False
        self.rect.y += self.vy + 1
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def process_coins(self, coins):
        hit_list = pygame.sprite.spritecollide(self, coins, True)

        for coin in hit_list:
            play_sound(COIN_SOUND)
            self.score += coin.value

            if self.score >= 200:
                self.max_hearts += 1
                self.score = 0

    def process_gems(self, gems):
        hit_list = pygame.sprite.spritecollide(self, gems, True)

        for gem in hit_list:
            play_sound(COIN_SOUND)
            self.score += gem.value

            if self.score >= 200:
                self.max_hearts += 1
                self.score = 0

    def process_enemies(self, enemies):
        hit_list = pygame.sprite.spritecollide(self, enemies, False)
        if self.invincibility == 0:
            for enemy in hit_list:
                if self.vy > 0:
                    enemy.kill()
                    self.vy -= 30
                    play_sound(HURT_SOUND)
                    self.score += enemy.point_value
                else:
                    play_sound(HURT_SOUND)
                    self.hearts -= 1
                    self.invincibility = int(0.75 * FPS)
        

    def process_powerups(self, powerups):
        hit_list = pygame.sprite.spritecollide(self, powerups, True)

        for p in hit_list:
            play_sound(POWERUP_SOUND)
            p.apply(self)
            self.score += 1

            if self.score >= 200:
                self.max_hearts += 1
                self.score = 0

    def check_exit(self, level):
        hit_list = pygame.sprite.spritecollide(self, level.exit, False)

        if len(hit_list) > 0:
            level.completed = True
            play_sound(LEVELUP_SOUND)

    def set_image(self):
        if self.on_ground:
            if self.vx != 0:
                if self.facing_right:
                    self.running_images = self.images_run_right
                else:
                    self.running_images = self.images_run_left

                self.steps = (self.steps + 1) % self.speed # Works well with 2 images, try lower number if more frames are in animation

                if self.steps == 0:
                    self.image_index = (self.image_index + 1) % len(self.running_images)
                    self.image = self.running_images[self.image_index]
            else:
                self.image = self.image_idle
        else:
            if self.facing_right:
                self.image = self.image_jump_right
            else:
                self.image = self.image_jump_left

    def die(self):
        self.lives -= 1
        self.score = 0

        if self.lives > 0:
            play_sound(DIE_SOUND)
        else:
            play_sound(GAMEOVER_SOUND)

    def respawn(self, level):
        self.rect.x = level.start_x
        self.rect.y = level.start_y
        self.hearts = self.max_hearts
        self.invincibility = 0
        self.speed = 6
        self.speed_timer = 0

    def update(self, level):
        self.process_enemies(level.enemies)
        self.apply_gravity(level)
        self.move_and_process_blocks(level.blocks)
        self.check_world_boundaries(level)
        self.set_image()

        if self.hearts > 0:
            self.process_coins(level.coins)
            self.process_gems(level.gems)
            self.process_powerups(level.powerups)
            self.check_exit(level)

            if self.invincibility > 0:
                self.invincibility -= 1

            if self.speed_timer > 0:
                self.speed_timer -= 1
        else:
            self.die()

class Coin(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.value = 5

class Gem(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.value = 10 

class Enemy(Entity):
    def __init__(self, x, y, images):
        super().__init__(x, y, images[0])

        self.images_left = images
        self.images_right = [pygame.transform.flip(img, 1, 0) for img in images]
        self.current_images = self.images_left
        self.image_index = 0
        self.steps = 0

    def reverse(self):
        self.vx *= -1

        if self.vx < 0:
            self.current_images = self.images_left
        else:
            self.current_images = self.images_right

        self.image = self.current_images[self.image_index]

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
            self.reverse()
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.reverse()

        if self.rect.y > 640:
            self.kill()
            

    def move_and_process_blocks(self):
        pass

    def set_images(self):
        if self.steps == 0:
            self.image = self.current_images[self.image_index]
            self.image_index = (self.image_index + 1) % len(self.current_images)

        self.steps = (self.steps + 1) % 20 # Nothing significant about 20. It just seems to work okay.

    def is_near(self, hero):
        return abs(self.rect.x - hero.rect.x) < 2 * WIDTH

    def update(self, level, hero):
        if self.is_near(hero):
            self.apply_gravity(level)
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)
            self.set_images()



    def reset(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.vx = self.start_vx
        self.vy = self.start_vy
        self.image = self.images_left[0]
        self.steps = 0

class Snail(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.start_x = x
        self.start_y = y
        self.start_vx = -2
        self.start_vy = 0

        self.vx = self.start_vx
        self.vy = self.start_vy

        self.point_value = 5

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy + 1
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

class slimeBlock(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.start_x = x
        self.start_y = y
        self.start_vx = -2
        self.start_vy = 0

        self.vx = self.start_vx
        self.vy = self.start_vy

        self.point_value = 7

    def move_and_process_blocks(self, blocks):
        reverse = False

        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy + 1
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        reverse = True

        for block in hit_list:
            if self.vy >= 0:
                self.rect.bottom = block.rect.top
                self.vy = 0

                if self.vx > 0 and self.rect.right <= block.rect.right:
                    reverse = False

                elif self.vx < 0 and self.rect.left >= block.rect.left:
                    reverse = False

            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

        if reverse:
            self.reverse()

class Bee(Enemy):
    def __init__(self, x, y, images):
        super().__init__(x, y, images)

        self.start_x = x
        self.start_y = y
        self.start_vx = -2
        self.start_vy = 0

        self.vx = self.start_vx
        self.vy = self.start_vy

        self.point_value = 10

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy 
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def update(self, level, hero):
        if self.is_near(hero):
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)
            self.set_images()

class OneUp(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.lives += 1

class Heart(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.hearts += 1
        character.hearts = max(character.hearts, character.max_hearts)

        if character.hearts > character.max_hearts:
            character.hearts = character.max_hearts

class ReducedSpeed(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.speed_timer = 1300

class Invincibility(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.invincibility = int(10 * FPS)
        
class Exit(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Level():

    def __init__(self, file_path):
        self.starting_blocks = []
        self.starting_enemies = []
        self.starting_coins = []
        self.starting_gems = []
        self.starting_powerups = []
        self.starting_exit = []

        self.blocks = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.gems = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.exit = pygame.sprite.Group()

        self.active_sprites = pygame.sprite.Group()
        self.inactive_sprites = pygame.sprite.Group()

        with open(file_path, 'r') as f:
            data = f.read()

        map_data = json.loads(data)

        self.width = map_data['width'] * GRID_SIZE
        self.height = map_data['height'] * GRID_SIZE

        self.start_x = map_data['start'][0] * GRID_SIZE
        self.start_y = map_data['start'][1] * GRID_SIZE

        for item in map_data['blocks']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            img = block_images[item[2]]
            self.starting_blocks.append(Block(x, y, img))

        for item in map_data['snails']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_enemies.append(Snail(x, y, snail_images))

        for item in map_data['slimeBlocks']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_enemies.append(slimeBlock(x, y, slimeBlock_images))

        for item in map_data['bees']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_enemies.append(Bee(x, y, bee_images))

        for item in map_data['coins']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_coins.append(Coin(x, y, coin_img))

        for item in map_data['gems']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_gems.append(Gem(x, y, gem_img))

        for item in map_data['oneups']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(OneUp(x, y, oneup_img))

        for item in map_data['reducedspeed']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(ReducedSpeed(x, y, reducedspeed_img))

        for item in map_data['stars']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(Invincibility(x, y, star_img))

        for item in map_data['hearts']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.starting_powerups.append(Heart(x, y, heart_img))

        for item in map_data['exit']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE

            self.starting_exit.append(Exit(x, y, exit_img))

        self.background_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.scenery_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.inactive_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)
        self.active_layer = pygame.Surface([self.width, self.height], pygame.SRCALPHA, 32)

        if map_data['background-color'] != "":
            self.background_layer.fill(map_data['background-color'])

        if map_data['background-img'] != "":
            background_img = pygame.image.load(map_data['background-img'])

            if map_data['background-fill-y']:
                h = background_img.get_height()
                w = int(background_img.get_width() * HEIGHT / h)
                background_img = pygame.transform.scale(background_img, (w, HEIGHT))

            if "top" in map_data['background-position']:
                start_y = 0
            elif "bottom" in map_data['background-position']:
                start_y = self.height - background_img.get_height()

            if map_data['background-repeat-x']:
                for x in range(0, self.width, background_img.get_width()):
                    self.background_layer.blit(background_img, [x, start_y])
            else:
                self.background_layer.blit(background_img, [0, start_y])

        if map_data['scenery-img'] != "":
            scenery_img = pygame.image.load(map_data['scenery-img'])

            if map_data['scenery-fill-y']:
                h = scenery_img.get_height()
                w = int(scenery_img.get_width() * HEIGHT / h)
                scenery_img = pygame.transform.scale(scenery_img, (w, HEIGHT))

            if "top" in map_data['scenery-position']:
                start_y = 0
            elif "bottom" in map_data['scenery-position']:
                start_y = self.height - scenery_img.get_height()

            if map_data['scenery-repeat-x']:
                for x in range(0, self.width, scenery_img.get_width()):
                    self.scenery_layer.blit(scenery_img, [x, start_y])
            else:
                self.scenery_layer.blit(scenery_img, [0, start_y])

        pygame.mixer.music.load(map_data['music'])

        self.gravity = map_data['gravity']
        self.terminal_velocity = map_data['terminal-velocity']

        self.completed = False

        self.blocks.add(self.starting_blocks)
        self.enemies.add(self.starting_enemies)
        self.coins.add(self.starting_coins)
        self.gems.add(self.starting_gems)
        self.powerups.add(self.starting_powerups)
        self.exit.add(self.starting_exit)

        self.active_sprites.add(self.coins, self.gems, self.enemies, self.powerups)
        self.inactive_sprites.add(self.blocks, self.exit)

        self.inactive_sprites.draw(self.inactive_layer)

    def reset(self):
        self.enemies.add(self.starting_enemies)
        self.coins.add(self.starting_coins)
        self.gems.add(self.starting_gems)
        self.powerups.add(self.starting_powerups)

        self.active_sprites.add(self.coins, self.gems, self.enemies, self.powerups)

        for e in self.enemies:
            e.reset()

class Game():

    SPLASH = 0
    START = 1
    PLAYING = 2
    PAUSED = 3
    LEVEL_COMPLETED = 4
    GAME_OVER = 5
    VICTORY = 6

    def __init__(self):
        self.window = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.done = False

        self.reset()

    def start(self):
        self.level = Level(levels[self.current_level])
        self.level.reset()
        self.hero.respawn(self.level)

    def advance(self):
        self.current_level += 1
        self.start()
        self.stage = Game.START

    def reset(self):
        self.hero = Character(hero_images)
        self.current_level = 0
        self.start()
        self.stage = Game.SPLASH

    def display_splash(self, surface):
        line1 = FONT_LG.render(TITLE, 1, DARK_BLUE)
        line2 = FONT_SM.render("Press any key to start.", 1, BLACK)
        img = pygame.image.load("assets/backgrounds/blue_land_splash.png")
        beige_guy = pygame.image.load("assets/character/alienBiege_front_splash.png")

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;

        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;

        surface.blit(img, (0, 0))
        surface.blit(beige_guy, (493,432))
        surface.blit(line1, (x1, y1))
        surface.blit(line2, (x2, y2))

    def display_message(self, surface, primary_text, secondary_text):
        line1 = FONT_MD.render(primary_text, 1, WHITE)
        line2 = FONT_SM.render(secondary_text, 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;

        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;

        #pygame.draw.rect(surface, BLACK, [150, 150, 770, 200])
        surface.blit(line1, (x1, y1))
        surface.blit(line2, (x2, y2))

    def display_stats(self, surface):
        hearts_text = FONT_SM.render("Hearts: " + str(self.hero.hearts) + "/" + str(self.hero.max_hearts), 1, WHITE)
        lives_text = FONT_SM.render("x " + str(self.hero.lives), 1, WHITE)
        score_text = FONT_SM.render("Score: " + str(self.hero.score), 1, WHITE)
        level_text = FONT_SM.render("World " + str(self.current_level + 1), 1, WHITE)
        pause_text = FONT_SM.render("Paused", 1, WHITE)

        surface.blit(lives_img, (32, 96))
        surface.blit(score_text, (WIDTH - score_text.get_width() - 32, 32))
        surface.blit(hearts_text, (32, 64))
        surface.blit(lives_text, (78, 98))
        surface.blit(level_text, (32, 32))

        if self.stage == Game.PAUSED:
            surface.blit(pause_text, (WIDTH - score_text.get_width() - 32, 64))

        if self.stage == Game.VICTORY or self.stage == Game.GAME_OVER:
            credits_text = FONT_MD.render("Credits", 1, WHITE)
            credits_text_2 = FONT_SM.render("Art: Kenney", 1, WHITE)
            credits_text_3 = FONT_SM.render("Sounds & Music: Open Game Art", 1, WHITE)
            credits_text_4 = FONT_SM.render("Game Template: Jon Cooper", 1, WHITE)
            credits_text_5 = FONT_SM.render("Everything Else: Colby Brown", 1, WHITE)

            
            pygame.draw.rect(surface, BLACK, [0, 0, 1088, 640])
            surface.blit(credits_text, (460, 300))
            surface.blit(credits_text_2, (420, 370))
            surface.blit(credits_text_3, (420, 400))
            surface.blit(credits_text_4, (420, 430))
            surface.blit(credits_text_5, (420, 460))

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

            elif event.type == pygame.KEYDOWN:
                if self.stage == Game.SPLASH or self.stage == Game.START:
                    self.stage = Game.PLAYING
                    play_music()

                elif self.stage == Game.PLAYING:
                    if event.key == JUMP or event.key == JUMP_2:
                        self.hero.jump(self.level.blocks)
                    if event.key == PAUSE:
                        self.stage = Game.PAUSED

                elif self.stage == Game.PAUSED:
                    if event.key == PAUSE:
                        self.stage = Game.PLAYING

                elif self.stage == Game.LEVEL_COMPLETED:
                    self.advance()

                elif self.stage == Game.VICTORY or self.stage == Game.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset()

        pressed = pygame.key.get_pressed()

        if self.stage == Game.PLAYING:
            if pressed[LEFT]:
                self.hero.move_left()
            elif pressed[RIGHT]:
                self.hero.move_right()
            else:
                self.hero.stop()


    def update(self):
        if self.stage == Game.PLAYING:
            self.hero.update(self.level)
            self.level.enemies.update(self.level, self.hero)

        if self.level.completed:
            if self.current_level < len(levels) - 1:
                self.stage = Game.LEVEL_COMPLETED
            else:
                self.stage = Game.VICTORY
            pygame.mixer.music.stop()

        elif self.hero.lives == 0:
            self.stage = Game.GAME_OVER
            pygame.mixer.music.stop()

        elif self.hero.hearts == 0:
            self.level.reset()
            self.hero.respawn(self.level)

    def calculate_offset(self):
        x = -1 * self.hero.rect.centerx + WIDTH / 2

        if self.hero.rect.centerx < WIDTH / 2:
            x = 0
        elif self.hero.rect.centerx > self.level.width - WIDTH / 2:
            x = -1 * self.level.width + WIDTH

        return x, 0

    def draw(self):
        offset_x, offset_y = self.calculate_offset()

        self.level.active_layer.fill(TRANSPARENT)
        self.level.active_sprites.draw(self.level.active_layer)

        if self.hero.invincibility % 3 < 2:
            self.level.active_layer.blit(self.hero.image, [self.hero.rect.x, self.hero.rect.y])

        self.window.blit(self.level.background_layer, [offset_x / 3, offset_y])
        self.window.blit(self.level.scenery_layer, [offset_x / 2, offset_y])
        self.window.blit(self.level.inactive_layer, [offset_x, offset_y])
        self.window.blit(self.level.active_layer, [offset_x, offset_y])

        self.display_stats(self.window)

        if self.stage == Game.SPLASH:
            self.display_splash(self.window)
        elif self.stage == Game.START:
            self.display_message(self.window, "Ready?!!!", "Press any key to start.")
        elif self.stage == Game.PAUSED:
            pass
        elif self.stage == Game.LEVEL_COMPLETED:
            self.display_message(self.window, "Level Complete", "Press any key to continue.")
        elif self.stage == Game.VICTORY:
            self.display_message(self.window, "You Win!", "Press 'R' to restart.")
        elif self.stage == Game.GAME_OVER:
            self.display_message(self.window, "Game Over", "Press 'R' to restart.")

        pygame.display.flip()

    def loop(self):
        while not self.done:
            self.process_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.start()
    game.loop()
    pygame.quit()
    sys.exit()
