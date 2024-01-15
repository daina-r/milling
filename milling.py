class Cavity:
    """
    Общий класс отдельного элемента фрезерования (отверстие, паз, отрез, выборка..)
    """
    all_cavities = []  # Классовый атрибут для хранения всех объектов класса

    def __init__(self, sequence, X, Y, depth):
        self.__sequence = sequence
        self.__X = X
        self.__Y = Y
        self.__depth = depth
        Cavity.all_cavities.append(self) # Добавляем созданный объект в список all_cavities

    @property
    def sequence(self):
        return self.__sequence

    @sequence.setter
    def sequence(self, new_sequence):
        self.__sequence = new_sequence
        self.check_sequences()

    def check_sequences(self):
        for unit in Cavity.all_cavities:
            if unit is not self:
                print(f"{self.sequence} изменил sequence на {self.__sequence}")

    def plunge(self):
        print(f"Привет, меня зовут {self.sequence} и мне {self.__X} лет.")

    @classmethod
    def get_all(cls):
        for unit in cls.all_cavities:
            print(unit.sequence)


class Hole(Cavity):
    """
    Класс отверстий
    """
    def __init__(self, sequence, X, Y, depth, D):
        super().__init__(sequence, X, Y, depth)  # вызываем конструктор родительского класса
        self.D = D

    def plunge(self):
        return "Гав-гав!"


class Line(Cavity):
    """
    Класс прямолинейных отрезов
    """
    def __init__(self, sequence, X, Y, depth, lenght):
        super().__init__(sequence, X, Y, depth)  # вызываем конструктор родительского класса
        self.lenght = lenght

    def plunge(self):
        super().plunge()  # вызываем метод родительского класса
        return "Мяу!"


# Создаем несколько экземпляров класса
hole = Hole("Барон", 3, 2, 4, 6)
line = Line("Мурзик", 2, 4, 6, 2)

# Вызываем метод get_all, чтобы вывести имена всех животных
Cavity.get_all()

# Изменяем sequence одного из животных, что вызывает перепроверку у других животных
line.sequence = "Том"
Cavity.get_all()

# Вызов метода plunge
hole.plunge()
print(f"{hole.sequence}: {hole.plunge()}")
print(f"{line.sequence}: {line.plunge()}")

