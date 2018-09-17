import datetime
import math
import re
import glob
import os
from . import coordinates_handler as coordinates


# Alf - Прямое восхождение - Right ascension - Ra - HMS
# Del - Склонение - Declination - Dec - DMS
# Az - Азимут - Azimuth
# Alt - Высота - Altitude
# Observer - Latitude and Longitude - широта и долгота


ALF_REGEX = re.compile(r'\d{1,2}:\s?\d{1,2}:\s?\d{1,2}\.\d')
DEL_REGEX = re.compile(r'(\+|-)\s?\d{1,2}:\s?\d{1,2}:\s?\d{1,2}')
MAGNITUDE_REGEX = re.compile(r'\d{1,2}\.\d{1,2}')
CLASSIFICATION_REGEX = re.compile(r'\s([\w.+-:?!]+?.+?)\s')
HD_NUMBER_REGEX = re.compile(r'\s(\d+?)\s')
STAR_RADIUS_MAP = {6: 2.5, 5: 3, 4: 3.5, 3: 4, 2: 4.5, 1: 5, 0: 5.5}


class Star:
    """
    Класс, отвечающий за звезду.
    Для каждой звезды хранятся её прямое восхождение (Alf), склонение (Del),
    высчитанные горизонтальные координаты и некоторая информацию о звезде
    """
    def __init__(self, info, observer):
        self.right_ascension = None
        self.declination = None
        self.altitude = None
        self.azimuth = None
        self.basic_vector = None
        self.projected_coordinates = None
        self.rotated_vector = None
        self.apparent_magnitude = None
        self.info = ''
        self.parse(info, observer)

    def parse(self, info, observer):
        """
        Метод предназначен для обработки входных данных и последующего создания объекта Star.
        Выбрасывает исключение ValueError в случае неудачи извлечения важных данных (координаты, звёздная велечина)
        :param info: Строка, описывающая звезду
        :param observer: Наблюдатель - экземпляр класса coordinates_handler.Observer
        """
        right_ascension = ALF_REGEX.search(info)
        declination = DEL_REGEX.search(info)
        apparent_magnitude = MAGNITUDE_REGEX.search(info[40:])
        stellar_class = CLASSIFICATION_REGEX.search(info[46:])
        hd_number = HD_NUMBER_REGEX.search(info[90:])

        if right_ascension and declination and apparent_magnitude:
            right_ascension = right_ascension.group(0)
            declination = declination.group(0)

            self.apparent_magnitude = float(apparent_magnitude.group(0))

            self.right_ascension = coordinates.AngleMeasuresHMS()
            self.right_ascension.parse_coordinates(right_ascension, decimal=False)

            self.declination = coordinates.AngleMeasuresDMS()
            self.declination.parse_coordinates(declination, decimal=False)

            self.ra_dec_to_alt_az(observer)

            if stellar_class:
                stellar_class = stellar_class.group(1)
                self.info += 'Stellar Classification: {}\r\n'.format(stellar_class)

            if hd_number:
                hd_number = hd_number.group(1)
                self.info += 'Henry Draper Catalog number of the star: {}'.format(hd_number)

            self.basic_vector = coordinates.spherical_to_cartesian(self.altitude, self.azimuth, radius=10)
        else:
            raise ValueError

    def ra_dec_to_alt_az(self, observer):
        """
        Переход от экваториальной системы координат к горизонтальной
        :param observer: Наблюдатель - экземпляр класса coordinates_handler.Observer
        """
        local_sidereal_time = observer.local_sidereal_time
        hour_angle = (local_sidereal_time + observer.long.decimal - self.right_ascension.decimal + 360) % 360

        declination = coordinates.degrees_to_radians(self.declination.decimal)
        hour_angle = coordinates.degrees_to_radians(hour_angle)
        latitude = coordinates.degrees_to_radians(observer.lat.decimal)

        cos_alt = (math.sin(latitude) * math.sin(declination) +
                   math.cos(latitude) * math.cos(declination) * math.cos(hour_angle))
        altitude = coordinates.radians_to_degrees(math.asin(cos_alt))
        self.altitude = altitude

        z = math.acos(cos_alt)
        z_s = math.sin(z)

        # избегаем деление на ноль
        if math.fabs(z_s) < 1e-5:
            if self.declination.decimal > 0:
                self.azimuth = 180
            else:
                self.azimuth = 0
            if (self.declination.decimal > 0 and observer.lat.decimal > 0) \
                    or (self.declination.decimal < 0 and observer.lat.decimal < 0):
                self.altitude = 90
            else:
                self.altitude = -90
            return

        a_s = (math.cos(declination) * math.sin(hour_angle)) / z_s
        a_c = (math.sin(latitude) * math.cos(declination) * math.cos(hour_angle) -
               math.cos(latitude) * math.sin(declination)) / z_s

        if a_s == 0 and a_c == 0:
            if self.declination.decimal > 0:
                self.azimuth = 180
            else:
                self.azimuth = 0
            return
        azimuth = math.atan2(a_s, a_c)

        self.azimuth = (coordinates.radians_to_degrees(azimuth) + 360) % 360

    def get_star_color(self):
        """
        Получение цвета в шестнадцатиричном формате, в зависимости от спектрального класса звезды
        :return: Строка, выражающая цвет в шестнадцатиричном формате
        """
        info = self.info
        if info.startswith('O', 24):
            return '#C2FEFC'
        elif info.startswith('B', 24):
            return '#EAF0F0'
        elif info.startswith('A', 24):
            return '#F9FCC8'
        elif info.startswith('F', 24):
            return '#F4FE50'
        elif info.startswith('G', 24):
            return '#FEDB50'
        elif info.startswith('K', 24):
            return '#FDC289'
        elif info.startswith('M', 24):
            return '#FD9C89'
        else:
            return '#F4FE50'

    def get_star_radius(self):
        """
        Получение радиуса звезды (условного) в зависимости от видимой звездной велечины
        :return: Радиус звезды (в пикселях)
        """
        info = round(self.apparent_magnitude)
        return STAR_RADIUS_MAP[info]


