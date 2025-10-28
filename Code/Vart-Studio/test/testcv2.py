import cv2
import numpy as np

# Максимальные размеры экрана
MAX_WIDTH = 1600
MAX_HEIGHT = 900

# Функция для пропорционального масштабирования изображения
def resize_image(image, max_width, max_height):
    height, width = image.shape[:2]
    # Вычисляем коэффициенты масштабирования по ширине и высоте
    width_ratio = max_width / width
    height_ratio = max_height / height
    # Выбираем минимальный коэффициент, чтобы изображение помещалось полностью
    scale_ratio = min(width_ratio, height_ratio, 1.0)  # Не увеличиваем изображение
    new_width = int(width * scale_ratio)
    new_height = int(height * scale_ratio)
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return resized_image

# Функция, которая будет вызываться при изменении ползунков
def update_image(val):
    # Получаем значения ползунков
    low_threshold = cv2.getTrackbarPos('Low Threshold', 'Canny Edge Detection')
    high_threshold = cv2.getTrackbarPos('High Threshold', 'Canny Edge Detection')
    bw_threshold = cv2.getTrackbarPos('B/W Threshold', 'Canny Edge Detection')

    # Применяем пороговое преобразование к серому изображению
    # _, bw_image = cv2.threshold(gray_image, bw_threshold, 255, cv2.THRESH_BINARY)

    # Применяем Canny с текущими значениями порогов
    edges = cv2.Canny(gray_image, low_threshold, high_threshold)

    # Показываем изображение с контурами
    cv2.imshow('Canny Edge Detection', edges)

# Загружаем изображение
image_path = 'cube.png'  # Укажите путь к вашему изображению
original_image = cv2.imread(image_path)

if original_image is None:
    print("Не удалось загрузить изображение.")
    exit()

# Масштабируем изображение пропорционально
original_image = resize_image(original_image, MAX_WIDTH, MAX_HEIGHT)

# Преобразуем в оттенки серого
gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

# Создаем окно для отображения
cv2.namedWindow('Canny Edge Detection', cv2.WINDOW_AUTOSIZE)

# Создаем ползунки для настройки порогов
cv2.createTrackbar('Low Threshold', 'Canny Edge Detection', 0, 255, update_image)
cv2.createTrackbar('High Threshold', 'Canny Edge Detection', 0, 255, update_image)
cv2.createTrackbar('B/W Threshold', 'Canny Edge Detection', 0, 255, update_image)

# Устанавливаем начальные значения ползунков
cv2.setTrackbarPos('Low Threshold', 'Canny Edge Detection', 100)
cv2.setTrackbarPos('High Threshold', 'Canny Edge Detection', 200)
cv2.setTrackbarPos('B/W Threshold', 'Canny Edge Detection', 127)  # Начальный порог для ЧБ

# Изначально отображаем контуры
update_image(0)

# Ожидаем нажатия клавиши для закрытия окна
while True:
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # Нажатие клавиши Esc для выхода
        break

cv2.destroyAllWindows()