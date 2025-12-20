from operator import itemgetter


class Composition:
    """Музыкальное произведение"""

    def __init__(self, id, title, duration, orchestra_id):
        self.id = id
        self.title = title
        self.duration = duration
        self.orchestra_id = orchestra_id


class Orchestra:
    """Оркестр"""

    def __init__(self, id, name):
        self.id = id
        self.name = name


class CompositionOrchestra:
    """Связь многие-ко-многим между произведениями и оркестрами"""

    def __init__(self, orchestra_id, composition_id):
        self.orchestra_id = orchestra_id
        self.composition_id = composition_id


# Данные (остаются глобальными для запуска main, но передаются в функции)
orchestras = [
    Orchestra(1, 'Симфонический оркестр'),
    Orchestra(2, 'Камерный оркестр'),
    Orchestra(3, 'Джазовый оркестр'),
    Orchestra(4, 'Народный оркестр'),
]

compositions = [
    Composition(1, 'Симфония №5', 20, 1),
    Composition(2, 'Концерт для скрипки', 15, 2),
    Composition(3, 'Рапсодия в стиле блюз', 10, 3),
    Composition(4, 'Симфония №9', 25, 1),
    Composition(5, 'Увертюра 1812', 15, 1),
    Composition(6, 'Симфониетта', 12, 2),
]

compositions_orchestras = [
    CompositionOrchestra(1, 1),
    CompositionOrchestra(1, 4),
    CompositionOrchestra(1, 5),
    CompositionOrchestra(2, 2),
    CompositionOrchestra(2, 6),
    CompositionOrchestra(3, 3),
    CompositionOrchestra(4, 1),
    CompositionOrchestra(4, 3),
]


def get_one_to_many(orchestras, compositions):
    """Формирует список связей один-ко-многим"""
    return [(c.title, c.duration, o.name)
            for o in orchestras
            for c in compositions
            if c.orchestra_id == o.id]


def get_many_to_many(orchestras, compositions, compositions_orchestras):
    """Формирует список связей многие-ко-многим"""
    many_to_many_temp = [(o.name, co.orchestra_id, co.composition_id)
                         for o in orchestras
                         for co in compositions_orchestras
                         if o.id == co.orchestra_id]

    return [(c.title, c.duration, orchestra_name)
            for orchestra_name, orchestra_id, composition_id in many_to_many_temp
            for c in compositions if c.id == composition_id]


def task_1(one_to_many):
    """
    Задание Б1: Вывести список всех связанных произведений и оркестров,
    отсортированный по названию произведения.
    """
    return sorted(one_to_many, key=itemgetter(0))


def task_2(orchestras, one_to_many):
    """
    Задание Б2: Вывести список оркестров с количеством произведений в каждом,
    отсортированный по количеству произведений.
    """
    res_2_unsorted = []
    for o in orchestras:
        # Фильтруем one_to_many по имени текущего оркестра
        o_compositions = list(filter(lambda i: i[2] == o.name, one_to_many))
        o_compositions_count = len(o_compositions)
        res_2_unsorted.append((o.name, o_compositions_count))

    return sorted(res_2_unsorted, key=itemgetter(1), reverse=True)


def task_3(many_to_many, ending):
    """
    Задание Б3: Вывести список всех оркестров, у которых название произведения
    заканчивается на заданную подстроку (например, 'ов').
    """
    res_3 = []
    for title, duration, orchestra in many_to_many:
        if title.endswith(ending):
            res_3.append((title, orchestra))

    return list(set(res_3))


def main():
    """Основная функция"""
    one_to_many = get_one_to_many(orchestras, compositions)
    many_to_many = get_many_to_many(orchestras, compositions, compositions_orchestras)

    print('Задание Б1')
    res_1 = task_1(one_to_many)
    [print(f"{title} - {orchestra}") for title, duration, orchestra in res_1]

    print('\nЗадание Б2')
    res_2 = task_2(orchestras, one_to_many)
    [print(f"{orchestra}: {count} произведений") for orchestra, count in res_2]

    print('\nЗадание Б3')
    # В оригинальном задании ищется окончание "ов"
    res_3 = task_3(many_to_many, 'ов')
    [print(f"{title} - {orchestra}") for title, orchestra in res_3]


if __name__ == '__main__':
    main()