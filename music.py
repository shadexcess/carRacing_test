import pygame
import threading

pygame.init()

# Глобальні змінні для управління музикою
music_playing = threading.Event()  # Подія для контролю відтворення музики
music_playing.set()  # Увімкнення відтворення за замовчуванням
music_thread = None  # Потік для фонового відтворення музики
current_track_index = 0  # Індекс поточного треку
soundtracks = []  # Список доступних саундтреків
effect_music_channel = pygame.mixer.Channel(0)  # Канал для звукових ефектів

def upload_soundtracks():
    """
    Завантажує список саундтреків у глобальну змінну soundtracks.

    Якщо список порожній, заповнює його файлами від track1.mp3 до track14.mp3.
    
    :return: Список саундтреків.
    """
    global soundtracks
    if not soundtracks:
        soundtracks = [f"music/track{i}.mp3" for i in range(1, 15)]  # Генерація імен файлів
    return soundtracks

def overlay_music_in_loop_infinity():
    """
    Відтворює саундтреки у фоновому потоці в безкінечному циклі.

    Завантажує та відтворює треки з глобального списку soundtracks,
    перемикаючись на наступний після завершення поточного.
    """
    global current_track_index
    soundtracks = upload_soundtracks()  # Завантаження саундтреків
    while music_playing.is_set():  # Поки музика активна
        pygame.mixer.music.load(soundtracks[current_track_index])  # Завантаження треку
        pygame.mixer.music.set_volume(0.5)  # Встановлення гучності
        pygame.mixer.music.play(1)  # Відтворення одного разу

        # Очікування завершення відтворення
        while pygame.mixer.music.get_busy() and music_playing.is_set():
            pygame.time.delay(100)  # Затримка для зменшення навантаження

        if not music_playing.is_set():
            break  # Вихід із циклу, якщо музику вимкнено

        current_track_index = (current_track_index + 1) % len(soundtracks)  # Перехід до наступного треку

def overlay_music_in_loop(background_audio_path):
    """
    Відтворює звуковий ефект один раз на окремому каналі.

    :param background_audio_path: Шлях до файлу звукового ефекту.
    """
    effect_music_channel.play(pygame.mixer.Sound(background_audio_path), loops=0, maxtime=0, fade_ms=0)

def stop_music():
    """Зупиняє відтворення фонової музики."""
    pygame.mixer.music.pause()  # Пауза поточного треку
    music_playing.clear()  # Вимикання прапорця відтворення

def start_music():
    """
    Запускає або відновлює відтворення фонової музики.

    Якщо потік не існує або завершений, створює новий для відтворення.
    """
    global music_thread
    music_playing.set()  # Увімкнення прапорця відтворення
    if music_thread is None or not music_thread.is_alive():  # Перевірка стану потоку
        music_thread = threading.Thread(target=overlay_music_in_loop_infinity, daemon=True)  # Створення нового потоку
        music_thread.start()  # Запуск потоку

def next_track():
    """
    Перемикає відтворення на наступний трек у списку.

    Зупиняє поточний трек і запускає наступний, якщо музика активна.
    """
    global current_track_index
    if music_playing.is_set():  # Якщо музика відтворюється
        current_track_index = (current_track_index + 1) % len(upload_soundtracks())  # Оновлення індексу
        pygame.mixer.music.stop()  # Зупинка поточного треку
        pygame.mixer.music.load(soundtracks[current_track_index])  # Завантаження нового треку
        pygame.mixer.music.play(1)  # Відтворення нового треку

def mute_music():
    """
    Перемикає стан відтворення музики: увімкнено/вимкнено.

    Якщо музика грає, зупиняє її; якщо зупинена, запускає.
    """
    if music_playing.is_set():
        stop_music()  # Зупинка музики
    else:
        start_music()  # Запуск музики

def stop_sound():
    """Зупиняє відтворення звукового ефекту на каналі effect_music_channel."""
    effect_music_channel.stop()