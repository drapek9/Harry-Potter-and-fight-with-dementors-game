import pygame
import random

# Inicializace hry
pygame.init()

width = 1200
height = 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Bitva s mozkomory")

# Fps & clock
fps = 60
clock = pygame.time.Clock()


# Classy
class Game:
    def __init__(self, our_player, group_of_mozkomors):
        self.score = 0
        self.round_number = 0

        self.round_time = 0
        self.slow_down_cycle = 0

        self.our_player = our_player
        self.group_of_mozkomors = group_of_mozkomors

        # Hudba v pozadí
        pygame.mixer.music.load("media/bg-music-hp.wav")
        pygame.mixer.music.play(-1, 0.0)

        # fonty
        self.potter_font = pygame.font.Font("fonts/Harry.ttf", 24)
        self.potter_font_2 = pygame.font.Font("fonts/Harry.ttf", 50)

        # Obrázek na pozadí
        self.background_image = pygame.image.load("img/bg-dementors.png")
        self.background_image_rect = self.background_image.get_rect()
        self.background_image_rect.topleft = (0, 0)

        # typy mozkomorů: 0 = modrý, 1 = zelený, 2 = růžový, 3 = žlutý
        blue_image = pygame.image.load("img/mozkomor-modry.png")
        green_image = pygame.image.load("img/mozkomor-zeleny.png")
        purple_image = pygame.image.load("img/mozkomor-ruzovy.png")
        yelllow_image = pygame.image.load("img/mozkomor-zluty.png")
        self.mozkomor_images = [blue_image, green_image, purple_image, yelllow_image]

        self.mozkomor_catch_type = random.randint(0, 3)
        self.mozkomor_catch_image = self.mozkomor_images[self.mozkomor_catch_type]
        self.mozkomor_catch_image_rect = self.mozkomor_catch_image.get_rect()
        self.mozkomor_catch_image_rect.centerx = width//2
        self.mozkomor_catch_image_rect.top = 25

    # Kód, který je volán stále dokola
    def update(self):
        self.slow_down_cycle += 1
        if self.slow_down_cycle % fps == 0:
            self.round_time += 1

        # kontrola kolize
        self.check_collisions()

    # Vykresluje vše ve hře - texty, hledaného mozkomora, tapetu
    def draw(self):
        dark_yellow = pygame.Color("#938f0c")
        colors = ["blue", "green", "purple", "yellow"]

        catch_text = self.potter_font.render("Catch this mozkomor:", True, dark_yellow)
        catch_text_rect = catch_text.get_rect()
        catch_text_rect.centerx = width//2
        catch_text_rect.top = 5

        score_text = self.potter_font.render(f"Score: {self.score}", True, dark_yellow)
        score_text_rect = score_text.get_rect()
        score_text_rect.topleft = (10, 5)

        lives_text = self.potter_font.render(f"Lives: {self.our_player.lives}", True, dark_yellow)
        lives_text_rect = lives_text.get_rect()
        lives_text_rect.topleft = (10, 35)

        round_text = self.potter_font.render(f"Round: {self.round_number}", True, dark_yellow)
        round_text_rect = round_text.get_rect()
        round_text_rect.topleft = (10, 65)

        time_text = self.potter_font.render(f"Time: {self.round_time}", True, dark_yellow)
        time_text_rect = time_text.get_rect()
        time_text_rect.topright = (width - 10, 5)

        back_save_zone_text = self.potter_font.render(f"Save zone: {self.our_player.enter_safe_zone}", True, dark_yellow)
        back_save_zone_text_rect = back_save_zone_text.get_rect()
        back_save_zone_text_rect.topright = (width - 10, 35)

        # Blitting
        screen.blit(catch_text, catch_text_rect)
        screen.blit(score_text, score_text_rect)
        screen.blit(lives_text, lives_text_rect)
        screen.blit(round_text, round_text_rect)
        screen.blit(time_text, time_text_rect)
        screen.blit(back_save_zone_text, back_save_zone_text_rect)
        screen.blit(self.mozkomor_catch_image, self.mozkomor_catch_image_rect)

        # Vykreslení rectenglu
        pygame.draw.rect(screen, colors[self.mozkomor_catch_type], (0, 100, width, height - 200), 4)

    # Kontroluje kolizi harryho s mozkomorem
    def check_collisions(self):
        color_mozkomors = 0
        # s jakým mozkomorem jsme se srazili
        collided_mozkomor = pygame.sprite.spritecollideany(self.our_player, self.group_of_mozkomors)
        if collided_mozkomor:
            # Srazili jsme mozkomora
            if collided_mozkomor.type == self.mozkomor_catch_type:
                self.score += 1 * self.round_number
                collided_mozkomor.remove(self.group_of_mozkomors)
                self.our_player.catch_sound.play()
                # Je více stejných mozkomorů k chycení?
                # for one_mozkomor in self.group_of_mozkomors:
                #     if one_mozkomor.type == collided_mozkomor.type:
                #         color_mozkomors += 1

                # if color_mozkomors > 0:
                #     pass
                if self.group_of_mozkomors:
                    self.choose_new_target()
                else:
                    self.our_player.reset()
                    self.start_new_round()

            else:
                self.our_player.lives -= 1
                self.our_player.wrong_sound.play()
                self.our_player.reset()
                if self.our_player.lives <= 0:
                    self.pause_game(f"Achived score: {self.score}", "Press space to continue")
                    self.reset_game()

    # Zahájí nové kolo - s větším počtem mozkomorů v herní ploše
    def start_new_round(self):
        # Při dokončení kola poskytneme bonus podle toho, jak rychle hráč kolo dokončí: dříve = více bodů
        self.score += int(100 * (self.round_number / (1 + self.round_time)))

        # Resetujeme hodnoty
        self.round_time = 0
        self.slow_down_cycle = 0
        self.our_player.enter_safe_zone += 1
        self.round_number += 1

        # Vyčistíme skupinu mozkomorů, abyychom mohli skupinu nasplnit novými mozkomory
        for one_mozkomor in self.group_of_mozkomors:
            self.group_of_mozkomors.remove(one_mozkomor)

        for _ in range(self.round_number):
            for number in range(4):
                self.group_of_mozkomors.add(Mozkomor(random.randint(0, width - 64), random.randint(100, height - 164),
                self.mozkomor_images[number], number))

        # vybíráme nového mozkomora
        self.choose_new_target()


    # Výběr nového mozkomora, kterého máme chytit
    def choose_new_target(self):
        new_mozkomor_to_catch = random.choice(self.group_of_mozkomors.sprites())
        self.mozkomor_catch_type = new_mozkomor_to_catch.type
        self.mozkomor_catch_image = new_mozkomor_to_catch.image

    # Pozastavení hry - pauza před zahájením nové hry, na začátku při spuštění
    def pause_game(self, main_text, subheading_text):

        global lets_continue

        dark_yellow = pygame.Color("#938f0c")

        main_text_create = self.potter_font_2.render(main_text, True, dark_yellow)
        main_text_create_rect = main_text_create.get_rect()
        main_text_create_rect.center = (width//2, height//2-20)

        subheading_text_create = self.potter_font_2.render(subheading_text, True, dark_yellow)
        subheading_text_create_rect = subheading_text_create.get_rect()
        subheading_text_create_rect.center = (width//2, height//2 + 40)

        screen.fill("black")
        screen.blit(main_text_create, main_text_create_rect)
        screen.blit(subheading_text_create, subheading_text_create_rect)
        pygame.mixer.music.pause()
        pygame.display.update()
        paused = True
        while paused:
            for one_event in pygame.event.get():
                if one_event.type == pygame.QUIT:
                    paused = False
                    lets_continue = False

                elif one_event.type == pygame.KEYDOWN:
                    if one_event.key == pygame.K_SPACE:
                        pygame.mixer.music.unpause()
                        paused = False

    # Resetuje hru do výchozího stavu
    def reset_game(self):
        self.score = 0
        self.round_number = 0
        self.our_player.lives = 5
        self.our_player.enter_safe_zone = 2
        self.start_new_round()
        pygame.mixer.music.play(-1, 0.0)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("img/potter-icon.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = width//2
        self.rect.bottom = height - 18

        self.lives = 5
        self.enter_safe_zone = 2
        self.speed = 8

        self.catch_sound = pygame.mixer.Sound("media/expecto-patronum.mp3")
        self.catch_sound.set_volume(0.1)

        self.wrong_sound = pygame.mixer.Sound("media/wrong.wav")
        self.wrong_sound.set_volume(0.1)

    # Kód, který je volán stále dokola
    def update(self):
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_w] or keys[pygame.K_UP]) and self.rect.top > 100:
            self.rect.y -= self.speed
        elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and self.rect.bottom < height - 100:
            self.rect.y += self.speed
        if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.rect.right < width:
            self.rect.x += self.speed
        elif (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.rect.left > 0:
            self.rect.x -= self.speed

    # Návrat do bezpečné zóny dole v herní ploše
    def back_to_save_zone(self):
        if self.enter_safe_zone > 0:
            self.rect.bottom = height - 18
            self.enter_safe_zone -= 1

    # Vrací hráče zpět na výchozí pozici - doprostřed bezpečné zóny
    def reset(self):
        self.rect.centerx = width//2
        self.rect.bottom = height - 18


class Mozkomor(pygame.sprite.Sprite):
    def __init__(self, x, y, file_name, mozkomor_type):
        super().__init__()
        self.image = file_name
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # typy mozkomorů: 0 = modrý, 1 = zelený, 2 = růžový, 3 = žlutý
        self.type = mozkomor_type

        # Nastavení náhodného směru mozkomora
        self.x = random.choice([-1, 1])
        self.y = random.choice([-1, 1])
        self.speed = random.randint(1, 5)

    # Kód, který je volán stále do kola
    def update(self):
        # pohyb mozkomora
        self.rect.x += self.x * self.speed
        self.rect.y += self.y * self.speed

        # Odraz mozkomora
        if self.rect.top < 100 or self.rect.bottom > height - 100:
            self.y = -1 * self.y
        if self.rect.left < 0 or self.rect.right > width:
            self.x = -1 * self.x


# Skupina mozkomorů
mozkomor_group = pygame.sprite.Group()
# testovací mozkomorové
# type = 0
# for color in ["modry", "zeleny", "ruzovy", "zluty"]:
#     one_mozkomor = Mozkomor(random.randint(0, width - 64), random.randint(100, height - 164), pygame.image.load(f"img/mozkomor-{color}.png"), type)
#     mozkomor_group.add(one_mozkomor)
#     type += 1

# Skupina hráčů
player_group = pygame.sprite.Group()
one_player = Player()
player_group.add(one_player)

# Objekt game
my_game = Game(one_player, mozkomor_group)
my_game.start_new_round()
# cyklus while pro hru
lets_continue = True
my_game.pause_game("Harry Potter and fight with mozkomors", "Press enter for start the game")
while lets_continue:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            lets_continue = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                one_player.back_to_save_zone()

    # fill screen
    # screen.fill("black")
    screen.blit(my_game.background_image, my_game.background_image_rect)

    # update skupiny mozkomorů
    mozkomor_group.draw(screen)
    mozkomor_group.update()

    # update skupiny hráčů
    player_group.draw(screen)
    player_group.update()

    # Update objektu hry
    my_game.update()
    my_game.draw()

    # Update hry
    pygame.display.update()

    # Fps - zpomalení cyklu
    clock.tick(fps)

# Konec hry
pygame.quit()
