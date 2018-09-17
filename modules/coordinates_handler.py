import math
import datetime
from . import star_handler


class Observer:
    """
    Наблюдатель и его координаты
    Дата по умолчанию - текущая дата
    """
    def __init__(self):
        self.lat = None
        self.long = None
        self.date = None
        self.local_sidereal_time = None
        self.view_vector = None

    def __str__(self):
        return 'Longitude: {}, latitude: {}'.format(self.long.decimal,
                                                    self.lat.decimal)

    def calibrate_sidereal_time(self):
        if self.long and self.date:
            self.calc_local_sidereal_time()

    def calc_local_sidereal_time(self):
        """
        Метод вычисляет звёздное время в зависимости от текущей даты и координат наблюдателя
        """
        day_offset = star_handler.days_passed_from_date(self.date)
        long = self.long.decimal
        self.local_sidereal_time = (100.46 + 0.985647 * day_offset + long +
                                    15 * (self.date.hour +
                                          self.date.minute / 60 +
                                          self.date.second / 3600) + 360) % 360

    def set_date(self, date=None):
        """
        Метод устанавливает переданную дату, если дата не была передана - устанавливается текущая дата
        В случае, если дата была передана - она должна быть экземпляром datetime.datetime
        В противном случае возникает исключение TypeError
        :param date: Дата, экземпляр класса datetime.datetime
        """
        if date:
            if not isinstance(date, datetime.datetime):
                raise TypeError('Date must be datetime object')
            self.date = date
            return
        date = datetime.datetime.today()
        self.date = date.utcnow()

    def set_view_vector(self, vector):
        """
        Установка вектора взгляда
        :param vector: Вектор - объект класса Vector
        """
        if isinstance(vector, Vector):
            if vector.x == vector.y == vector.z == 0:
                raise ValueError('Select correct view vector')
            self.view_vector = vector
        elif isinstance(vector, str):
            spl = vector.split(',')
            if len(spl) == 3:
                try:
                    x = float(spl[0])
                    y = float(spl[1])
                    z = float(spl[2])
                    if x == y == z == 0:
                        raise ValueError('Select correct view vector')
                except ValueError:
                    raise
                self.view_vector = Vector(x, y, z)
            else:
                raise ValueError('Select correct view vector')
        else:
            raise TypeError

    def set_decimal_coordinates(self, latitude, longitude):
        """
        Метод заполняет координаты наблюдателя
        :param latitude: Широта в градусах в виде строки (десятичный формат)
        :param longitude: Долгота в градусах в виде строки (десятичный формат)
        """
        self.lat, self.long = AngleMeasuresDMS(), AngleMeasuresDMS()
        self.lat.parse_coordinates(latitude, decimal=True)
        self.long.parse_coordinates(longitude, decimal=True)

    def set_geo_dms_coordinates(self, latitude, longitude):
        """
        Метод заполняет координаты наблюдателя
        :param latitude: Широта в формате "sdd:mm:ss.s" (знак, градусы, минуты, секунды)
        :param longitude: Долгота в формате "sdd:mm:ss.s" (знак, градусы, минуты, секунды)
        """
        self.lat, self.long = AngleMeasuresDMS(), AngleMeasuresDMS()
        self.lat.parse_coordinates(latitude, decimal=False)
        self.long.parse_coordinates(longitude, decimal=False)


