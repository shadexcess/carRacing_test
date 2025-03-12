import pytest
from game_objects import Cars

def test_reset():
    # Створюємо екземпляр автомобіля з початковими значеннями
    car = Cars(10, 10, 0, 5, 0, "img/ice-cube.png", 'wasd')

    # Змінюємо значення, щоб перевірити, чи reset повертає їх до початкових
    car.x = 100
    car.y = 200
    car.angle = 180
    car.speed = 5.0

    # Викликаємо метод reset
    car.reset()

    # Перевіряємо, чи повернулися значення до початкових
    assert car.x == 10, f"Очікувалось x = 10, отримали {car.x}"
    assert car.y == 20, f"Очікувалось y = 20, отримали {car.y}"
    assert car.angle == 90, f"Очікувалось angle = 90, отримали {car.angle}"
    assert car.speed == 0.01, f"Очікувалось speed = 0.01, отримали {car.speed}"

def test_reset_default_values():
    # Перевіряємо з дефолтними значеннями
    car = Cars()
    
    # Змінюємо значення
    car.x = 50
    car.y = 60
    car.angle = 45
    car.speed = 2.0
    
    # Викликаємо reset
    car.reset()
    
    # Перевіряємо дефолтні значення
    assert car.x == 0
    assert car.y == 0
    assert car.angle == 0
    assert car.speed == 0.01