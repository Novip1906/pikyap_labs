import unittest
from main import (
    Composition, Orchestra, CompositionOrchestra,
    get_one_to_many, get_many_to_many,
    task_1, task_2, task_3
)


class TestRK2(unittest.TestCase):
    def setUp(self):
        """Инициализация тестовых данных перед каждым тестом"""
        self.orchestras = [
            Orchestra(1, 'Оркестр А'),
            Orchestra(2, 'Оркестр Б'),
            Orchestra(3, 'Оркестр В'),
        ]

        self.compositions = [
            Composition(1, 'Альфа', 10, 1),
            Composition(2, 'Бета', 20, 1),
            Composition(3, 'Гамма', 15, 2),
            Composition(4, 'Марш Петров', 5, 3),  # Для теста Б3 (оканчивается на "ов")
        ]

        self.compositions_orchestras = [
            CompositionOrchestra(1, 1),  # Оркестр А - Альфа
            CompositionOrchestra(1, 2),  # Оркестр А - Бета
            CompositionOrchestra(2, 3),  # Оркестр Б - Гамма
            CompositionOrchestra(3, 4),  # Оркестр В - Марш Петров
        ]

        self.one_to_many = get_one_to_many(self.orchestras, self.compositions)
        self.many_to_many = get_many_to_many(self.orchestras, self.compositions, self.compositions_orchestras)

    def test_task_1(self):
        """Тест задания Б1: сортировка по названию"""
        result = task_1(self.one_to_many)

        # Ожидаем сортировку: Альфа, Бета, Гамма, Марш Петров
        expected_titles = ['Альфа', 'Бета', 'Гамма', 'Марш Петров']
        actual_titles = [item[0] for item in result]

        self.assertEqual(actual_titles, expected_titles)

    def test_task_2(self):
        """Тест задания Б2: сортировка по количеству произведений"""
        result = task_2(self.orchestras, self.one_to_many)

        # Оркестр А: 2 произведения
        # Оркестр Б: 1 произведение
        # Оркестр В: 1 произведение

        # Проверяем, что первый элемент имеет наибольшее количество
        self.assertEqual(result[0][0], 'Оркестр А')
        self.assertEqual(result[0][1], 2)

    def test_task_3(self):
        """Тест задания Б3: фильтрация по окончанию"""
        # Ищем произведения, оканчивающиеся на "ов"
        result = task_3(self.many_to_many, 'ов')

        # Должен найтись только "Марш Петров"
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], 'Марш Петров')
        self.assertEqual(result[0][1], 'Оркестр В')


if __name__ == '__main__':
    unittest.main()