class AngleMeasuresDMS:
    """
    Формат измерения угла - градусы, минуты, секунды
    """
    def __init__(self):
        self.sign = None
        self.degrees = None
        self.minutes = None
        self.seconds = None
        self.decimal = None

    def __str__(self):
        return str(self.decimal)

    def parse_coordinates(self, info, decimal=True):
        """
        Метод заполняет поля экземпляра класса
        :param info: Строка координат. Может быть представлена в градусах в десятичном виде
        или в формате "sdd:mm:ss.s" - знак, градусы, минуты, секунды
        :param decimal: Флаг, сообщающий о том, в каком из форматов была передана строка:
        True, если переданы строка, содержащая градусы в десятичном виде
        False, если передана строка в формате "sdd:mm:ss.s"
        """
        if decimal:
            self.decimal = float(info)
            self.fill_dms_with_decimal()
        else:
            if info[0] == '-':
                self.sign = -1
                info = info[1:]
            elif info[0] == '+':
                self.sign = 1
                info = info[1:]
            if self.sign is None:
                self.sign = 1
            info_spl = info.split(':')
            self.degrees = float(info_spl[0].replace(' ', ''))
            self.minutes = float(info_spl[1].replace(' ', ''))
            self.seconds = float(info_spl[2].replace(' ', ''))
            self.fill_decimal_with_dms()

    def fill_dms_with_decimal(self):
        if self.decimal < 0:
            self.sign = -1
        else:
            self.sign = 1
        decimal = abs(self.decimal)
        self.degrees = int(decimal)
        self.minutes = int((decimal - self.degrees) * 60)
        self.seconds = (decimal - self.degrees - self.minutes / 60) * 3600

    def fill_decimal_with_dms(self):
        self.decimal = self.sign * (self.degrees + self.minutes / 60 + self.seconds / 3600)


class AngleMeasuresHMS:
    """
    Формат измерения угла - часы, минуты, секунды
    """
    def __init__(self):
        self.hours = None
        self.minutes = None
        self.seconds = None
        self.decimal = None

    def __str__(self):
        return str(self.decimal)

    def parse_coordinates(self, info, decimal=True):
        """
        Метод заполняет поля экземпляра класса
        :param info: Строка координат. Может быть представлена в градусах в десятичном виде
        или в формате "shh:mm:ss.s" - знак, часы, минуты, секунды
        :param decimal: Флаг, сообщающий о том, в каком из форматов была передана строка:
        True, если переданы строка, содержащая градусы в десятичном виде
        False, если передана строка в формате "shh:mm:ss.s"
        """
        if decimal:
            self.decimal = float(info)
            self.fill_hms_with_decimal()
        else:
            info_spl = info.split(':')
            self.hours = float(info_spl[0].replace(' ', ''))
            self.minutes = float(info_spl[1].replace(' ', ''))
            self.seconds = float(info_spl[2].replace(' ', ''))
            self.fill_decimal_with_hms()

    def fill_hms_with_decimal(self):
        hours_total = self.decimal / 15
        self.hours = int(hours_total)
        self.minutes = int((hours_total - self.hours) * 60)
        self.seconds = (hours_total - self.hours - self.minutes / 60) * 3600

    def fill_decimal_with_hms(self):
        hours = self.hours + self.minutes / 60 + self.seconds / 3600
        self.decimal = hours * 15


class Vector:
    def __init__(self, x, y, z):
        if all(isinstance(i, (int, float)) for i in [x, y, z]):
            self.x = x
            self.y = y
            self.z = z
        else:
            raise ValueError('Coordinates must be int or float')

    def __str__(self):
        return 'X: {}, Y: {}, Z: {}'.format(self.x, self.y, self.z)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector(self.x * other, self.y * other, self.z * other)
        else:
            raise TypeError

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def normalize(self):
        length = self.get_length()
        self.x *= (1 / length)
        self.y *= (1 / length)
        self.z *= (1 / length)

    def get_length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    @staticmethod
    def cross_product(vector1, vector2):
        """
        Векторное произведение vector1 и vector2
        :param vector1: Вектор - объект класса Vector
        :param vector2: Вектор - объект класса Vector
        :return: Вектор - результат векторного произведения
        """
        if not all(isinstance(x, Vector) for x in [vector1, vector2]):
            raise TypeError('Wrong argument types were given')
        new_x = vector1.y * vector2.z - vector1.z * vector2.y
        new_y = vector1.z * vector2.x - vector1.x * vector2.z
        new_z = vector1.x * vector2.y - vector1.y * vector2.x
        return Vector(new_x, new_y, new_z)

    @staticmethod
    def dot_product(vector1, vector2):
        """
        Скалярное произведение vector1 и vector2
        :param vector1: Вектор - объект класса Vector
        :param vector2: Вектор - объект класса Vector
        :return: Результат скалярного произведения
        """
        if not all(isinstance(x, Vector) for x in [vector1, vector2]):
            raise TypeError('Wrong argument type was given')
        return (vector1.x * vector2.x +
                vector1.y * vector2.y +
                vector1.z * vector2.z)


