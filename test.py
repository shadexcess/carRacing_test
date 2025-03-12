import pygame
import random
import math
from utilities import scale_image
import time
from abc import ABC, abstractmethod
import os
from music import overlay_music_in_loop, stop_music, start_music, next_track, mute_music, stop_sound

pygame.init()

class GameSys:
    def __init__(self):
        self.running = True
        self.aspect_ratio = (1920, 1080)
        self.screen = pygame.display.set_mode(self.aspect_ratio)
        pygame.display.set_caption('Car Racing')
        self.background = pygame.image.load('garage_blur.png')
        self.car = Cars(400, 997, 0, 0, 0, 'car1.png', 'wasd')
        self.bot = Bots(400, 992, 0, 0, 0, [])
        self.menu = Menu(800, 450)
        self.roads = Roads('winter.jpg', 0)
        self.obs = Obstacles(0, 0, 'snowflake.png','banana.png', 'sand.png')
        self.road_contour = pygame.image.load('winter_edge.png')
        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)
        self.countdown_images = [
            pygame.image.load('3.png'),
            scale_image(pygame.image.load('2.png'), 2),
            pygame.image.load('1.png'),
            pygame.image.load('GO.png')
        ]
        self.in_menu = True
        self.score = Score("coin.png")
        self.maps_page = MapsMenu(80, 100, self.score)
        self.cars_page = CarsMenu(90, 100, self.score)
        self.modes_page = ModesMenu(100, 100)
        self.choosing_map = False
        self.choosing_car = False
        self.choosing_mode = False
        self.map_choice = '0'
        self.mode_choice = '0'
        self.car1 = Cars(400, 997, 0, 0.5, 0, 'car5.png', 'wasd')
        self.car2 = Cars(500, 997, 0, 0.5, 0, 'car5.png', 'arrows')
        self.pause_font = pygame.font.Font("D:/CarRacing/AveriaSansLibre-Bold.ttf", 36)
        self.pause_text = self.pause_font.render('Paused', True, (255, 255, 255))
        self.pause_rect = self.pause_text.get_rect(center=(self.aspect_ratio[0]//2 - 15, self.aspect_ratio[1]//2))
        
    def run(self):
        new_game = True
        # Змінна для регулювання кількості кадрів на секунду
        clock = pygame.time.Clock()
        while self.running:
            if new_game:
                self.in_menu = True
                self.show_menu()
                self.menu.countdown(self.countdown_images, self.screen, self.roads, self.car, self.car1, self.car2, self.bot, self.aspect_ratio, self.mode_choice)
                # Після запуску гри встановлюємо newGame у False, щоб запобігти повторному перезапуску
                new_game = False
            self.roads.draw(self.screen)
            self.finish.draw(self.screen)
            self.obs.draw_obstackles(self.screen, self.map_choice)

            if self.mode_choice == 'single':
                self.score.draw_coins(self.screen)
                self.car.draw(self.screen)
                self.car.update_car(self.obs, self.map_choice, self.score)
                self.bot.draw(self.screen)  # Малюємо бота
                # Завершення гри, якщо фініш було перетнуто (пройдено всі кола)
                new_game = self.finish.crossed(self.screen, self.aspect_ratio, self.car, self.bot, self.score)  # self.running = not 
                self.score.draw_score(self.screen)

            else:
                self.car1.draw(self.screen)
                self.car1.update_car(self.obs, self.map_choice, self.score, self.mode_choice)
                self.car2.draw(self.screen)
                self.car2.update_car(self.obs, self.map_choice, self.score, self.mode_choice)
                # Завершення гри, якщо фініш було перетнуто (пройдено всі кола)
                new_game = self.finish.crossed(self.screen, self.aspect_ratio, self.car1, self.car2)  # self.running = not 

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if not self.handle_pause():  # Викликаємо метод паузи
                            new_game = True
                            break  # Якщо handle_pause повернув False, перериваємо цю ітерацію
                    elif event.key == pygame.K_n:
                        next_track()
                    elif event.key == pygame.K_m:
                        mute_music()
            cars = [self.car, self.car1, self.car2]

            for car in cars:
                if car.collide(self.road_contour_mask):
                    car.bounce()

            self.bot.move()
            # Ліміт fps = 500
            clock.tick(500)

        # print(points_str)
        pygame.quit()    

    def show_menu(self):
        while self.in_menu:
            self.screen.blit(self.background, (0, 0))  
            self.menu.draw(self.screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.in_menu = False
                    pygame.quit()
                    exit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.menu.start_rect.collidepoint(event.pos):
                        overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
                        self.in_menu = False
                        self.choosing_mode = True
                        self.show_modes()
                    elif self.menu.options_rect.collidepoint(event.pos):
                        overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
                        self.menu.show_options(self.screen, self.running, self.background)  
                        
                    elif self.menu.rating_btn_rect.collidepoint(event.pos):
                        overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
                        self.menu.show_rating(self.screen, self.running, self.in_menu, self.background)

    # def check_for_menu_click(self, event):
    #     if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    #         if self.menu.menu_back_rect.collidepoint(event.pos):
    #             overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
    #             self.in_menu = True 
    #             self.show_menu() 

    def show_maps(self):
        while self.choosing_map:
            self.screen.blit(self.background, (0, 0))  
            self.maps_page.draw(self.screen)
            # self.menu.draw_menu_button(self.screen)
            pygame.display.update()

            for event in pygame.event.get():
                # self.check_for_menu_click(event)                    
                if event.type == pygame.QUIT:
                    self.running = False
                    self.choosing_map = False
                    pygame.quit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.map_choice = self.maps_page.check_click(event.pos)
                    if self.map_choice:
                        self.choose_maps(self.map_choice)

    def choose_maps(self, map_choice):
        print(f"Selected map: {map_choice}")
        self.roads = Roads(f"{map_choice}.jpg", 0)
        self.choosing_map = False
        if self.mode_choice == 'single':
            self.create_objects_single(map_choice)
        else:
            self.create_objects_doubles(map_choice)

    def show_cars(self):
        if self.mode_choice == 'doubles':
            self.choosing_car = False
            self.choosing_map = True
            self.show_maps()
            
        while self.choosing_car:
            self.screen.blit(self.background, (0, 0))  
            self.cars_page.draw(self.screen)
            # self.menu.draw_menu_button(self.screen)
            pygame.display.update()

            for event in pygame.event.get():
                # self.check_for_menu_click(event)                    
                if event.type == pygame.QUIT:
                    self.running = False
                    self.choosing_car = False
                    pygame.quit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    car_choice = self.cars_page.check_click(event.pos)
                    if car_choice:
                        self.choose_cars(car_choice)

    def choose_cars(self, car_choice):
        print(f"Selected car: {car_choice}")
        self.choosing_car = False
        if car_choice == 'car1':
            self.image = 'car1.png'
        elif car_choice == 'car2':
            self.image = 'car2.png'
        elif car_choice == 'car3':
            self.image = 'car3.png'
        elif car_choice == 'car4':
            self.image = 'car4.png'
        else:
            self.image = 'car5.png'

        self.choosing_map = True
        self.show_maps()       

    def show_modes(self):
        while self.choosing_mode:
            self.screen.blit(self.background, (0, 0))  
            self.modes_page.draw(self.screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.choosing_mode = False
                    pygame.quit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mode_choice = self.modes_page.check_click(event.pos, self.mode_choice)
                    if self.mode_choice:
                        self.choose_modes()

    def choose_modes(self):
        print(f"Selected mode: {self.mode_choice}")
        self.choosing_mode = False
        self.choosing_car = True
        self.show_cars()

    def create_objects_single(self, map_choice):
        if map_choice == 'winter':
            self.finish_location = (275, 230)
            self.finish = Finish('finish.png', *self.finish_location, 90, 0.308, "bottom")
            self.car = Cars(1350, 250, 0, 0.75, 270, self.image, 'wasd')
            self.bot = Bots(1350, 287, 0, 0.67, 270, [(1654, 265), (1774, 309), (1822, 391), (1807, 657), 
            (1721, 723), (1575, 681), (1539, 550), (1450, 468), (1317, 500), (1273, 607), (1197, 701), (1036, 739), 
            (990, 815), (956, 929), (890, 990), (497, 1010), (184, 981), (138, 868), (139, 739), (162, 631),
            (225, 564), (384, 550), (637, 549), (727, 485), (739, 365), (644, 289), (268, 285)])
            self.road_contour = pygame.image.load('winter_edge.png')                       
        elif map_choice == 'summer':
            self.finish_location = (183, 985)
            self.finish = Finish('finish.png', *self.finish_location, 142, 0.21, "bottom")
            self.car = Cars(1745, 945, 0, 0.5, 52, self.image, 'wasd')
            self.bot = Bots(1755, 925, 0, 0.48, 52, [(1491, 749), (1344, 634), (1243, 555), (1200, 474), (1236, 383), 
            (1308, 282), (1376, 185), (1366, 109), (1293, 62), (1203, 92), (1106, 121), (1024, 90), (944, 110), 
            (858, 163), (759, 132), (671, 144), (591, 228), (492, 381), (475, 475), (541, 545), (695, 643), 
            (792, 598), (796, 505), (764, 401), (812, 328), (903, 332), (938, 378), (934, 446), (901, 525), 
            (942, 606), (1064, 700), (1112, 768), (1102, 847), (1028, 898), (965, 875), (891, 816), (808, 757), 
            (719, 740), (643, 809), (583, 881), (523, 918), (440, 909), (362, 887), (306, 917), (208, 1032)])
            self.road_contour = pygame.image.load('summer_edge.png')
        elif map_choice == 'beach':
            self.finish_location = (1488, 993)
            self.finish = Finish('finish.png', *self.finish_location, 0, 0.308)
            self.car = Cars(95, 990, 0, 0.75, 270, self.image, 'wasd')
            self.bot = Bots(95, 950, 0, 0.67, 270, [(336, 962), (489, 945), (547, 826), (490, 706), (329, 661), 
            (268, 540), (347, 413), (619, 413), (709, 504), (714, 918), (767, 989), (901, 1005), (973, 921), 
            (1005, 660), (1125, 596), (1248, 530), (1293, 407), (1428, 347), (1529, 414), (1566, 534), 
            (1703, 602), (1808, 671), (1822, 767), (1780, 855), (1657, 894), (1575, 946), (1541, 1028)])
            self.road_contour = pygame.image.load('beach_edge.png')
        elif map_choice == 'champions_field':
            self.finish_location = (292, 668)
            self.finish = Finish('finish.png', *self.finish_location, 0, 0.37, required_circles = 2)
            self.car = Cars(342, 730, 0, 0.85, 180, self.image, 'wasd')
            self.bot = Bots(372, 730, 0, 0.87, 180, [(376, 853), (458, 908), (557, 952), (706, 931), (861, 943), 
            (1140, 925), (1368, 950), (1499, 884), (1556, 767), (1541, 560), (1565, 337), (1526, 216), 
            (1413, 154), (1200, 158), (927, 136), (661, 154), (441, 162), (355, 282), (342, 428), (340, 700)])
            self.road_contour = pygame.image.load('champions_field_edge.png')
        elif map_choice == 'map2':
            self.finish_location = (128, 400)
            self.finish = Finish('finish.png', *self.finish_location, 0, 0.5, required_circles = 2)
            self.car = Cars(200, 487, 0, 1, 180, self.image, 'wasd')
            self.bot = Bots(240, 487, 0, 0.88, 180, [(220, 811), (496, 954), (951, 947), (1315, 990), (1495, 761), 
            (1586, 466), (1458, 152), (1138, 49), (986, 114), (959, 259), (1080, 352), (1199, 408), (1257, 491), (1223, 609), 
            (982, 662), (680, 620), (648, 463), (708, 316), (647, 201), (493, 141), (299, 178), (258, 247), (195, 423)])
            self.road_contour = pygame.image.load('map2_contour.png')
        else:
            self.finish_location = (55, 278)
            self.finish = Finish('finish.png', *self.finish_location, 0, 0.53, required_circles = 2)
            self.car = Cars(160, 365, 0, 1.1, 180, self.image, 'wasd')
            self.bot = Bots(120, 365, 0, 0.95, 180, [(166, 629), (161, 861), (280, 970), 
            (560, 845), (697, 674), (995, 685), (1225, 561), (1569, 519), (1742, 413), 
            (1665, 242), (1362, 245), (943, 219), (686, 87), (401, 71), (184, 158), (98, 386)])
            self.road_contour = pygame.image.load('map3_contour.png')        

        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)
        self.score = Score("coin.png", map_choice)


    def create_objects_doubles(self, map_choice):
        if map_choice == 'winter':
            self.finish_location = (275, 230)
            self.finish = Finish('finish.png', *self.finish_location, 90, 0.308, "bottom")
            self.car1 = Cars(1350, 250, 0, 0.75, 270, 'car1.png', 'wasd')
            self.car2 = Cars(1350, 287, 0, 0.75, 270, 'car2.png', 'arrows')
            self.road_contour = pygame.image.load('winter_edge.png')                       
        elif map_choice == 'summer':
            self.finish_location = (183, 985)
            self.finish = Finish('finish.png', *self.finish_location, 142, 0.21, "bottom")
            self.car1 = Cars(1745, 945, 0, 0.5, 52, 'car1.png', 'wasd')
            self.car2 = Cars(1755, 925, 0, 0.5, 52, 'car2.png', 'arrows')
            self.road_contour = pygame.image.load('summer_edge.png')
        elif map_choice == 'beach':
            self.finish_location = (1488, 993)
            self.finish = Finish('finish.png', *self.finish_location, 0, 0.308)
            self.car1 = Cars(95, 990, 0, 0.75, 270, 'car1.png', 'wasd')
            self.car2 = Cars(95, 950, 0, 0.75, 270, 'car2.png', 'arrows')
            self.road_contour = pygame.image.load('beach_edge.png')
        elif map_choice == 'champions_field':
            self.finish_location = (292, 668)
            self.finish = Finish('finish.png', *self.finish_location, 0, 0.37, required_circles = 2)
            self.car1 = Cars(342, 730, 0, 0.85, 180, 'car1.png', 'wasd')
            self.car2 = Cars(372, 730, 0, 0.85, 180, 'car2.png', 'arrows')
            self.road_contour = pygame.image.load('champions_field_edge.png')
        elif map_choice == 'map2':
            self.finish_location = (128, 400)
            self.finish = Finish('finish.png', *self.finish_location, 0, 0.5, required_circles = 2)
            self.car1 = Cars(200, 487, 0, 0.78, 180, 'car1.png', 'wasd')
            self.car2 = Cars(240, 487, 0, 0.78, 180, 'car2.png', 'arrows')
            self.road_contour = pygame.image.load('map2_contour.png')
        else:
            self.finish_location = (55, 278)
            self.finish = Finish('finish.png', *self.finish_location, 0, 0.53, required_circles = 2)
            self.car1 = Cars(160, 365, 0, 0.84, 180, 'car1.png', 'wasd')
            self.car2 = Cars(120, 365, 0, 0.84, 180, 'car2.png', 'arrows')
            self.road_contour = pygame.image.load('map3_contour.png')        

        self.road_contour_mask = pygame.mask.from_surface(self.road_contour)

    def handle_pause(self):
        """
        Обробляє стан паузи гри, дозволяючи змінювати налаштування або вийти в головне меню.

        Ця функція викликається, коли гравець натискає `ESC` під час гри. Вона зупиняє 
        основний ігровий цикл та відображає меню паузи. У меню можна:
        - Відкрити налаштування.
        - Вийти в головне меню.
        - Продовжити гру, натиснувши `ESC`.

        Повертає:
            bool: `True`, якщо гравець продовжує гру.
                `False`, якщо гравець виходить у головне меню або закриває гру.
        """
        paused = True     
        while paused:
            for event in pygame.event.get():
                # Обробка кліків миші
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Відкрити меню налаштувань
                    if self.menu.options_rect.collidepoint(event.pos):
                        self.menu.show_options(self.screen, self.running, self.background)

                    # Вийти в головне меню
                    if self.menu.menu_back_rect.collidepoint(event.pos):
                        return False  

                # Закрити гру
                if event.type == pygame.QUIT:
                    self.running = False
                    quit()
                    return False  

                # Продовжити гру, якщо натиснуто ESC
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True  

            # Малюємо екран паузи
            overlay = pygame.Surface(self.aspect_ratio, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Напівпрозорий чорний фон
            self.screen.blit(self.background, (0, 0))  
            self.screen.blit(self.pause_text, self.pause_rect)
            self.screen.blit(self.menu.imageOptions, self.menu.options_rect.topleft)  
            self.screen.blit(self.menu.menu_back_bnt, self.menu.menu_back_rect)
            pygame.display.flip()  

        return True

class Menu:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.imageStart = self.load_image("start.png", (289, 143))
        self.imageOptions = self.load_image("options.png", (289, 143))
        self.imageBack = self.load_image("back.png", (288, 103))
        self.leadorboard = self.load_image("leaderboard.png", (1234, 817))
        self.rating_btn = self.load_image("rating_btn.png", (287, 141))
        self.menu_back_bnt = self.load_image("menu_btn.png", (232, 83))
        self.on_music = self.load_image("on_music.png", (288, 103))
        self.off_music = self.load_image("off_music.png", (287, 103))
        self.leadorboard_rect = self.leadorboard.get_rect(topleft=(x - 460, y - 400))
        self.start_rect = self.imageStart.get_rect(topleft=(x, y - 75))
        self.options_rect = self.imageOptions.get_rect(topleft=(x, y + 275))
        self.back_rect = self.imageBack.get_rect(topleft=(x, y + 200))
        self.back_rect2 = self.imageBack.get_rect(topleft=(x, y + 500))
        self.rating_btn_rect = self.rating_btn.get_rect(topleft=(x, y + 100))
        self.menu_back_rect = self.menu_back_bnt.get_rect(topleft=(x - 790, y - 440))
        self.on_music_rect = self.on_music.get_rect(topleft=(x, y - 200))
        self.off_music_rect = self.off_music.get_rect(topleft=(x, y - 60))
        # Параметри повзунка
        self.slider_x = self.off_music_rect.x
        self.slider_y = self.off_music_rect.y + self.off_music_rect.height + 60  
        self.slider_width = 288
        self.slider_height = 10
        self.slider_knob_radius = 10

        self.volume = 0.5  # Початкова гучність
        self.knob_x = self.slider_x + int(self.volume * self.slider_width)
        self.dragging = False       

    def load_image(self, path, size):
        img = pygame.image.load(path)
        return pygame.transform.scale(img, size)

    def draw(self, screen):
        screen.blit(self.imageStart, self.start_rect.topleft)
        screen.blit(self.imageOptions, self.options_rect.topleft)
        screen.blit(self.rating_btn, self.rating_btn_rect.topleft)

    # def draw_menu_button(self, screen):
    #     """Малює кнопку меню у верхньому лівому кутку."""
    #     screen.blit(self.menu_back_bnt, self.menu_back_rect)

    def countdown(self, countdown_images, screen, roads, car, car1, car2, bot, aspect_ratio, mode_choice):
        overlay_music_in_loop("D:/CarRacing/soundeffects/321go.mp3")
        for img in countdown_images:
            screen.fill((0, 0, 0))
            roads.draw(screen)

            if mode_choice == 'single':
                car.draw(screen)
                bot.draw(screen)

            else:
                car1.draw(screen)
                car2.draw(screen)

            img_rect = img.get_rect(center=(aspect_ratio[0] // 2, aspect_ratio[1] // 2))
            screen.blit(img, img_rect)

            pygame.display.update()
            time.sleep(1)      

    def show_options(self, screen, running, background):
        options_active = True  
        
        while options_active:
            screen.fill((0, 0, 0))
            screen.blit(background, (0, 0))
            screen.blit(self.imageBack, self.back_rect)
            screen.blit(self.on_music, self.on_music_rect)
            screen.blit(self.off_music, self.off_music_rect)

            # Малюємо повзунок
            pygame.draw.rect(screen, (200, 200, 200), (self.slider_x, self.slider_y, self.slider_width, self.slider_height))
            pygame.draw.circle(screen, (59, 59, 59), (self.knob_x, self.slider_y + self.slider_height // 2), self.slider_knob_radius)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    options_active = False 
                    pygame.quit()
                    exit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.on_music_rect.collidepoint(event.pos):
                            overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
                            start_music()
                        if self.off_music_rect.collidepoint(event.pos):
                            overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
                            stop_music()
                        if self.back_rect.collidepoint(event.pos):
                            overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
                            options_active = False
                            return
                        # Перевірка, чи натиснуто на повзунок
                        if abs(event.pos[0] - self.knob_x) < self.slider_knob_radius * 2 and \
                           self.slider_y - self.slider_knob_radius < event.pos[1] < self.slider_y + self.slider_knob_radius:
                            self.dragging = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        self.knob_x = max(self.slider_x, min(event.pos[0], self.slider_x + self.slider_width))
                        self.volume = (self.knob_x - self.slider_x) / self.slider_width
                        pygame.mixer.music.set_volume(self.volume)  # Оновлення гучності

    def show_rating(self, screen, running, in_menu, background):
        rating_active = True  
        while rating_active:
            screen.fill((0, 0, 0))
            screen.blit(background, (0, 0))
            screen.blit(self.imageBack, self.back_rect2)
            screen.blit(self.leadorboard, self.leadorboard_rect)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    rating_active = False 
                    pygame.quit()
                    exit()
                    return

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_rect2.collidepoint(event.pos):
                        overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
                        options_active = True
                        in_menu = True
                        return
    
class Background:
    def __init__(self, imagePath, animSpeed):
        self.image = pygame.image.load(imagePath)
        self.x = 0
        self.y = 0
        self.anim_speed = animSpeed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Cars:
    def __init__(self, x, y, speed, max_speed, angle, current_image, controls):
        self.angle = angle
        self.x = x  
        self.y = y  
        self.prev_coordinates = (x, y)
        self.starting_position = (x, y)  
        self.starting_angle = angle
        self.image = self.load_image(f"D:/CarRacing/{current_image}")
        self.current_image = scale_image(self.image, 0.5)
        self.rect = self.current_image.get_rect(center=(x, y))
        self.rotation_intensity = 0.6
        self.rotation_direction = 0
        self.speed = speed
        self.max_speed = max_speed
        self.acceleration = 0.01
        self.max_backward_speed = -0.4
        self.freeze_time = 0  # Час, коли машина замерзла
        self.ice_image = pygame.image.load('ice-cube.png')  # Завантажуємо зображення льоду
        self.show_ice = False  # Флаг для показу льоду
        self.ice_time = 0  # Час початку показу льоду
        self.spinning = False  # Чи машина обертається
        self.spin_time = 0  # Час початку обертання
        self.spin_duration = 1  # Тривалість обертання (в секундах)
        self.spin_speed = 5  # Швидкість обертання (градусів за кадр)
        self.frozen = False
        self.controls = controls
    
    def load_image(self, base_path):
        return pygame.image.load(f"{base_path}")
    
    def check_freeze(self):
        if self.frozen and time.time() - self.freeze_time >= 1:  # Чекаємо 1 секунду
            self.frozen = False  # Відновлюємо рух

    def check_spin(self):
        if self.spinning and time.time() - self.spin_time >= self.spin_duration:
            self.spinning = False  # Закінчити обертання

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.current_image, self.angle)
        new_rect = rotated_image.get_rect(center=self.rect.center)
        screen.blit(rotated_image, new_rect.topleft)

        # Накласти лід, якщо машина заморожена
        if self.show_ice:
            screen.blit(self.ice_image, self.rect.topleft)  # Накладаємо лід на машину
            if pygame.time.get_ticks() - self.ice_time >= 1000:  # Якщо пройшла 1 секунда
                self.show_ice = False  # Сховати лід

    def get_drive_direction(self):
        drive_direction = None
        keys = pygame.key.get_pressed()

        if self.controls == 'wasd':
            if keys[pygame.K_w]:
                drive_direction = 'forward'
            elif keys[pygame.K_s]:
                drive_direction = 'backward'
        elif self.controls == 'arrows':
            if keys[pygame.K_UP]:
                drive_direction = 'forward'
            elif keys[pygame.K_DOWN]:
                drive_direction = 'backward'
        return drive_direction


    def get_rotation_direction(self, drive_direction):
        keys = pygame.key.get_pressed()
        rotation_direction = 0

        if self.controls == 'wasd':
            if (drive_direction == 'forward' or self.speed > 0):
                if keys[pygame.K_d]:
                    rotation_direction = -1
                elif keys[pygame.K_a]:
                    rotation_direction = 1
            elif (drive_direction == 'backward' or self.speed < 0):
                if keys[pygame.K_d]:
                    rotation_direction = 1
                elif keys[pygame.K_a]:
                    rotation_direction = -1

        elif self.controls == 'arrows':
            if (drive_direction == 'forward' or self.speed > 0):
                if keys[pygame.K_RIGHT]:
                    rotation_direction = -1
                elif keys[pygame.K_LEFT]:
                    rotation_direction = 1
            elif (drive_direction == 'backward' or self.speed < 0):
                if keys[pygame.K_RIGHT]:
                    rotation_direction = 1
                elif keys[pygame.K_LEFT]:
                    rotation_direction = -1

        return rotation_direction

    def rotate(self):
        self.angle += self.rotation_intensity * self.rotation_direction

    def drive_forward(self):
        self.speed = min(self.speed + self.acceleration, self.max_speed)
        self.drive_forward_shift()

    def drive_forward_shift(self):
        angle_value = math.radians(self.angle)
        vertical_shift = self.speed * math.cos(angle_value)
        horizontal_shift = self.speed * (-math.sin(angle_value))
        self.y -= vertical_shift 
        self.x += horizontal_shift
        self.rect.center = (self.x, self.y)

    def drive_backward(self):
        self.speed = max(self.speed - self.acceleration, self.max_backward_speed)
        self.drive_backward_shift()
    
    def drive_backward_shift(self):
        angle_value = math.radians(self.angle)
        vertical_shift = self.speed * (-math.cos(angle_value))
        horizontal_shift = self.speed * math.sin(angle_value)
        self.y += vertical_shift 
        self.x -= horizontal_shift
        self.rect.center = (self.x, self.y)

    def reduce_speed_forward(self):
        self.speed = max(self.speed - self.acceleration / 4, 0)
        self.drive_forward_shift()

    def reduce_speed_backward(self):
        self.speed = min(self.speed + self.acceleration / 4, 0)
        self.drive_backward_shift()

    def collide(self, mask, x=0, y=0):
        """
        Перевіряє зіткнення автомобіля з заданою маскою.

        :param mask: Маска об'єкта, з яким перевіряється зіткнення.
        :param x: Зміщення по осі X (за замовчуванням 0).
        :param y: Зміщення по осі Y (за замовчуванням 0).
        :return: Координати точки зіткнення або None, якщо зіткнення немає.
        """
        car_mask = pygame.mask.from_surface(self.current_image)
        width, height = car_mask.get_size()
        offset = (int(self.rect.centerx - x - width // 2), int(self.rect.centery - y - height // 2))
        point_of_intersection = mask.overlap(car_mask, offset)
        return point_of_intersection

    def bounce(self):
        """
        Виконує відскок автомобіля після зіткнення, змінюючи напрямок руху.

        Швидкість змінюється на протилежну з коефіцієнтом загасання 0.65.
        Якщо автомобіль рухався вперед, після відскоку він рухається назад, і навпаки.
        """
        self.speed = -0.65 * self.speed

        if self.speed > 0:
            self.drive_backward()  # Відскок назад
        else:
            self.drive_forward()  # Відскок вперед

    def cross_finish(self, finish_collision_point, required_side):
        """
        Перевіряє, чи перетнув автомобіль фінішну лінію з правильної сторони.

        :param finish_collision_point: Координати точки зіткнення з фінішною лінією.
        :param required_side: Сторона, з якої має бути перетнута лінія ("top" або "bottom").
        :return: True, якщо автомобіль коректно перетнув фініш, інакше False.
        """
        if finish_collision_point is None:
            self.prev_coordinates = self.x, self.y
            return False
        else:
            collision_y = finish_collision_point[1]

            if (required_side == "top" and collision_y == 0) or (required_side == "bottom" and collision_y > 0):
                return True
            else:
                self.x, self.y = self.prev_coordinates
                return False
    
    def reset(self):
        """
        Скидає позицію автомобіля до початкових координат та швидкості.

        Після скидання автомобіль повертається на стартову позицію та перестає рухатися.
        """
        self.x, self.y = self.starting_position
        self.angle = self.starting_angle
        self.speed = 0.01

    
    def obstakles_feaches(self, obs, map_choice):
        if obs.check_collision_obstackles(self.rect, map_choice):  # Якщо машина торкається об'єкта
            if map_choice == "winter":
                self.frozen = True
                overlay_music_in_loop("D:/CarRacing/soundeffects/ice_sound.mp3")
                self.freeze_time = time.time()
                self.show_ice = True  # Показати лід
                self.ice_time = pygame.time.get_ticks()  # Час початку накладання льоду
                obs.show_snowflakes = False
                return
            elif map_choice == "beach" or map_choice == "map3":
                self.spinning = True  # Почати обертання
                overlay_music_in_loop("D:/CarRacing/soundeffects/spinning.mp3")
                self.spin_time = time.time()  # Запам'ятати час початку
                return
            elif map_choice == "map2":  
            # Якщо поворот ще не активовано, ініціалізуємо його
                if not hasattr(self, "sand_turning") or time.time() - self.sand_turn_start >= 1.5: 
                    self.sand_turning = random.choice([-1, 1])  # Випадковий напрямок повороту
                    self.sand_turn_start = time.time()  # Час початку повороту
                else:
                    self.angle += self.sand_turning * 0.5  # Плавний поворот (0.5 градуса за кадр)
    
    def update_car(self, obs, map_choice, score, mode_choice = 'single'):
        self.check_freeze()  # Перевіряємо, чи закінчився час заморозки
        self.check_spin()  # Перевіряємо, чи закінчилося обертання

        if self.frozen:
            return  # Блокуємо рух, поки машина заморожена

        if self.spinning:
            self.angle += self.spin_speed  # Плавне обертання
            return             
        
        # Перевірка на зіштовхнення з монетками
        if mode_choice == 'single':
            score.check_collision(self.rect)
        self.obstakles_feaches(obs, map_choice)      
        drive_direction = self.get_drive_direction()
        rotation_direction = self.get_rotation_direction(drive_direction)
        self.rotation_direction = rotation_direction
        self.rotate()
        moved = False

        if drive_direction == 'forward':
            moved = True
            self.drive_forward()
        elif drive_direction == 'backward':
            moved = True
            self.drive_backward()

        if not moved:
            if self.speed > 0:
                self.reduce_speed_forward()
            elif self.speed < 0:
                self.reduce_speed_backward()
            else:
                pass

class Score:
    """
    Клас для керування очками гравця та монетами у грі.

    Відповідає за розміщення монет на карті, підрахунок очок,
    збереження та завантаження очок із файлу, а також їхнє відображення на екрані.
    """

    def __init__(self, image_path, map_choice="none", file_path="score.txt", car_file_path="purchased_cars.txt", map_file_path="purchased_maps.txt"):
        """
        Ініціалізує об'єкт очок та монет.

        :param image_path: Шлях до зображення монети.
        :param map_choice: Назва карти для визначення можливих розташувань монет.
                           Якщо "none", монети будуть розміщені випадково.
        :param file_path: Шлях до файлу для збереження очок.
        """
        self.image = scale_image(pygame.image.load(image_path), 0.07)
        self.file_path = file_path
        self.car_purchased = False  # Додаємо змінну, яка відстежує покупку
        self.map_purchased = False  
        self.car_file_path = car_file_path
        self.map_file_path = map_file_path
        self.buy_price = 3000
        self.buy_price2 = 5000
        self.buy_prices = {"car": 3000, "map": 5000}  # Ціна для машин і карт
        
        # Визначення можливих позицій монет для кожної карти
        self.coin_positions = {
            "winter": [(515, 286), (630, 580), (219, 521), (179, 904), (605, 1009), 
                       (881, 909), (1166, 632), (1377, 463), (1761, 583), (1712, 260)],
            "beach": [(385, 932), (193, 521), (549, 366), (708, 702), (825, 1032), 
                      (950, 610), (1263, 549), (1383, 310), (1620, 521), (1588, 835)],
            "map3": [(40, 503), (190, 748), (488, 941), (766, 594), (1283, 586), 
                     (1772, 371), (1577, 157), (1180, 295), (744, 91), (117, 156)],
            "map2": [(162, 218), (165, 748), (564, 945), (1170, 849), (1540, 707), 
                     (1441, 287), (1228, 22), (1056, 367), (582, 590), (538, 86)],
            "summer": [(373, 869), (716, 686), (1003, 608), (923, 296), (462, 479), 
                       (648, 176), (1008, 64), (1311, 247), (1165, 525), (1568, 776)],
            "champions_field": [(376, 914), (711, 905), (1145, 960), (1494, 746), (1567, 391), 
                                (1404, 84), (1103, 158), (765, 132), (320, 199), (391, 521)],
            "none": [(random.randint(100, 1800), random.randint(100, 900)) for _ in range(5)]
        }

        # Вибираємо 5 випадкових монет із доступних позицій або всі, якщо їх менше
        available_positions = self.coin_positions.get(map_choice, [])
        self.coins = random.sample(available_positions, min(5, len(available_positions)))

        # Створення об'єктів Rect для перевірки зіткнень
        self.coin_rects = [pygame.Rect(x, y, self.image.get_width(), self.image.get_height()) for x, y in self.coins]

        self.last_score = -1
        self.font = pygame.font.Font("D:/CarRacing/AveriaSansLibre-Bold.ttf", 36)
        self.score_pos = (1700, 10)  # Збереження позиції

        # Завантаження очок із файлу
        self.load_score()

    def load_score(self):
        """
        Завантажує очки з файлу. Якщо файл не існує або пошкоджений, встановлює 0.
        """
        try:
            with open(self.file_path, "r") as file:
                self.current_score = int(file.read().strip())
        except (FileNotFoundError, ValueError):
            self.current_score = 0

    def save_score(self):
        """
        Зберігає поточну кількість очок у файл.
        """
        with open(self.file_path, "w") as file:
            file.write(str(self.current_score))

    def draw_coins(self, screen):
        """
        Малює монети на екрані.
d
        :param screen: Поверхня Pygame, на якій відображається гра.
        """
        for i, (x, y) in enumerate(self.coins):
            screen.blit(self.image, (x, y))
            self.coin_rects[i].topleft = (x, y)

    def check_collision(self, car_rect):
        """
        Перевіряє, чи автомобіль зіткнувся з монетою. Якщо так, монета видаляється та додаються очки.

        :param car_rect: Прямокутник (pygame.Rect), що представляє колізію автомобіля.
        :return: True, якщо зіткнення було, False інакше.
        """
        for i, rect in enumerate(self.coin_rects):
            if rect.colliderect(car_rect):
                self.coins.pop(i)
                self.coin_rects.pop(i)
                overlay_music_in_loop("D:/CarRacing/soundeffects/coin_collect.mp3")
                self.add_score(100)
                return True
        return False

    def load_purchases(self, file_path):
        """Завантажує куплені авто або карти"""
        if not os.path.exists(file_path):
            return set()
        with open(file_path, "r") as file:
            return set(file.read().splitlines())

    def save_purchases(self, file_path, purchases):
        """Зберігає куплені авто або карти"""
        with open(file_path, "w") as file:
            file.write("\n".join(purchases))

    def purchase_item(self, item_name, item_type):
        """
        Універсальний метод покупки для машин і карт.

        :param item_name: Назва авто або карти.
        :param item_type: Тип ("car" або "map").
        :return: True, якщо покупка вдала, інакше False.
        """
        if item_type not in self.buy_prices:
            return False  # Некоректний тип товару

        file_path = self.car_file_path if item_type == "car" else self.map_file_path
        purchased_items = self.load_purchases(file_path)
        price = self.buy_prices[item_type]

        if self.current_score >= price and item_name not in purchased_items:
            purchased_items.add(item_name)
            self.current_score -= price
            self.save_score()
            self.save_purchases(file_path, purchased_items)
            return True
        return False

    def add_score(self, amount):
        """
        Додає вказану кількість очок та зберігає оновлений рахунок.

        :param amount: Кількість очок для додавання.
        """
        self.current_score += amount
        self.save_score()

    def subtract_score(self, amount):
        """
        Віднімає вказану кількість очок та зберігає оновлений рахунок.

        :param amount: Кількість очок для віднімання.
        """
        self.current_score -= amount
        self.save_score()

    def clear_score(self):
        """
        Обнуляє рахунок гравця та зберігає зміни у файлі.
        """
        self.current_score = 0
        self.save_score()

    def draw_score(self, screen):
        """
        Відображає поточну кількість очок у правому верхньому куті екрана.

        :param screen: Поверхня Pygame, на якій відображається гра.
        """
        if self.current_score != self.last_score:
             self.last_score = self.current_score
             self.score_text = self.font.render(f"Score: {self.current_score}", True, (255, 255, 255))

        screen.blit(self.score_text, self.score_pos)

    def is_item_purchased(self, item_name, item_type):
        """
        Перевіряє, чи куплений товар (авто або карта).

        :param item_name: Назва авто або карти.
        :param item_type: Тип ("car" або "map").
        :return: True, якщо куплено, False інакше.
        """
        file_path = self.car_file_path if item_type == "car" else self.map_file_path
        purchased_items = self.load_purchases(file_path)
        return item_name in purchased_items

    def check_buy_click(self, pos, item_name, buy_rect, item_type):
        """
        Обробляє клік по кнопці покупки (універсальний метод для авто і карт).

        :param pos: Координати кліку.
        :param item_name: Назва авто або карти.
        :param buy_rect: Прямокутник кнопки покупки.
        :param item_type: Тип товару ("car" або "map").
        :return: True, якщо покупка вдала, інакше False.
        """
        if buy_rect.collidepoint(pos) and not self.is_item_purchased(item_name, item_type):
            return self.purchase_item(item_name, item_type)
        return False


class Roads:
    def __init__(self, imagePath, animSpeed):
        self.image = pygame.image.load(imagePath)
        self.x = 0
        self.y = 0
        self.anim_speed = animSpeed

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Obstacles:
    def __init__(self, x, y, imagePath, imagePath2, imagePath3):
        self.image = pygame.image.load(imagePath)
        self.image2 = pygame.image.load(imagePath2)
        self.image3 = pygame.image.load(imagePath3)
        self.snowflakes = [(539, 1025), (607, 577), (96, 780), (1588, 285), 
                           (1395, 434), (1269, 657), (1679, 746), (628, 244), 
                           (248, 1024), (1137, 708), (1821, 492), (360, 302)]  # Координати сніжинок
        self.banana = [(1069, 555), (850, 1019), (1262, 522), (1632, 599),
                        (1586, 854), (552, 851), (343, 919), (356, 690),
                        (216, 481), (285, 505), (661, 887), (1610, 925)]
        self.banana2 = [(100, 900), (79, 737), (136, 497), (424, 50), 
                        (781, 165), (1240, 280), (1379, 173), (1547, 262), 
                        (1684, 456), (1345, 580), (1043, 563), (844, 665)]
        self.sand = [(545, 805), (1329, 791), (1282, 469), (533, 503),
                     (308, 196), (716, 651), (244, 715), (987, 193),
                     (923, 610), (457, 867), (1256, 536), (187, 340)]
        self.snowflakes_rand = random.sample(self.snowflakes, 4)
        self.banana_rand = random.sample(self.banana, 4)
        self.banana2_rand = random.sample(self.banana2, 4)
        self.sand_rand = random.sample(self.sand, 4)
        self.snowflake_rects = [pygame.Rect(x, y, self.image.get_width(), self.image.get_height()) for x, y in self.snowflakes_rand]
        self.banana_rects = [pygame.Rect(x, y, self.image2.get_width(), self.image2.get_height()) for x, y in self.banana_rand]
        self.banana2_rects = [pygame.Rect(x, y, self.image2.get_width(), self.image2.get_height()) for x, y in self.banana2_rand]
        self.sand_rects = [pygame.Rect(x, y, self.image3.get_width(), self.image3.get_height()) for x, y in self.sand_rand]
        self.show_snowflakes = True
        self.show_banana = True

    def draw_obstackles(self, screen, map_choice):
        if map_choice == "winter":
            for i, (x, y) in enumerate(self.snowflakes_rand):
                screen.blit(self.image, (x, y))
                self.snowflake_rects[i].topleft = (x, y)  # Оновлюємо позицію
        elif map_choice =='beach':
            for i, (x, y) in enumerate(self.banana_rand):
                screen.blit(self.image2, (x, y))
                self.banana_rects[i].topleft = (x, y)
        elif map_choice =='map3':
            for i, (x, y) in enumerate(self.banana2_rand):
                screen.blit(self.image2, (x, y))
                self.banana2_rects[i].topleft = (x, y)
        elif map_choice =='map2':
            for i, (x, y) in enumerate(self.sand_rand):
                screen.blit(self.image3, (x, y))
                self.sand_rects[i].topleft = (x, y)

    def check_collision_obstackles(self, car_rect, map_choice):
        if map_choice == "winter":
            for i, rect in enumerate(self.snowflake_rects):
                if rect.colliderect(car_rect):
                    # Якщо зіткнення, видалити сніжинку
                    self.snowflakes_rand.pop(i)
                    self.snowflake_rects.pop(i)
                    return True  # Зіткнення відбулося
        elif map_choice =='beach':
            for i, rect in enumerate(self.banana_rects):
                if rect.colliderect(car_rect):
                    self.banana_rand.pop(i)
                    self.banana_rects.pop(i)
                    return True
        elif map_choice =='map3':
            for i, rect in enumerate(self.banana2_rects):
                if rect.colliderect(car_rect):
                    self.banana2_rand.pop(i)
                    self.banana2_rects.pop(i)
                    return True
        elif map_choice =='map2':
            for i, rect in enumerate(self.sand_rects):
                if rect.colliderect(car_rect):
                    return True
        return False  # Якщо зіткнення не було

class Bots(Cars):
    def __init__(self, x, y, speed, max_speed, angle, points):
        available_cars = [
            "car1.png", "car2.png", "car3.png", "car4.png", "car5.png"
        ]
        current_image = random.choice(available_cars)
        controls = 'wasd'
        super().__init__(x, y, speed, max_speed, angle, current_image, controls)

        self.target_y = 400  # Цільова координата Y
        self.current_point = 0
        self.points = points

    def draw_points(self, screen):
        for point in self.points:
            pygame.draw.circle(screen, (255, 0, 0), point, 5)  # Малюємо кульки червоним кольором

    def calculate_angle(self):
        target_x, target_y = self.points[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_intensity, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_intensity, abs(difference_in_angle))

    def update_points(self):
        target = self.points[self.current_point]
        rect = pygame.Rect(
            self.x, self.y, self.current_image.get_width(), self.current_image.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.points):
            return

        self.calculate_angle()
        self.update_points()
        if self.controls == 'wasd':
            super().drive_forward()    

    def reset(self):
        self.x, self.y = self.starting_position
        self.angle = self.starting_angle
        self.speed = 0
        self.current_point = 0

class ConfigurationMenu(ABC):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.font = pygame.font.Font("D:/CarRacing/AveriaSansLibre-Bold.ttf", 36)
        self.title_font = pygame.font.Font("D:/CarRacing/AveriaSansLibre-Bold.ttf", 56)
  
    def load_image(self, path):
        return pygame.image.load(path)

    def draw_text(self, text, x, y, screen, font = None):
        if font is None:
            font = self.font
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

    @abstractmethod
    def draw():
        pass

    @abstractmethod
    def check_click():
        pass         

class MapsMenu(ConfigurationMenu):
    def __init__(self, x, y, score, file_path="purchased_maps.txt"):
        super().__init__(x, y)
        self.file_path = file_path
        self.score = score 
        self.purchased_maps = self.load_purchased_maps()
        
        self.image_map3 = self.load_image("map3_preview.png")
        self.image_map2 = self.load_image("map2_preview.png")
        self.image_beach = self.load_image("beach_preview.png")
        self.image_winter = self.load_image("winter_preview.png")
        self.image_summer = self.load_image("summer_preview.png")
        self.image_champions_field = self.load_image("champions_field_preview.png")
        self.image_beach_lock = self.load_image("beach_lock.png")
        self.image_winter_lock = self.load_image("winter_lock.png")
        self.image_summer_lock = self.load_image("summer_lock.png")
        self.image_champions_field_lock = self.load_image("champions_field_lock.png")
        self.buy_image = self.load_image("5000.png")
        
        self.map3_rect = self.image_map3.get_rect(topleft=(x, y + 90))
        self.map2_rect = self.image_map2.get_rect(topleft=(x, y + 550))
        self.beach_rect = self.image_beach.get_rect(topleft=(x + 600, y + 90))
        self.winter_rect = self.image_winter.get_rect(topleft=(x + 600, y + 550))
        self.summer_rect = self.image_summer.get_rect(topleft=(x + 1200, y + 90))
        self.champions_field_rect = self.image_champions_field.get_rect(topleft=(x + 1200, y + 550))
        self.buy_image_rect = self.buy_image.get_rect(topleft=(x + 750, y + 410))
        self.buy_image_rect2 = self.buy_image.get_rect(topleft=(x + 1350, y + 410))
        self.buy_image_rect3 = self.buy_image.get_rect(topleft=(x + 1350, y + 870))
        self.buy_image_rect4 = self.buy_image.get_rect(topleft=(x + 750, y + 870))

    def load_purchased_maps(self):
        if not os.path.exists(self.file_path):
            return set()
        with open(self.file_path, "r") as file:
            return set(file.read().splitlines())
    
    def save_purchased_maps(self):
        with open(self.file_path, "w") as file:
            file.write("\n".join(self.purchased_maps))
    
    def purchase_map(self, map_name):
        if map_name not in self.purchased_maps:
            self.purchased_maps.add(map_name)
            self.save_purchased_maps()

    def draw(self, screen):
        screen.blit(self.image_map3, self.map3_rect.topleft)
        screen.blit(self.image_map2, self.map2_rect.topleft)
        screen.blit(self.image_beach if 'beach' in self.purchased_maps else self.image_beach_lock, self.beach_rect.topleft)
        screen.blit(self.image_winter if 'winter' in self.purchased_maps else self.image_winter_lock, self.winter_rect.topleft)
        screen.blit(self.image_summer if 'summer' in self.purchased_maps else self.image_summer_lock, self.summer_rect.topleft)
        screen.blit(self.image_champions_field if 'champions_field' in self.purchased_maps else self.image_champions_field_lock, self.champions_field_rect.topleft)        

        if 'beach' not in self.purchased_maps:
            screen.blit(self.buy_image, self.buy_image_rect.topleft)
        if 'summer' not in self.purchased_maps:
            screen.blit(self.buy_image, self.buy_image_rect2.topleft)
        if 'champions_field' not in self.purchased_maps:
            screen.blit(self.buy_image, self.buy_image_rect3.topleft)
        if 'winter' not in self.purchased_maps:
            screen.blit(self.buy_image, self.buy_image_rect4.topleft)

        self.draw_text("Select a map:", self.beach_rect.centerx, self.y - 50, screen, self.title_font)
        self.draw_text("Tidal Heatwave", self.map3_rect.centerx, self.map3_rect.top - 30, screen)
        self.draw_text("Meadow Rush", self.map2_rect.centerx, self.map2_rect.top - 30, screen)
        self.draw_text("Palm Paradise", self.beach_rect.centerx, self.beach_rect.top - 30, screen)
        self.draw_text("Frozen Tides", self.winter_rect.centerx, self.winter_rect.top - 30, screen)
        self.draw_text("Evergreen Escape", self.summer_rect.centerx, self.summer_rect.top - 30, screen)
        self.draw_text("Champions Field", self.champions_field_rect.centerx, self.champions_field_rect.top - 30, screen)
        self.score.draw_score(screen)

    def check_click(self, pos):

        if self.buy_image_rect.collidepoint(pos):
            if self.score.purchase_item("beach", "map"):
                overlay_music_in_loop("D:/CarRacing/soundeffects/purchase.mp3")
                self.purchased_maps.add("beach")
                self.save_purchased_maps()
        elif self.buy_image_rect2.collidepoint(pos):
            if self.score.purchase_item("summer", "map"):
                overlay_music_in_loop("D:/CarRacing/soundeffects/purchase.mp3")
                self.purchased_maps.add("summer")
                self.save_purchased_maps()
        elif self.buy_image_rect3.collidepoint(pos):
            if self.score.purchase_item("champions_field", "map"):
                overlay_music_in_loop("D:/CarRacing/soundeffects/purchase.mp3")
                self.purchased_maps.add("champions_field")
                self.save_purchased_maps()
        elif self.buy_image_rect4.collidepoint(pos):
            if self.score.purchase_item("winter", "map"):
                overlay_music_in_loop("D:/CarRacing/soundeffects/purchase.mp3")
                self.purchased_maps.add("winter")
                self.save_purchased_maps()

        if self.map3_rect.collidepoint(pos):
            return 'map3'
        elif self.map2_rect.collidepoint(pos):
            return 'map2'
        elif self.beach_rect.collidepoint(pos) and "beach" in self.purchased_maps:
            return 'beach'
        elif self.winter_rect.collidepoint(pos) and "winter" in self.purchased_maps:
            return 'winter'
        elif self.summer_rect.collidepoint(pos) and "summer" in self.purchased_maps:
            return 'summer'
        elif self.champions_field_rect.collidepoint(pos) and "champions_field" in self.purchased_maps:
            return 'champions_field'
        return None

class CarsMenu(ConfigurationMenu):
    def __init__(self, x, y, score, file_path="purchased_cars.txt"):
        super().__init__(x, y)
        self.file_path = file_path
        self.score = score 
        self.purchased_cars = self.load_purchased_cars()
        
        self.image_car1 = self.load_image("car1_preview.png")
        self.image_car2 = self.load_image("car2_preview.png")
        self.image_car3 = self.load_image("car3_preview.png")
        self.image_car4 = self.load_image("car4_preview.png")
        self.image_car5 = self.load_image("car5_preview.png")
        
        self.image_car1_lock = self.load_image("car1_lock.png")
        self.image_car2_lock = self.load_image("car2_lock.png")
        self.image_car3_lock = self.load_image("car3_lock.png")
        
        self.buy_image = self.load_image("3000.png")
        
        self.car1_rect = self.image_car1.get_rect(topleft=(x + 1200, y + 60))
        self.car2_rect = self.image_car2.get_rect(topleft=(x + 600, y + 60))
        self.car3_rect = self.image_car3.get_rect(topleft=(x + 900, y + 550))
        self.car4_rect = self.image_car4.get_rect(topleft=(x + 300, y + 550))
        self.car5_rect = self.image_car5.get_rect(topleft=(x, y + 60))
        self.buy_image_rect = self.buy_image.get_rect(topleft=(x + 1325, y + 400))
        self.buy_image2_rect = self.buy_image.get_rect(topleft=(x + 725, y + 400))
        self.buy_image3_rect = self.buy_image.get_rect(topleft=(x + 1025, y + 890))
    
    def load_purchased_cars(self):
        if not os.path.exists(self.file_path):
            return set()
        with open(self.file_path, "r") as file:
            return set(file.read().splitlines())
    
    def save_purchased_cars(self):
        with open(self.file_path, "w") as file:
            file.write("\n".join(self.purchased_cars))
    
    def purchase_car(self, car_name):
        if car_name not in self.purchased_cars:
            self.purchased_cars.add(car_name)
            self.save_purchased_cars()
    
    def draw(self, screen):
        screen.blit(self.image_car1 if 'car1' in self.purchased_cars else self.image_car1_lock, self.car1_rect.topleft)
        screen.blit(self.image_car2 if 'car2' in self.purchased_cars else self.image_car2_lock, self.car2_rect.topleft)
        screen.blit(self.image_car3 if 'car3' in self.purchased_cars else self.image_car3_lock, self.car3_rect.topleft)
        screen.blit(self.image_car4, self.car4_rect.topleft)
        screen.blit(self.image_car5, self.car5_rect.topleft)
        
        # Малюємо кнопки "Купити", якщо машина ще не куплена
        if 'car1' not in self.purchased_cars:
            screen.blit(self.buy_image, self.buy_image_rect.topleft)
        if 'car2' not in self.purchased_cars:
            screen.blit(self.buy_image, self.buy_image2_rect.topleft)
        if 'car3' not in self.purchased_cars:
            screen.blit(self.buy_image, self.buy_image3_rect.topleft)
        
        self.draw_text("Select a car:", self.car2_rect.centerx, self.y - 50, screen, self.title_font)
        self.draw_text("Ferrari 458 Challenge", self.car1_rect.centerx, self.car1_rect.top - 30, screen)
        self.draw_text("Mclaren P1 Sports", self.car2_rect.centerx, self.car2_rect.top - 30, screen)
        self.draw_text("Ford Mustang Shelby", self.car3_rect.centerx, self.car3_rect.top - 30, screen)
        self.draw_text("Subaru Impreza WRX STI", self.car4_rect.centerx, self.car4_rect.top - 30, screen)
        self.draw_text("Dodge Viper GTS", self.car5_rect.centerx, self.car5_rect.top - 30, screen)
        self.score.draw_score(screen)
    
    def check_click(self, pos):
        if self.buy_image_rect.collidepoint(pos):
            if self.score.purchase_item("car1", "car"):
                overlay_music_in_loop("D:/CarRacing/soundeffects/purchase.mp3")
                self.purchased_cars.add("car1")
                self.save_purchased_cars()
        elif self.buy_image2_rect.collidepoint(pos):
            if self.score.purchase_item("car2", "car"):
                overlay_music_in_loop("D:/CarRacing/soundeffects/purchase.mp3")
                self.purchased_cars.add("car2")
                self.save_purchased_cars()
        elif self.buy_image3_rect.collidepoint(pos):
            if self.score.purchase_item("car3", "car"):
                overlay_music_in_loop("D:/CarRacing/soundeffects/purchase.mp3")
                self.purchased_cars.add("car3")
                self.save_purchased_cars()
    
        # Вибір тільки куплених машин
        if self.car1_rect.collidepoint(pos) and "car1" in self.purchased_cars:
            overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
            return "car1"
        elif self.car2_rect.collidepoint(pos) and "car2" in self.purchased_cars:
            overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
            return "car2"
        elif self.car3_rect.collidepoint(pos) and "car3" in self.purchased_cars:
            overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
            return "car3"
        elif self.car4_rect.collidepoint(pos):
            overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
            return "car4"
        elif self.car5_rect.collidepoint(pos):
            overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
            return "car5"
        return None
    
class ModesMenu(ConfigurationMenu):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.image_single = self.load_image("single.png")        
        self.image_doubles = self.load_image("doubles.png")

        self.single_rect = self.image_single.get_rect(topleft=(x - 40, y + 250))
        self.doubles_rect = self.image_doubles.get_rect(topleft=(x + 890, y + 250))

    def draw(self, screen):
        screen.blit(self.image_single, self.single_rect.topleft)
        screen.blit(self.image_doubles, self.doubles_rect.topleft)

        self.draw_text("Select the game mode:", self.x + 855, self.y + 50, screen, self.title_font)
        self.draw_text("Single", self.single_rect.centerx, self.single_rect.top - 30, screen)
        self.draw_text("Doubles", self.doubles_rect.centerx, self.doubles_rect.top - 30, screen)

    def check_click(self, pos, mode_choice):
        if self.single_rect.collidepoint(pos):
            overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
            mode_choice = 'single'
            return mode_choice
        elif self.doubles_rect.collidepoint(pos):
            overlay_music_in_loop("D:/CarRacing/soundeffects/button_sound.mp3")
            mode_choice = 'doubles'
            return mode_choice
        
        return None

class Finish:
    """
    Клас Finish представляє фінішну лінію у грі. Відповідає за відстеження проходження 
    фінішу машинами, підрахунок кіл та виведення результатів.
    """

    def __init__(self, imagePath, x, y, angle, scale_value, required_side="top", required_circles=1):
        """
        Ініціалізує об'єкт фінішу.

        :param imagePath: Шлях до зображення фінішної лінії.
        :param x: Початкова координата X.
        :param y: Початкова координата Y.
        :param angle: Кут повороту фінішної лінії.
        :param scale_value: Масштабування зображення.
        :param required_side: Сторона, з якої необхідно перетнути фініш (за замовчуванням "top").
        :param required_circles: Кількість необхідних кіл для завершення гонки.
        """
        self.image = scale_image(pygame.image.load(imagePath), scale_value)
        self.x = x
        self.y = y
        self.angle = angle
        self.required_side = required_side
        self.required_circles = required_circles
        self.car1_wins, self.car2_wins = 0, 0

    def draw(self, screen):
        """
        Малює фінішну лінію на екрані.

        :param screen: Екран, на якому відображається фініш.
        """
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        self.mask = pygame.mask.from_surface(rotated_image)
        screen.blit(rotated_image, (self.x, self.y))

    def crossed(self, screen, aspect_ratio, car1, car2, score = None):
        """
        Визначає, чи перетнула машина фінішну лінію, та підраховує кола.

        :param screen: Екран для відображення результатів.
        :param aspect_ratio: Співвідношення сторін екрану.
        :param car1: Об'єкт першої машини.
        :param car2: Об'єкт другої машини.
        :return: True, якщо гонка завершена, інакше False.
        """
        if self.car1_wins + self.car2_wins == self.required_circles:
            if self.car1_wins > self.car2_wins:      
                self.show_result(screen, aspect_ratio, 'Car 1 Wins!', "D:/CarRacing/soundeffects/car1_win.mp3")
                self.credit_prize(score, 200)
            elif self.car1_wins < self.car2_wins:
                self.show_result(screen, aspect_ratio, 'Car 2 Wins!', "D:/CarRacing/soundeffects/car2_win.mp3")
            else:
                self.show_result(screen, aspect_ratio, 'It\'s a Tie!')
                self.credit_prize(score, 100)
            stop_sound()
            return True

        else:
            car1_collision_point = car1.collide(self.mask, self.x, self.y)
            car2_collision_point = car2.collide(self.mask, self.x, self.y)
            if car1.cross_finish(car1_collision_point, self.required_side):
                self.car1_wins += 1
                self.display_circle_number(screen, aspect_ratio)
                car1.reset()
                car2.reset()
                self.menu = Menu(825, 400)
        
            elif car2.cross_finish(car2_collision_point, self.required_side):
                self.car2_wins += 1
                self.display_circle_number(screen, aspect_ratio)
                car1.reset()
                car2.reset()

            return False

    def credit_prize(self, score, amount):
        if score != None:
            score.add_score(amount)

    def display_circle_number(self, screen, aspect_ratio):
        """
        Відображає поточний номер кола на екрані.

        :param screen: Екран, на якому відображається номер кола.
        :param aspect_ratio: Співвідношення сторін екрану.
        """
        font = pygame.font.Font("D:/CarRacing/AveriaSansLibre-Bold.ttf", 72)
        text = font.render(f"Circle #{self.car1_wins + self.car2_wins} out of {self.required_circles} done!", True, (255, 255, 0))
        text_rect = text.get_rect(center=(aspect_ratio[0] // 2, aspect_ratio[1] // 2))
        screen.blit(text, text_rect)
        pygame.display.update()
        time.sleep(1)

    def show_result(self, screen, aspect_ratio, message, musicPath):
        """
        Відображає фінальний результат гонки на екрані.

        :param screen: Екран, на якому відображається результат.
        :param aspect_ratio: Співвідношення сторін екрану.
        :param message: Текст повідомлення про переможця.
        """
        font = pygame.font.Font("D:/CarRacing/AveriaSansLibre-Bold.ttf", 72)
        text = font.render(message, True, (255, 255, 0))
        text_rect = text.get_rect(center=(aspect_ratio[0] // 2, aspect_ratio[1] // 2))
        screen.blit(text, text_rect)
        pygame.display.update()
        overlay_music_in_loop(musicPath)
        time.sleep(5)

if __name__ == "__main__":
    game = GameSys()
    game.run()