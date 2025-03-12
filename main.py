import pygame
from game_objects import Cars, Bots, Roads, Obstacles, Finish, Score
from menus import Menu, MapsMenu, CarsMenu, ModesMenu
from music import overlay_music_in_loop, next_track, mute_music, music_playing
from utilities import scale_image

pygame.init()

class GameSys:
    """
    Основний клас гри, що управляє логікою гри, відображенням та взаємодією з гравцем.

    Цей клас ініціалізує всі об'єкти гри (машини, боти, дороги, меню тощо), 
    управляє основним циклом гри та обробляє введення користувача.
    """
    def __init__(self):
        """Ініціалізація основних параметрів гри."""
        self.running = True  # Прапорець для роботи основного циклу гри
        self.aspect_ratio = (1920, 1080)  # Роздільна здатність екрану
        self.screen = pygame.display.set_mode(self.aspect_ratio)  # Створення вікна гри
        pygame.display.set_caption('Car Racing')  # Заголовок вікна
        self.background = pygame.image.load('img/garage_blur.png')  # Фон для меню
        self.car = Cars(400, 997, 0, 0, 0, 'img/car1.png', 'wasd')  # Основна машина для одиночного режиму
        self.bot = Bots(400, 992, 0, 0, 0, [])  # Бот для одиночного режиму
        self.menu = Menu(800, 450)  # Головне меню
        self.roads = Roads('img/winter.jpg', 'img/winter_edge.png')  # Дороги (карта)
        self.obs = Obstacles('img/snowflake.png', 'img/banana.png', 'img/sand.png')  # Перешкоди
        self.countdown_images = [  # Зображення для зворотного відліку
            pygame.image.load('img/3.png'),
            scale_image(pygame.image.load('img/2.png'), 2),
            pygame.image.load('img/1.png'),
            pygame.image.load('img/GO.png')
        ]
        self.in_menu = True  # Прапорець перебування в меню
        self.score = Score("img/coin.png")  # Об'єкт для підрахунку очок
        self.maps_page = MapsMenu(80, 100, self.score)  # Меню вибору карт
        self.cars_page = CarsMenu(90, 100, self.score)  # Меню вибору машин
        self.modes_page = ModesMenu(100, 100)  # Меню вибору режимів
        self.choosing_map = False  # Прапорець вибору карти
        self.choosing_car = False  # Прапорець вибору машини
        self.choosing_mode = False  # Прапорець вибору режиму
        self.map_choice = '0'  # Обрана карта
        self.mode_choice = '0'  # Обраний режим
        self.car1 = Cars(400, 997, 0, 0.5, 0, 'img/car5.png', 'wasd')  # Перша машина для двогравцевого режиму
        self.car2 = Cars(500, 997, 0, 0.5, 0, 'img/car5.png', 'arrows')  # Друга машина для двогравцевого режиму
        self.pause_font = pygame.font.Font("fonts/AveriaSansLibre-Bold.ttf", 36)  # Шрифт для тексту паузи
        self.pause_text = self.pause_font.render('Paused', True, (255, 255, 255))  # Текст паузи
        self.pause_rect = self.pause_text.get_rect(center=(self.aspect_ratio[0]//2 - 15, self.aspect_ratio[1]//2))  # Позиція тексту паузи

    def run(self):
        """
        Основний цикл гри.

        Цей метод запускає гру, відображає меню, оновлює екран та обробляє події.
        """
        new_game = True  # Прапорець для запуску нової гри
        clock = pygame.time.Clock()  # Об'єкт для регулювання FPS
        while self.running:
            if new_game:
                self.in_menu = True  # Повернення в меню перед новою грою
                self.show_menu()  # Відображення головного меню
                self.menu.countdown(self.countdown_images, self.screen, self.roads, self.car, self.car1, self.car2, self.bot, self.aspect_ratio, self.mode_choice)  # Зворотний відлік
                new_game = False  # Вимикаємо прапорець нової гри після запуску

            # Малювання ігрових об'єктів
            self.roads.draw(self.screen)  # Відображення доріг
            self.finish.draw(self.screen)  # Відображення фінішу
            self.obs.draw_obstackles(self.screen, self.map_choice)  # Відображення перешкод

            if self.mode_choice == 'single':
                # Логіка для одиночного режиму
                self.score.draw_coins(self.screen)  # Малювання монет
                self.car.draw(self.screen)  # Малювання гравця
                self.car.update_car(self.obs, self.map_choice, self.score)  # Оновлення стану гравця
                self.bot.draw(self.screen)  # Малювання бота
                new_game = self.finish.crossed(self.screen, self.aspect_ratio, self.car, self.bot, self.score)  # Перевірка перетину фінішу
                self.score.draw_score(self.screen)  # Відображення очок
            else:
                # Логіка для двогравцевого режиму
                self.car1.draw(self.screen)  # Малювання першої машини
                self.car1.update_car(self.obs, self.map_choice, self.score, self.mode_choice)  # Оновлення стану
                self.car2.draw(self.screen)  # Малювання другої машини
                self.car2.update_car(self.obs, self.map_choice, self.score, self.mode_choice)  # Оновлення стану
                new_game = self.finish.crossed(self.screen, self.aspect_ratio, self.car1, self.car2)  # Перевірка перетину фінішу

            pygame.display.update()  # Оновлення екрану

            # Обробка подій
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False  # Закриття гри
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if not self.handle_pause():  # Виклик меню паузи
                            new_game = True  # Повернення до меню
                            break
                    elif event.key == pygame.K_n:
                        if music_playing.is_set():
                            next_track()  # Перемикання треку
                    elif event.key == pygame.K_m:
                        mute_music()  # Вимкнення музики

            # Перевірка зіткнень із краями дороги
            cars = [self.car, self.car1, self.car2]
            for car in cars:
                if car.collide(self.roads.contour_mask):
                    car.bounce()  # Відштовхування від країв

            self.bot.move()  # Рух бота
            clock.tick(500)  # Обмеження FPS до 500

        pygame.quit()  # Завершення роботи Pygame

    def show_menu(self):
        """
        Відображення головного меню гри.

        Цей метод малює меню та обробляє взаємодію з кнопками (старт, опції, рейтинг).
        """
        while self.in_menu:
            self.screen.blit(self.background, (0, 0))  # Малювання фону
            self.menu.draw(self.screen)  # Малювання меню
            pygame.display.update()  # Оновлення екрану

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.in_menu = False
                    pygame.quit()
                    exit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.menu.start_rect.collidepoint(event.pos):
                        overlay_music_in_loop("soundeffects/button_sound.mp3")  # Звук кліку
                        self.in_menu = False
                        self.choosing_mode = True
                        self.show_modes()  # Перехід до вибору режиму
                    elif self.menu.options_rect.collidepoint(event.pos):
                        overlay_music_in_loop("soundeffects/button_sound.mp3")
                        self.menu.show_options(self.screen, self.background)  # Відображення налаштувань
                    elif self.menu.rating_btn_rect.collidepoint(event.pos):
                        overlay_music_in_loop("soundeffects/button_sound.mp3")
                        self.menu.show_rating(self.screen, self.background)  # Відображення рейтингу

    def show_maps(self):
        """
        Відображення меню вибору карти.

        Цей метод дозволяє гравцеві обрати карту для гри.
        """
        while self.choosing_map:
            self.screen.blit(self.background, (0, 0))
            self.maps_page.draw(self.screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.choosing_map = False
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.map_choice = self.maps_page.check_click(event.pos)  # Вибір карти
                    if self.map_choice:
                        self.choose_maps(self.map_choice)  # Ініціалізація обраної карти

    def choose_maps(self, map_choice):
        """
        Ініціалізація обраної карти.

        Args:
            map_choice (str): Назва обраної карти.
        """
        print(f"Selected map: {map_choice}")
        self.roads = Roads(f"img/{map_choice}.jpg", f"img/{map_choice}_edge.png")  # Завантаження карти
        self.choosing_map = False
        if self.mode_choice == 'single':
            self.create_objects_single(map_choice)  # Ініціалізація об'єктів для одиночного режиму
        else:
            self.create_objects_doubles(map_choice)  # Ініціалізація об'єктів для двогравцевого режиму

    def show_cars(self):
        """
        Відображення меню вибору машини.

        Цей метод дозволяє обрати машину для одиночного режиму або переходить до вибору карти для двогравцевого.
        """
        if self.mode_choice == 'doubles':
            self.choosing_car = False
            self.choosing_map = True
            self.show_maps()  # У двогравцевому режимі вибір машини пропускається
        while self.choosing_car:
            self.screen.blit(self.background, (0, 0))
            self.cars_page.draw(self.screen)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.choosing_car = False
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    car_choice = self.cars_page.check_click(event.pos)  # Вибір машини
                    if car_choice:
                        self.choose_cars(car_choice)  # Ініціалізація обраної машини

    def choose_cars(self, car_choice):
        """
        Ініціалізація обраної машини.

        Args:
            car_choice (str): Назва обраної машини.
        """
        print(f"Selected car: {car_choice}")
        self.choosing_car = False
        if car_choice == 'car1':
            self.image = 'img/car1.png'
        elif car_choice == 'car2':
            self.image = 'img/car2.png'
        elif car_choice == 'car3':
            self.image = 'img/car3.png'
        elif car_choice == 'car4':
            self.image = 'img/car4.png'
        else:
            self.image = 'img/car5.png'
        self.choosing_map = True
        self.show_maps()  # Перехід до вибору карти

    def show_modes(self):
        """
        Відображення меню вибору режиму гри (одинарний або двогравцевий).
        """
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
                    self.mode_choice = self.modes_page.check_click(event.pos, self.mode_choice)  # Вибір режиму
                    if self.mode_choice:
                        self.choose_modes()  # Ініціалізація режиму

    def choose_modes(self):
        """Ініціалізація обраного режиму гри."""
        print(f"Selected mode: {self.mode_choice}")
        self.choosing_mode = False
        self.choosing_car = True
        self.show_cars()  # Перехід до вибору машини

    def create_objects_single(self, map_choice):
        """
        Створення об'єктів для одиночного режиму.

        Args:
            map_choice (str): Назва обраної карти.
        """
        if map_choice == 'winter':
            self.finish_location = (275, 230)
            self.finish = Finish('img/finish.png', *self.finish_location, 90, 0.308, "bottom")
            self.car = Cars(1350, 250, 0, 0.75, 270, self.image, 'wasd')
            self.bot = Bots(1350, 287, 0, 0.67, 270, [(1654, 265), (1774, 309), (1822, 391), (1807, 657), 
            (1721, 723), (1575, 681), (1539, 550), (1450, 468), (1317, 500), (1273, 607), (1197, 701), (1036, 739), 
            (990, 815), (956, 929), (890, 990), (497, 1010), (184, 981), (138, 868), (139, 739), (162, 631),
            (225, 564), (384, 550), (637, 549), (727, 485), (739, 365), (644, 289), (268, 285)])
        elif map_choice == 'summer':
            self.finish_location = (183, 985)
            self.finish = Finish('img/finish.png', *self.finish_location, 142, 0.21, "bottom")
            self.car = Cars(1745, 945, 0, 0.5, 52, self.image, 'wasd')
            self.bot = Bots(1755, 925, 0, 0.48, 52, [(1491, 749), (1344, 634), (1243, 555), (1200, 474), (1236, 383), 
            (1308, 282), (1376, 185), (1366, 109), (1293, 62), (1203, 92), (1106, 121), (1024, 90), (944, 110), 
            (858, 163), (759, 132), (671, 144), (591, 228), (492, 381), (475, 475), (541, 545), (695, 643), 
            (792, 598), (796, 505), (764, 401), (812, 328), (903, 332), (938, 378), (934, 446), (901, 525), 
            (942, 606), (1064, 700), (1112, 768), (1102, 847), (1028, 898), (965, 875), (891, 816), (808, 757), 
            (719, 740), (643, 809), (583, 881), (523, 918), (440, 909), (362, 887), (306, 917), (208, 1032)])
        elif map_choice == 'beach':
            self.finish_location = (1488, 993)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.308)
            self.car = Cars(95, 990, 0, 0.75, 270, self.image, 'wasd')
            self.bot = Bots(95, 950, 0, 0.67, 270, [(336, 962), (489, 945), (547, 826), (490, 706), (329, 661), 
            (268, 540), (347, 413), (619, 413), (709, 504), (714, 918), (767, 989), (901, 1005), (973, 921), 
            (1005, 660), (1125, 596), (1248, 530), (1293, 407), (1428, 347), (1529, 414), (1566, 534), 
            (1703, 602), (1808, 671), (1822, 767), (1780, 855), (1657, 894), (1575, 946), (1541, 1028)])
        elif map_choice == 'champions_field':
            self.finish_location = (292, 668)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.37, required_circles=2)
            self.car = Cars(342, 730, 0, 0.99, 180, self.image, 'wasd')
            self.bot = Bots(372, 730, 0, 1, 180, [(376, 853), (458, 908), (557, 952), (706, 931), (861, 943), 
            (1140, 925), (1368, 950), (1499, 884), (1556, 767), (1541, 560), (1565, 337), (1526, 216), 
            (1413, 154), (1200, 158), (927, 136), (661, 154), (441, 162), (355, 282), (342, 428), (340, 700)])
        elif map_choice == 'map2':
            self.finish_location = (128, 400)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.5, required_circles=2)
            self.car = Cars(200, 487, 0, 1.07, 180, self.image, 'wasd')
            self.bot = Bots(240, 487, 0, 0.95, 180, [(230, 770), (306, 907), (670, 943), (918, 882), (1214, 967), 
            (1459, 852), (1557, 602), (1575, 330), (1460, 181), (1220, 81), (1097, 69), (986, 87), (911, 157), 
            (921, 264), (1079, 326), (1207, 395), (1264, 512), (1230, 592), (1094, 651), (752, 636), (625, 538), 
            (639, 338), (639, 175), (572, 110), (427, 119), (301, 168), (227, 242), (186, 419)])
        else:
            self.finish_location = (55, 278)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.53, required_circles=2)
            self.car = Cars(160, 365, 0, 1.1, 180, self.image, 'wasd')
            self.bot = Bots(120, 365, 0, 0.95, 180, [(166, 629), (161, 861), (280, 970), 
            (560, 845), (697, 674), (995, 685), (1225, 561), (1569, 519), (1742, 413), 
            (1665, 242), (1362, 245), (943, 219), (686, 87), (401, 71), (184, 158), (98, 386)])
        self.score = Score("img/coin.png", map_choice)  # Ініціалізація очок для карти

    def create_objects_doubles(self, map_choice):
        """
        Створення об'єктів для двогравцевого режиму.

        Args:
            map_choice (str): Назва обраної карти.
        """
        if map_choice == 'winter':
            self.finish_location = (275, 230)
            self.finish = Finish('img/finish.png', *self.finish_location, 90, 0.308, "bottom")
            self.car1 = Cars(1350, 250, 0, 0.75, 270, 'img/car1.png', 'wasd')
            self.car2 = Cars(1350, 287, 0, 0.75, 270, 'img/car2.png', 'arrows')
        elif map_choice == 'summer':
            self.finish_location = (183, 985)
            self.finish = Finish('img/finish.png', *self.finish_location, 142, 0.21, "bottom")
            self.car1 = Cars(1745, 945, 0, 0.5, 52, 'img/car1.png', 'wasd')
            self.car2 = Cars(1755, 925, 0, 0.5, 52, 'img/car2.png', 'arrows')
        elif map_choice == 'beach':
            self.finish_location = (1488, 993)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.308)
            self.car1 = Cars(95, 990, 0, 0.75, 270, 'img/car1.png', 'wasd')
            self.car2 = Cars(95, 950, 0, 0.75, 270, 'img/car2.png', 'arrows')
        elif map_choice == 'champions_field':
            self.finish_location = (292, 668)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.37, required_circles=2)
            self.car1 = Cars(342, 730, 0, 0.95, 180, 'img/car1.png', 'wasd')
            self.car2 = Cars(372, 730, 0, 0.95, 180, 'img/car2.png', 'arrows')
        elif map_choice == 'map2':
            self.finish_location = (128, 400)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.5, required_circles=2)
            self.car1 = Cars(200, 487, 0, 1.07, 180, 'img/car1.png', 'wasd')
            self.car2 = Cars(240, 487, 0, 1.07, 180, 'img/car2.png', 'arrows')
        else:
            self.finish_location = (55, 278)
            self.finish = Finish('img/finish.png', *self.finish_location, 0, 0.53, required_circles=2)
            self.car1 = Cars(160, 365, 0, 1.1, 180, 'img/car1.png', 'wasd')
            self.car2 = Cars(120, 365, 0, 1.1, 180, 'img/car2.png', 'arrows')

    def handle_pause(self):
        """
        Обробляє стан паузи гри, дозволяючи змінювати налаштування або вийти в головне меню.

        Ця функція викликається, коли гравець натискає ESC під час гри. Вона зупиняє 
        основний ігровий цикл та відображає меню паузи. У меню можна:
        - Відкрити налаштування.
        - Вийти в головне меню.
        - Продовжити гру, натиснувши ESC.

        Returns:
            bool: True, якщо гравець продовжує гру.
                  False, якщо гравець виходить у головне меню або закриває гру.
        """
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.menu.options_rect.collidepoint(event.pos):
                        self.menu.show_options(self.screen, self.background)  # Відкриття налаштувань
                    if self.menu.menu_back_rect.collidepoint(event.pos):
                        return False  # Вихід у головне меню
                if event.type == pygame.QUIT:
                    self.running = False
                    quit()
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return True  # Продовження гри

            # Малювання екрану паузи
            overlay = pygame.Surface(self.aspect_ratio, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Напівпрозорий фон
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.pause_text, self.pause_rect)
            self.screen.blit(self.menu.imageOptions, self.menu.options_rect.topleft)
            self.screen.blit(self.menu.menu_back_bnt, self.menu.menu_back_rect)
            pygame.display.flip()

        return True

if __name__ == "__main__":
    """Запуск гри."""
    game = GameSys()
    game.run()