class Quaternion:
    def __init__(self, vector, scalar):
        if isinstance(vector, Vector) and isinstance(scalar, (int, float)):
            self.vector = vector
            self.scalar = scalar
            self.conjunct = None
        else:
            raise TypeError('Wrong argument type was given')

    def __str__(self):
        return 'Vector: {}, Scalar: {}'.format(self.vector, self.scalar)

    def get_length(self):
        return math.sqrt(self.vector.x ** 2 + self.vector.y ** 2 + self.vector.z ** 2 + self.scalar ** 2)

    def get_conjunct(self):
        if self.conjunct:
            return self.conjunct
        self.conjunct = Quaternion(self.vector * (-1), self.scalar)
        return self.conjunct

    def reversed(self):
        return self.get_conjunct() * (1 / self.get_length())

    def normalize(self):
        length = self.get_length()
        self.vector *= (1 / length)
        self.scalar *= (1 / length)

    def rotate_vector(self, vector):
        if isinstance(vector, Vector):
            new_quat = self * Quaternion(vector, 0) * self.reversed()
            return new_quat.vector

    @staticmethod
    def get_quaternion(vector1, vector2):
        """
        Вычисление кватерниона, выражающего поворот от vector1 к vector2
        :param vector1: Вектор
        :param vector2: Вектор
        :return: Кватернион - объект класса Quaternion
        """
        if not all(isinstance(x, Vector) for x in [vector1, vector2]):
            raise TypeError('Wrong argument type was given')
        q_vector = Vector.cross_product(vector1, vector2)
        q_scalar = (math.sqrt((vector1.get_length() ** 2) * (vector2.get_length() ** 2))
                    + Vector.dot_product(vector1, vector2))
        return Quaternion(q_vector, q_scalar)

    def __add__(self, other):
        return Quaternion(self.vector + other.vector, self.scalar + other.scalar)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            self.vector *= other
            self.scalar *= other
            return self
        if isinstance(other, Quaternion):
            new_vector = (Vector.cross_product(self.vector, other.vector) +
                          other.vector * self.scalar +
                          self.vector * other.scalar)
            new_scalar = self.scalar * other.scalar - Vector.dot_product(self.vector, other.vector)
            return Quaternion(new_vector, new_scalar)

    def __eq__(self, other):
        if not isinstance(other, Quaternion):
            return False
        return self.vector == other.vector and self.scalar == other.scalar


def degrees_to_radians(degrees):
    return degrees * (math.pi / 180)


def radians_to_degrees(radians):
    return (180 / math.pi) * radians


def spherical_to_cartesian(elevation, azimuth, radius=1):
    """
    Перевод сферический координат в декартовы
    :param elevation: Сферическая координата (в градусах)
    :param azimuth: Сферическая координата (в градусах)
    :param radius: Константа, не имеющая значения
    :return: Вектор, представленный в декартовых координатах
    """
    elevation = degrees_to_radians(elevation)
    azimuth = degrees_to_radians(azimuth)

    x = radius * math.cos(elevation) * math.cos(azimuth)
    y = radius * math.cos(elevation) * math.sin(azimuth)
    z = radius * math.sin(elevation)
    vector = Vector(x, y, z)
    return vector


def main():
    pass

if __name__ == '__main__':
    main()
