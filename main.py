import yaml
import cv2
import numpy as np
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import json


def load_config(yaml_file):
    with open(yaml_file, 'r') as file:
        config = yaml.safe_load(file)
    return config

def analyze_image(image_path, config):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Изображение не загружено, проверьте путь к файлу")
    height, width = image.shape[:2]

    # Преобразование изображения в HSV
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Определение диапазона зелёного цвета
    lower_green = np.array([64, 239, 220])
    upper_green = np.array([76, 255, 255])

    # Создание маски для зелёного цвета
    image = cv2.inRange(hsv_image, lower_green, upper_green)

    # Получение не нулевых координат (положение пятна)
    coords = np.column_stack(np.where(image > 0)) - np.array([height / 2, width / 2])
    if len(coords) == 0:
        raise ValueError("Не найдено пятно на изображении")

    # Вычисление центра пятна (среднего положения)
    position = np.mean(coords, axis=0)

    # Вычисление стандартного отклонения
    std_dev = np.std(coords)

    # Вычисление дисперсии
    dispersion = np.var(coords)

    print(position, std_dev, dispersion)

    return {
        "position": position.tolist(),
        "std_dev": std_dev.tolist(),
        "dispersion": dispersion.tolist()
    }

def test_position(expected_position, actual_position):
    return np.allclose(expected_position, actual_position, atol=1)

def test_std_dev(expected_std_dev, actual_std_dev):
    return np.allclose(expected_std_dev, actual_std_dev, atol=1e-1)

def test_dispersion(expected_dispersion, actual_dispersion):
    return np.allclose(expected_dispersion, actual_dispersion, atol=1e-1)

def send_metrics_to_influxdb(data, measurement_name="image_analysis"):
    token = "kMwnL1L-eWZPg52U61-2v0OlqpvrOLxg8RZvWXOOZlxBRzBOXkTt3bEe3fI8O8wuy-fLy5Cwe4l_WDWg3j45zw=="
    org = "2"
    url = "https://us-east-1-1.aws.cloud2.influxdata.com"
    bucket = "Akinin"

    client = influxdb_client.InfluxDBClient(
        url=url,
        token=token,
        org=org
    )

    write_api = client.write_api(write_options=SYNCHRONOUS)
    p = influxdb_client.Point("test_measurement").field("position_x", data["position"][0]).field("position_y", data["position"][1]).field("std_dev", data["std_dev"]).field("dispersion", data["dispersion"])
    write_api.write(bucket=bucket, org=org, record=p)


def save_results_to_json(results, output_file):
    with open(output_file, 'w') as file:
        json.dump(results, file, indent=4)


def save_projection_to_txt(image_path, output_file):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Изображение не загружено, проверьте путь к файлу")

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_green = np.array([64, 239, 220])
    upper_green = np.array([76, 255, 255])

    image = cv2.inRange(hsv_image, lower_green, upper_green)

    projection_x = np.count_nonzero(image, axis=0)
    projection_y = np.count_nonzero(image, axis=1)

    with open(output_file, 'w') as file:
        file.write("Projection on X-axis:\n")
        file.write(" ".join(map(str, projection_x)) + "\n\n")
        file.write("Projection on Y-axis:\n")
        file.write(" ".join(map(str, projection_y)) + "\n")

def main():
    config = load_config("config.yaml")
    image_analysis_results = analyze_image("image.png", config)

    # Тестирование
    try:
        assert test_position(config['position'], image_analysis_results['position'])
        assert test_std_dev(config['std'], image_analysis_results['std_dev'])
        assert test_dispersion(config['dispersion'], image_analysis_results['dispersion'])
    except:
        print("Большое расхождение с валидными значениями! ([0, 0] 10 10) ")

    # Отправка метрик в базу данных
    send_metrics_to_influxdb(image_analysis_results)

    # Сохранение результатов
    save_results_to_json(image_analysis_results, "results.json")
    save_projection_to_txt("image.png", "projections.txt")


if __name__ == "__main__":
    main()
