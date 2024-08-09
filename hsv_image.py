import cv2
import numpy as np

def nothing(*arg):
    pass

# Создаем главное окно и окно настроек
cv2.namedWindow("result")
cv2.namedWindow("settings")

# Загружаем изображение из файла
img = cv2.imread('image.png')
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Создаем 6 бегунков для настройки начального и конечного цвета фильтра
cv2.createTrackbar('h1', 'settings', 0, 255, nothing)
cv2.createTrackbar('s1', 'settings', 0, 255, nothing)
cv2.createTrackbar('v1', 'settings', 0, 255, nothing)
cv2.createTrackbar('h2', 'settings', 255, 255, nothing)
cv2.createTrackbar('s2', 'settings', 255, 255, nothing)
cv2.createTrackbar('v2', 'settings', 255, 255, nothing)

while True:
    # Считываем значения бегунков
    h1 = cv2.getTrackbarPos('h1', 'settings')
    s1 = cv2.getTrackbarPos('s1', 'settings')
    v1 = cv2.getTrackbarPos('v1', 'settings')
    h2 = cv2.getTrackbarPos('h2', 'settings')
    s2 = cv2.getTrackbarPos('s2', 'settings')
    v2 = cv2.getTrackbarPos('v2', 'settings')

    # Формируем начальный и конечный цвет фильтра
    h_min = np.array((h1, s1, v1), np.uint8)
    h_max = np.array((h2, s2, v2), np.uint8)

    # Накладываем фильтр на изображение в модели HSV
    thresh = cv2.inRange(hsv, h_min, h_max)

    # Отображаем результат
    cv2.imshow('result', thresh)

    ch = cv2.waitKey(5)
    if ch == 27:
        break

cv2.destroyAllWindows()
