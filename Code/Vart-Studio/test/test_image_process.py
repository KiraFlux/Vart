from typing import Iterable
from typing import Tuple

import cv2
import numpy as np
from scipy.spatial import ConvexHull

Matrix = np.ndarray
Vertices = Tuple[Iterable[float], Iterable[float]]


class VertexGenerator:
    @classmethod
    def fromImage(cls, image_path: str, canny_threshold1: int = 100, canny_threshold2: int = 120) -> Vertices:
        """
        Преобразует изображение в последовательность вершин, используя Canny edge detection.

        Args:
            image_path: Путь к изображению.
            canny_threshold1: Первый порог для детектора Canny.
            canny_threshold2: Второй порог для детектора Canny.

        Returns:
            Кортеж (x_coords, y_coords) с координатами вершин.
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Не удалось загрузить изображение: {image_path}")

        # Используем Canny для обнаружения границ
        edges = cv2.Canny(img, canny_threshold1, canny_threshold2)

        # Находим координаты пикселей, где есть границы
        y_coords, x_coords = np.where(edges != 0)

        # Объединяем координаты в список точек (x, y)
        points = list(zip(x_coords, y_coords))

        if not points:
            return [], []

        # Сортируем точки одним из методов
        sorted_points = cls._sort_points_nearest_neighbor_directional(points)
        # sorted_points = cls._sort_points_convex_hull(points)

        x_coords, y_coords = zip(*sorted_points)
        return list(x_coords), list(y_coords)

    @classmethod
    def _sort_points_nearest_neighbor_directional(cls, points: list) -> list:
        """
        Сортировка точек на основе алгоритма ближайшего соседа с учетом направления.

        Args:
            points: Список точек в формате [(x1, y1), (x2, y2), ...].

        Returns:
            Отсортированный список точек.
        """
        if not points:
            return []

        sorted_points = []
        remaining_points = points.copy()

        # Находим самую левую верхнюю точку
        current_point = min(remaining_points, key=lambda p: (p[0], p[1]))
        sorted_points.append(current_point)
        remaining_points.remove(current_point)

        # Задаем начальное направление (вправо)
        direction = np.array([1, 0])

        while remaining_points:
            # Ищем ближайшую точку с учетом направления
            nearest_point, best_angle = cls._find_nearest_directional(current_point, remaining_points, direction)

            # Обновляем направление
            direction = np.array([nearest_point[0] - current_point[0], nearest_point[1] - current_point[1]])

            current_point = nearest_point
            sorted_points.append(current_point)
            remaining_points.remove(current_point)

        return sorted_points

    @classmethod
    def _find_nearest_directional(cls, current_point: tuple, remaining_points: list, direction: np.ndarray) -> tuple:
        """
        Находит среди remaining_points точку, ближайшую к current_point, с учетом direction

        Args:
            current_point: Текущая точка (x, y).
            remaining_points: Список оставшихся точек.
            direction: Направление (вектор), задающее приоритет.

        Returns:
            Кортеж (nearest_point, best_angle), где:
            - nearest_point: Ближайшая точка с учетом направления.
            - best_angle: Угол между direction и вектором от current_point к nearest_point.
        """
        # Векторизуем вычисления
        current_point_arr = np.array(current_point)
        remaining_points_arr = np.array(remaining_points)

        # Векторы от current_point ко всем remaining_points
        vectors_to_points = remaining_points_arr - current_point_arr

        # Нормализуем векторы
        vector_lengths = np.linalg.norm(vectors_to_points, axis=1)
        normalized_vectors = vectors_to_points / vector_lengths[:, np.newaxis]

        # Нормализуем direction
        direction_len = np.linalg.norm(direction)
        normalized_direction = direction / direction_len

        # Скалярное произведение для вычисления косинусов углов
        dot_products = np.dot(normalized_vectors, normalized_direction)

        # Углы в радианах
        angles = np.arccos(dot_products)

        # Взвешенные расстояния (чем меньше угол, тем меньше вес)
        distances = np.linalg.norm(remaining_points_arr - current_point_arr, axis=1)
        weighted_distances = distances * (1 + angles)  # Чем меньше угол, тем лучше.

        # Индекс лучшей точки
        best_index = np.argmin(weighted_distances)
        nearest_point = tuple(remaining_points_arr[best_index])
        best_angle = angles[best_index]

        return nearest_point, best_angle

    @classmethod
    def _sort_points_convex_hull(cls, points: list) -> list:
        """
        Сортировка точек с использованием алгоритма выпуклой оболочки.

        Args:
            points: Список точек в формате [(x1, y1), (x2, y2), ...].

        Returns:
            Отсортированный список точек.
        """
        if not points:
            return []

        # Находим выпуклую оболочку
        points_array = np.array(points)
        hull = ConvexHull(points_array)

        # Точки выпуклой оболочки
        hull_points = points_array[hull.vertices]

        # Сортируем точки по часовой стрелке
        sorted_hull_points = cls._sort_points_clockwise(hull_points)

        # Добавляем внутренние точки (не из выпуклой оболочки)
        inner_points = [p for p in points if tuple(p) not in map(tuple, sorted_hull_points)]
        sorted_points = list(map(tuple, sorted_hull_points)) + cls._sort_inner_points(sorted_hull_points, inner_points)

        return sorted_points

    @classmethod
    def _sort_points_clockwise(cls, points: np.ndarray) -> np.ndarray:
        """
        Сортирует точки по часовой стрелке относительно центра.

        Args:
            points: Массив точек в формате [[x1, y1], [x2, y2], ...].

        Returns:
            Массив точек, отсортированных по часовой стрелке.
        """
        center = np.mean(points, axis=0)
        angles = np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0])
        sorted_indices = np.argsort(angles)
        return points[sorted_indices]

    @classmethod
    def _sort_inner_points(cls, hull_points: list, inner_points: list) -> list:
        """
        Сортирует внутренние точки, добавляя их к ближайшему сегменту выпуклой оболочки.

        Args:
            hull_points: Список точек выпуклой оболочки.
            inner_points: Список внутренних точек.

        Returns:
            Список внутренних точек, отсортированных в порядке, соответствующем обходу выпуклой оболочки.
        """
        if not inner_points:
            return []

        sorted_inner_points = []
        for point in inner_points:
            min_dist = float('inf')
            nearest_segment_index = -1
            for i in range(len(hull_points)):
                p1 = hull_points[i]
                p2 = hull_points[(i + 1) % len(hull_points)]
                dist = cls._point_to_segment_distance(point, p1, p2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_segment_index = i

            sorted_inner_points.append((nearest_segment_index, point))

        sorted_inner_points.sort(key=lambda x: x[0])
        return [p[1] for p in sorted_inner_points]

    @staticmethod
    def _point_to_segment_distance(point: tuple, p1: tuple, p2: tuple) -> float:
        """
        Вычисляет расстояние от точки до отрезка (p1, p2).

        Args:
            point: Точка (x, y).
            p1: Первая точка отрезка (x, y).
            p2: Вторая точка отрезка (x, y).

        Returns:
            Расстояние от точки до отрезка.
        """
        x0, y0 = point
        x1, y1 = p1
        x2, y2 = p2

        dx = x2 - x1
        dy = y2 - y1

        if dx == 0 and dy == 0:
            # Отрезок является точкой
            return np.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)

        t = ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)

        if t < 0:
            # Ближайшая точка - p1
            dx = x0 - x1
            dy = y0 - y1
        elif t > 1:
            # Ближайшая точка - p2
            dx = x0 - x2
            dy = y0 - y2
        else:
            # Ближайшая точка на отрезке
            closest_x = x1 + t * dx
            closest_y = y1 + t * dy
            dx = x0 - closest_x
            dy = y0 - closest_y

        return np.sqrt(dx * dx + dy * dy)

    @staticmethod
    def _distance(point1: tuple, point2: tuple) -> float:
        """
        Вычисляет Евклидово расстояние между двумя точками.
        """
        return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


# Пример использования
if __name__ == "__main__":
    try:
        x_coords, y_coords = VertexGenerator.fromImage("Ball.png")

        # Выводим координаты и визуализируем

        import matplotlib.pyplot as plt

        plt.plot(x_coords, y_coords)
        plt.gca().invert_yaxis()
        plt.show()

    except ValueError as e:
        print(e)