def days_passed_from_date(date1, date2=datetime.datetime(2000, 1, 1, 12, 0, 0, 0)):
    """
    Вычисление количества дней, прошедших с заданной даты,
    по умолчанию - кол-во дней, прошедших с эпохи J2000 (1 января 2000 года 12:00:00)
    :param date1: Первая дата
    :param date2: Вторая дата
    :return: Количество дней между первой и второй датой (может быть отрицательным)
    """
    julian_date1 = get_julian_date(date1)
    julian_date2 = get_julian_date(date2)
    return julian_date1 - julian_date2


def get_julian_date(date):
    """
    Находим юлианскую дату
    Юлианская дата - количество прошедших дней,
    начиная с полудня 1 января 4713 до н. э.
    :param date: Дата, для которой высчитывается соответсвующая юлианская дата
    :return: Юлианская дата
    """
    a = (14 - date.month) // 12
    year = date.year + 4800 - a
    month = date.month + 12*a - 3
    julian_day_num = date.day + (153 * month + 2) // 5 + 365 * year + year // 4 - year // 100 + year // 400 - 32045
    julian_date = julian_day_num + (date.hour - 12) / 24 + date.minute / 1440 + date.second / 86400
    return julian_date


def extract_star_from_file(filename):
    """
    Функция извлекает строки из файла, представляющие описание небесного тела
    :param filename: путь до файла, содержащего звезды (*.txt)
    """
    with open(filename, 'r', encoding='cp1251') as file:
        # required python version 3.3 and newer
        yield from file


def star_generator(path):
    """
    Функция извлекает все текстовые файлы из заданной папки
    :param path: папка, содержащая извлекаемые файлы
    :return:
    """
    for filename in glob.glob(os.path.join(path, '*.txt')):
        yield from extract_star_from_file(filename)


def rotate_vectors(stars, quaternion):
    """
    Поворот списка векторов с помощью заданного кватерниона
    :param stars: Список звезд, его элементы - объекты класса star_handler.Star
    :param quaternion: Кватернион, описывающий вращение - объект класса coordinates_handler.Quaternion
    """
    for star in stars:
        new_vector = quaternion.rotate_vector(star.basic_vector)
        star.projected_coordinates = coordinates.Vector(0, 0, 0)
        star.rotated_vector = coordinates.Vector(0, 0, 0)
        star.rotated_vector.x = new_vector.x
        star.rotated_vector.y = new_vector.y
        star.rotated_vector.z = new_vector.z


def get_screen_points(stars, dist, fov, canvas_params=3):
    """
    Функция, отвечающая за нахождение точек на экране пользователя.
    Она так же отсеивает точки, находящиеся за пределами плоскости, на которую проектируется пространство
    :param stars: Список звёзд
    :param dist: Расстояние до плоскости (константа)
    :param fov: Field of view в процентах
    :param canvas_params: Максимальная ширина и высота проективной плоскости
    :return: Список, содержащий координаты только тех звёзд, которые видны пользователю
    """
    canvas_width = canvas_height = (canvas_params * fov) / 100
    projected = []
    for star in stars:
        new_x = (dist * star.rotated_vector.x) / star.rotated_vector.z
        new_y = (dist * star.rotated_vector.y) / star.rotated_vector.z
        if abs(new_x) > canvas_width / 2 or abs(new_y) > canvas_height / 2:
            continue
        star.projected_coordinates.x = (new_x + canvas_width / 2) / canvas_width
        star.projected_coordinates.y = (new_y + canvas_height / 2) / canvas_height
        star.projected_coordinates.z = 0
        projected.append(star)
    return projected


def get_raster_coordinates(stars, image_width, image_height):
    """
    Получение координат в диапозоне от 0 до 1, начало координат находится в левом верхнем углу,
    ось X направлена вниз, Y - вправо
    :param stars: Список звезд
    :param image_width: Ширина экрана
    :param image_height: Высота экрана
    """
    for i in range(0, len(stars)):
        stars[i].projected_coordinates.x = int(stars[i].projected_coordinates.x * image_width)
        stars[i].projected_coordinates.y = int((1 - stars[i].projected_coordinates.y) * image_height)


def get_projected_stars(stars, observer, dist=5, width=512, height=512, fov=65):
    """
    Функция, предназначенная для нахождения проекций точек на плоскость
    :param stars: Список звёзд
    :param observer: Наблюдатель - объект класса coordinates_handler.Observer
    :param dist: Расстояние до плоскости (константа)
    :param width: Ширина экрана
    :param height: Высота экрана
    :param fov: Field of view в процентах
    :return: Список звезд, содержащий спроектированные координаты в поле класса Star
    """
    if not isinstance(observer, coordinates.Observer):
        raise TypeError
    view_vector = coordinates.Vector(0, 0, 0)

    # old
    # view_vector = observer.view_vector
    # old

    # new
    obs_view = observer.view_vector
    view_vector.x, view_vector.y, view_vector.z = map(math.cos, [obs_view.x, obs_view.y, obs_view.z])
    # new

    basic_vector = coordinates.Vector(0, 0, 1)
    quaternion = coordinates.Quaternion.get_quaternion(view_vector, basic_vector)
    quaternion.normalize()
    rotate_vectors(stars, quaternion)
    projected = get_screen_points(stars, dist, fov)
    get_raster_coordinates(projected, width, height)
    return projected
