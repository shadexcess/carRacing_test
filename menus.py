import pygame
from abc import ABC, abstractmethod
from music import *
import os
import time

class Menu:
    """
    Клас Menu представляє головне меню гри.
    Відповідає за відображення кнопок, зворотний відлік та опції гри.
    """
    def __init__(self, x, y):
        """
        Ініціалізує об'єкт головного меню.

        :param x: Координата X центру меню.
        :param y: Координата Y центру меню.
        """
        self.x = x
        self.y = y
        self.imageStart = self.load_image("img/start.png", (289, 143))  # Кнопка "Старт"
        self.imageOptions = self.load_image("img/options.png", (289, 143))  # Кнопка "Опції"
        self.imageBack = self.load_image("img/back.png", (288, 103))  # Кнопка "Назад"
        self.leadorboard = self.load_image("img/leaderboard.png", (1234, 817))  # Таблиця лідерів
        self.rating_btn = self.load_image("img/rating_btn.png", (287, 141))  # Кнопка "Рейтинг"
        self.menu_back_bnt = self.load_image("img/menu_btn.png", (232, 83))  # Кнопка повернення в меню
        self.on_music = self.load_image("img/on_music.png", (288, 103))  # Кнопка увімкнення музики
        self.off_music = self.load_image("img/off_music.png", (287, 103))  # Кнопка вимкнення музики
        self.leadorboard_rect = self.leadorboard.get_rect(topleft=(x - 460, y - 400))  # Прямокутник таблиці лідерів
        self.start_rect = self.imageStart.get_rect(topleft=(x, y - 75))  # Прямокутник кнопки "Старт"
        self.options_rect = self.imageOptions.get_rect(topleft=(x, y + 275))  # Прямокутник кнопки "Опції"
        self.back_rect = self.imageBack.get_rect(topleft=(x, y + 400))  # Прямокутник кнопки "Назад" (опції)
        self.back_rect2 = self.imageBack.get_rect(topleft=(x, y + 500))  # Прямокутник кнопки "Назад" (рейтинг)
        self.rating_btn_rect = self.rating_btn.get_rect(topleft=(x, y + 100))  # Прямокутник кнопки "Рейтинг"
        self.menu_back_rect = self.menu_back_bnt.get_rect(topleft=(x - 790, y - 440))  # Прямокутник повернення в меню
        self.on_music_rect = self.on_music.get_rect(topleft=(x, y))  # Прямокутник кнопки увімкнення музики
        self.off_music_rect = self.off_music.get_rect(topleft=(x, y + 140))  # Прямокутник кнопки вимкнення музики
        
        # Параметри повзунка гучності
        self.slider_x = self.off_music_rect.x
        self.slider_y = self.off_music_rect.y + self.off_music_rect.height + 50
        self.slider_width = 288
        self.slider_height = 10
        self.slider_knob_radius = 10
        self.volume = 0.5  # Початкова гучність (0.0 - 1.0)
        self.knob_x = self.slider_x + int(self.volume * self.slider_width)  # Позиція повзунка
        self.dragging = False  # Прапорець перетягування повзунка

    def load_image(self, path, size):
        """
        Завантажує та масштабує зображення.

        :param path: Шлях до файлу зображення.
        :param size: Кортеж із шириною та висотою для масштабування.
        :return: Масштабоване зображення Pygame.
        """
        img = pygame.image.load(path)
        return pygame.transform.scale(img, size)

    def draw(self, screen):
        """
        Малює головне меню на екрані.

        :param screen: Поверхня Pygame для відображення.
        """
        screen.blit(self.imageStart, self.start_rect.topleft)
        screen.blit(self.imageOptions, self.options_rect.topleft)
        screen.blit(self.rating_btn, self.rating_btn_rect.topleft)

    def countdown(self, countdown_images, screen, roads, car, car1, car2, bot, aspect_ratio, mode_choice):
        """
        Відображає зворотний відлік перед початком гри.

        :param countdown_images: Список зображень для відліку (3, 2, 1, GO).
        :param screen: Поверхня Pygame для відображення.
        :param roads: Об'єкт класу Roads для малювання дороги.
        :param car: Автомобіль для одиночного режиму.
        :param car1: Перший автомобіль для двогравцевого режиму.
        :param car2: Другий автомобіль для двогравцевого режиму.
        :param bot: Бот для одиночного режиму.
        :param aspect_ratio: Розмір екрану (ширина, висота).
        :param mode_choice: Режим гри ('single' або 'doubles').
        """
        overlay_music_in_loop("soundeffects/321go.mp3")  # Відтворення звуку відліку
        for img in countdown_images:
            screen.fill((0, 0, 0))  # Очищення екрану
            roads.draw(screen)  # Малювання дороги
            if mode_choice == 'single':
                car.draw(screen)  # Малювання гравця
                bot.draw(screen)  # Малювання бота
            else:
                car1.draw(screen)  # Малювання першого гравця
                car2.draw(screen)  # Малювання другого гравця
            img_rect = img.get_rect(center=(aspect_ratio[0] // 2, aspect_ratio[1] // 2))
            screen.blit(img, img_rect)
            pygame.display.update()
            time.sleep(1)  # Затримка 1 секунда між зображеннями

    def show_options(self, screen, background):
        """
        Відображає меню налаштувань гри.

        :param screen: Поверхня Pygame для відображення.
        :param background: Фонове зображення.
        """
        options_active = True
        pause_font = pygame.font.Font("fonts/AveriaSansLibre-Bold.ttf", 36)
        pause_text = pause_font.render('Key bindings:', True, (255, 255, 255))
        pause_text1 = pause_font.render('ESC - pause the game', True, (255, 255, 255))
        pause_text2 = pause_font.render('M - turn music on/off', True, (255, 255, 255))
        pause_text3 = pause_font.render('N - play the next audio track', True, (255, 255, 255))
        pause_rect = pause_text.get_rect(topleft=(835, 200))
        pause_rect1 = pause_text1.get_rect(topleft=(770, 265))
        pause_rect2 = pause_text2.get_rect(topleft=(772, 315))
        pause_rect3 = pause_text3.get_rect(topleft=(720, 365))

        while options_active:
            screen.fill((0, 0, 0))
            screen.blit(background, (0, 0))
            screen.blit(self.imageBack, self.back_rect)
            screen.blit(self.on_music, self.on_music_rect)
            screen.blit(self.off_music, self.off_music_rect)
            screen.blit(pause_text, pause_rect)
            screen.blit(pause_text1, pause_rect1)
            screen.blit(pause_text2, pause_rect2)
            screen.blit(pause_text3, pause_rect3)

            # Малювання повзунка гучності
            pygame.draw.rect(screen, (200, 200, 200), (self.slider_x, self.slider_y, self.slider_width, self.slider_height))
            pygame.draw.circle(screen, (59, 59, 59), (self.knob_x, self.slider_y + self.slider_height // 2), self.slider_knob_radius)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    options_active = False
                    pygame.quit()
                    exit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if self.on_music_rect.collidepoint(event.pos):
                            overlay_music_in_loop("soundeffects/button_sound.mp3")
                            start_music()  # Увімкнення музики
                        if self.off_music_rect.collidepoint(event.pos):
                            overlay_music_in_loop("soundeffects/button_sound.mp3")
                            stop_music()  # Вимкнення музики
                        if self.back_rect.collidepoint(event.pos):
                            overlay_music_in_loop("soundeffects/button_sound.mp3")
                            options_active = False
                            return
                        # Перевірка кліку на повзунок
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

    def show_rating(self, screen, background):
        """
        Відображає таблицю лідерів.

        :param screen: Поверхня Pygame для відображення.
        :param background: Фонове зображення.
        """
        rating_active = True
        while rating_active:
            screen.fill((0, 0, 0))
            screen.blit(background, (0, 0))
            screen.blit(self.imageBack, self.back_rect2)
            screen.blit(self.leadorboard, self.leadorboard_rect)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    rating_active = False
                    pygame.quit()
                    exit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.back_rect2.collidepoint(event.pos):
                        overlay_music_in_loop("soundeffects/button_sound.mp3")
                        return

class ConfigurationMenu(ABC):
    """
    Абстрактний базовий клас для конфігураційних меню (карти, машини, режими).
    """
    def __init__(self, x, y):
        """
        Ініціалізує базові параметри конфігураційного меню.

        :param x: Координата X центру меню.
        :param y: Координата Y центру меню.
        """
        self.x = x
        self.y = y
        self.font = pygame.font.Font("fonts/AveriaSansLibre-Bold.ttf", 36)  # Шрифт для тексту
        self.title_font = pygame.font.Font("fonts/AveriaSansLibre-Bold.ttf", 56)  # Шрифт для заголовків

    def load_image(self, path):
        """
        Завантажує зображення.

        :param path: Шлях до файлу зображення.
        :return: Завантажене зображення Pygame.
        """
        return pygame.image.load(path)

    def draw_text(self, text, x, y, screen, font=None):
        """
        Малює текст на екрані.

        :param text: Текст для відображення.
        :param x: Координата X центру тексту.
        :param y: Координата Y центру тексту.
        :param screen: Поверхня Pygame для відображення.
        :param font: Шрифт (за замовчуванням None, використовується self.font).
        """
        if font is None:
            font = self.font
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

    @abstractmethod
    def draw(self):
        """Абстрактний метод для малювання меню."""
        pass

    @abstractmethod
    def check_click(self):
        """Абстрактний метод для обробки кліків."""
        pass

class MapsMenu(ConfigurationMenu):
    """
    Клас MapsMenu представляє меню вибору карт.
    """
    def __init__(self, x, y, score, file_path="purchased_maps.txt"):
        """
        Ініціалізує меню вибору карт.

        :param x: Координата X центру меню.
        :param y: Координата Y центру меню.
        :param score: Об'єкт класу Score для управління очками.
        :param file_path: Шлях до файлу з купленими картами.
        """
        super().__init__(x, y)
        self.file_path = file_path
        self.score = score
        self.purchased_maps = self.load_purchased_maps()
        self.image_map3 = self.load_image("img/map3_preview.png")
        self.image_map2 = self.load_image("img/map2_preview.png")
        self.image_beach = self.load_image("img/beach_preview.png")
        self.image_winter = self.load_image("img/winter_preview.png")
        self.image_summer = self.load_image("img/summer_preview.png")
        self.image_champions_field = self.load_image("img/champions_field_preview.png")
        self.image_beach_lock = self.load_image("img/beach_lock.png")
        self.image_winter_lock = self.load_image("img/winter_lock.png")
        self.image_summer_lock = self.load_image("img/summer_lock.png")
        self.image_champions_field_lock = self.load_image("img/champions_field_lock.png")
        self.buy_image = self.load_image("img/5000.png")
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
        """
        Завантажує список куплених карт із файлу.

        :return: Множина назв куплених карт.
        """
        if not os.path.exists(self.file_path):
            return set()
        with open(self.file_path, "r") as file:
            return set(file.read().splitlines())

    def save_purchased_maps(self):
        """Зберігає список куплених карт у файл."""
        with open(self.file_path, "w") as file:
            file.write("\n".join(self.purchased_maps))

    def purchase_map(self, map_name):
        """
        Додає карту до списку куплених.

        :param map_name: Назва карти.
        """
        if map_name not in self.purchased_maps:
            self.purchased_maps.add(map_name)
            self.save_purchased_maps()

    def draw(self, screen):
        """
        Малює меню вибору карт на екрані.

        :param screen: Поверхня Pygame для відображення.
        """
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
        """
        Обробляє клік миші у меню карт.

        :param pos: Координати кліку (x, y).
        :return: Назва вибраної карти або None.
        """
        if self.buy_image_rect.collidepoint(pos):
            if self.score.purchase_item("beach", "map"):
                overlay_music_in_loop("soundeffects/purchase.mp3")
                self.purchased_maps.add("beach")
                self.save_purchased_maps()
        elif self.buy_image_rect2.collidepoint(pos):
            if self.score.purchase_item("summer", "map"):
                overlay_music_in_loop("soundeffects/purchase.mp3")
                self.purchased_maps.add("summer")
                self.save_purchased_maps()
        elif self.buy_image_rect3.collidepoint(pos):
            if self.score.purchase_item("champions_field", "map"):
                overlay_music_in_loop("soundeffects/purchase.mp3")
                self.purchased_maps.add("champions_field")
                self.save_purchased_maps()
        elif self.buy_image_rect4.collidepoint(pos):
            if self.score.purchase_item("winter", "map"):
                overlay_music_in_loop("soundeffects/purchase.mp3")
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
    """
    Клас CarsMenu представляє меню вибору автомобілів.
    """
    def __init__(self, x, y, score, file_path="purchased_cars.txt"):
        """
        Ініціалізує меню вибору автомобілів.

        :param x: Координата X центру меню.
        :param y: Координата Y центру меню.
        :param score: Об'єкт класу Score для управління очками.
        :param file_path: Шлях до файлу з купленими автомобілями.
        """
        super().__init__(x, y)
        self.file_path = file_path
        self.score = score
        self.purchased_cars = self.load_purchased_cars()
        self.image_car1 = self.load_image("img/car1_preview.png")
        self.image_car2 = self.load_image("img/car2_preview.png")
        self.image_car3 = self.load_image("img/car3_preview.png")
        self.image_car4 = self.load_image("img/car4_preview.png")
        self.image_car5 = self.load_image("img/car5_preview.png")
        self.image_car1_lock = self.load_image("img/car1_lock.png")
        self.image_car2_lock = self.load_image("img/car2_lock.png")
        self.image_car3_lock = self.load_image("img/car3_lock.png")
        self.buy_image = self.load_image("img/3000.png")
        self.car1_rect = self.image_car1.get_rect(topleft=(x + 1200, y + 60))
        self.car2_rect = self.image_car2.get_rect(topleft=(x + 600, y + 60))
        self.car3_rect = self.image_car3.get_rect(topleft=(x + 900, y + 550))
        self.car4_rect = self.image_car4.get_rect(topleft=(x + 300, y + 550))
        self.car5_rect = self.image_car5.get_rect(topleft=(x, y + 60))
        self.buy_image_rect = self.buy_image.get_rect(topleft=(x + 1325, y + 400))
        self.buy_image2_rect = self.buy_image.get_rect(topleft=(x + 725, y + 400))
        self.buy_image3_rect = self.buy_image.get_rect(topleft=(x + 1025, y + 890))

    def load_purchased_cars(self):
        """
        Завантажує список куплених автомобілів із файлу.

        :return: Множина назв куплених автомобілів.
        """
        if not os.path.exists(self.file_path):
            return set()
        with open(self.file_path, "r") as file:
            return set(file.read().splitlines())

    def save_purchased_cars(self):
        """Зберігає список куплених автомобілів у файл."""
        with open(self.file_path, "w") as file:
            file.write("\n".join(self.purchased_cars))

    def purchase_car(self, car_name):
        """
        Додає автомобіль до списку куплених.

        :param car_name: Назва автомобіля.
        """
        if car_name not in self.purchased_cars:
            self.purchased_cars.add(car_name)
            self.save_purchased_cars()

    def draw(self, screen):
        """
        Малює меню вибору автомобілів на екрані.

        :param screen: Поверхня Pygame для відображення.
        """
        screen.blit(self.image_car1 if 'car1' in self.purchased_cars else self.image_car1_lock, self.car1_rect.topleft)
        screen.blit(self.image_car2 if 'car2' in self.purchased_cars else self.image_car2_lock, self.car2_rect.topleft)
        screen.blit(self.image_car3 if 'car3' in self.purchased_cars else self.image_car3_lock, self.car3_rect.topleft)
        screen.blit(self.image_car4, self.car4_rect.topleft)
        screen.blit(self.image_car5, self.car5_rect.topleft)

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
        """
        Обробляє клік миші у меню автомобілів.

        :param pos: Координати кліку (x, y).
        :return: Назва вибраного автомобіля або None.
        """
        if self.buy_image_rect.collidepoint(pos):
            if self.score.purchase_item("car1", "car"):
                overlay_music_in_loop("soundeffects/purchase.mp3")
                self.purchased_cars.add("car1")
                self.save_purchased_cars()
        elif self.buy_image2_rect.collidepoint(pos):
            if self.score.purchase_item("car2", "car"):
                overlay_music_in_loop("soundeffects/purchase.mp3")
                self.purchased_cars.add("car2")
                self.save_purchased_cars()
        elif self.buy_image3_rect.collidepoint(pos):
            if self.score.purchase_item("car3", "car"):
                overlay_music_in_loop("soundeffects/purchase.mp3")
                self.purchased_cars.add("car3")
                self.save_purchased_cars()

        if self.car1_rect.collidepoint(pos) and "car1" in self.purchased_cars:
            overlay_music_in_loop("soundeffects/button_sound.mp3")
            return "car1"
        elif self.car2_rect.collidepoint(pos) and "car2" in self.purchased_cars:
            overlay_music_in_loop("soundeffects/button_sound.mp3")
            return "car2"
        elif self.car3_rect.collidepoint(pos) and "car3" in self.purchased_cars:
            overlay_music_in_loop("soundeffects/button_sound.mp3")
            return "car3"
        elif self.car4_rect.collidepoint(pos):
            overlay_music_in_loop("soundeffects/button_sound.mp3")
            return "car4"
        elif self.car5_rect.collidepoint(pos):
            overlay_music_in_loop("soundeffects/button_sound.mp3")
            return "car5"
        return None

class ModesMenu(ConfigurationMenu):
    """
    Клас ModesMenu представляє меню вибору режимів гри.
    """
    def __init__(self, x, y):
        """
        Ініціалізує меню вибору режимів гри.

        :param x: Координата X центру меню.
        :param y: Координата Y центру меню.
        """
        super().__init__(x, y)
        self.image_single = self.load_image("img/single.png")
        self.image_doubles = self.load_image("img/doubles.png")
        self.single_rect = self.image_single.get_rect(topleft=(x - 40, y + 250))
        self.doubles_rect = self.image_doubles.get_rect(topleft=(x + 890, y + 250))

    def draw(self, screen):
        """
        Малює меню вибору режимів на екрані.

        :param screen: Поверхня Pygame для відображення.
        """
        screen.blit(self.image_single, self.single_rect.topleft)
        screen.blit(self.image_doubles, self.doubles_rect.topleft)
        self.draw_text("Select the game mode:", self.x + 855, self.y + 50, screen, self.title_font)
        self.draw_text("Single", self.single_rect.centerx, self.single_rect.top - 30, screen)
        self.draw_text("Doubles", self.doubles_rect.centerx, self.doubles_rect.top - 30, screen)

    def check_click(self, pos, mode_choice):
        """
        Обробляє клік миші у меню режимів.

        :param pos: Координати кліку (x, y).
        :param mode_choice: Поточний режим гри.
        :return: Новий режим гри або None.
        """
        if self.single_rect.collidepoint(pos):
            overlay_music_in_loop("soundeffects/button_sound.mp3")
            mode_choice = 'single'
            return mode_choice
        elif self.doubles_rect.collidepoint(pos):
            overlay_music_in_loop("soundeffects/button_sound.mp3")
            mode_choice = 'doubles'
            return mode_choice
        return None