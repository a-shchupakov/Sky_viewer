import datetime
import math
import tkinter
from tkinter import filedialog, messagebox
from pygame import mixer
from . import star_handler
from . import coordinates_handler


class ConfigurationWindow(tkinter.Tk):
    """
    Форма, отвечающая за окно, в котором пользователь вводит конфигурационные данные, такие как:
    Папка, содержащая информацию о небесной сфере
    Дата наблюдения
    Координаты наблюдателя
    Вектор взгляда наблюдателя
    """
    def __init__(self, canvas_width, canvas_height, fov, bright, music_path):
        super().__init__()
        self.canvas_width, self.canvas_height = canvas_width, canvas_height
        self.canvas_fov = fov
        self.bright = bright
        self.music_path = music_path

        self.geometry('350x428+300+200')
        self.resizable(width=False, height=False)

        self.path_frame = PathFrame(self)
        self.path_frame.pack()

        self.date_frame = DateFrame(self)
        self.date_frame.pack()

        self.position_frame = MainPositionFrame(self)
        self.position_frame.pack()

        self.vector_frame = VectorFrame(self)
        self.vector_frame.pack()

        tkinter.Button(self, text='Initialize', command=self.initialize, font=('Arial', 13)).place(
                                                                                            relx=0.5,
                                                                                            rely=0.935,
                                                                                            anchor=tkinter.CENTER)

    def initialize(self, event=None):
        """
        В этой методе производится извлечение данных, ведённых пользователем и их обработка
        """
        def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
            return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

        stars_path = self.path_frame.path.get()
        if not stars_path:
            messagebox.showwarning('Input error', 'Please select the directory with sky information')
            return

        date_frame = self.date_frame
        year, month, day, hour, minute = (date_frame.year.get(), date_frame.month.get(),
                                          date_frame.day.get(), date_frame.hour.get(),
                                          date_frame.minute.get())

        date = None
        if year and month and day and hour and minute:
            try:
                date = datetime.datetime(int(year), int(month),
                                         int(day), int(hour), int(minute))
            except ValueError:
                messagebox.showwarning('Input error', 'Date input was not in the correct format')
                return
        else:
            messagebox.showwarning('Input error', 'Please select the date of observation')
            return

        latitude = self.position_frame.dec.latitude.get()
        longitude = self.position_frame.dec.longitude.get()
        if latitude and longitude:
            try:
                float(latitude), float(longitude)
            except ValueError:
                messagebox.showwarning('Input error', 'Position input was not in the correct format')
                return
        else:
            messagebox.showwarning('Input error', 'Please select position of the observer')
            return

        vector = None
        x = self.vector_frame.x.get()
        y = self.vector_frame.y.get()
        z = self.vector_frame.z.get()

        if x and y and z:
            try:
                x, y, z = map(float, (x, y, z))

                if all(isclose(i, 0, abs_tol=1e-3) for i in (x, y, z)):
                    messagebox.showerror('Input Error', 'View vector must be non zero')
                    return

            except ValueError:
                messagebox.showwarning('Input error', 'Coordinates input was not in the correct format')
                return
            vector = coordinates_handler.Vector(x, y, z)
            vector.normalize()
            new_x, new_y, new_z = map(math.acos, [vector.x, vector.y, vector.z])
            vector.x, vector.y, vector.z = new_x, new_y, new_z
        else:
            messagebox.showwarning('Input error', 'Please select view vector')
            return

        self.destroy()

        calibrate_observer(date=date, longitude=longitude,
                           latitude=latitude, vector=vector,
                           path=stars_path,
                           canvas_width=self.canvas_width, canvas_height=self.canvas_height,
                           fov=self.canvas_fov, bright=self.bright, music_path=self.music_path)


class PathFrame(tkinter.Frame):
    """
    Фрейм, содержаший кнопку и поле для установления пути к папке
    """
    def __init__(self, master):
        super().__init__(master, width=350, height=90)
        self.path = tkinter.StringVar()
        path_label = tkinter.Label(self, text='Choose directory with stars:', font=('Arial', 11))
        path_label.place(relx=0.5, rely=0.30, anchor=tkinter.CENTER)

        path_text = tkinter.Entry(self, width=31, textvariable=self.path)
        path_text.place(relx=0.35, rely=0.57)

        btn = tkinter.Button(self, text="Choose path", command=self.ask_dir)
        btn.place(relx=0.1, rely=0.53)

    def ask_dir(self, event=None):
        dir_ = filedialog.askdirectory()
        self.path.set(dir_)


class DateFrame(tkinter.Frame):
    """
    Фрейм, содержащий поля для введения даты наблюдения
    """
    def __init__(self, master):
        super().__init__(master, width=350, height=150)
        self.year, self.month, self.day, self.hour, self.minute = (tkinter.StringVar(), tkinter.StringVar(),
                                                                   tkinter.StringVar(), tkinter.StringVar(),
                                                                   tkinter.StringVar())

        tkinter.Label(self, text='Observer configuration:', font=('Arial', 11)).place(relx=0.5, rely=0.1,
                                                                                      anchor=tkinter.CENTER)

        tkinter.Label(self, text='Date of observation').place(relx=0.5, rely=0.27, anchor=tkinter.CENTER)

        tkinter.Button(self, text='Today', command=self.set_date).place(relx=0.75, rely=0.27, anchor=tkinter.W)

        self.date_generate_labels()

        self.date_generate_entries()

    def date_generate_labels(self):
        """
        Создание надписей
        """
        tkinter.Label(self, text='Year').place(relx=0.25, rely=0.38)
        tkinter.Label(self, text='Month').place(relx=0.43, rely=0.38)
        tkinter.Label(self, text='Day').place(relx=0.65, rely=0.38)

        tkinter.Label(self, text='Hour').place(relx=0.36, rely=0.68)
        tkinter.Label(self, text='Minute').place(relx=0.52, rely=0.68)

    def date_generate_entries(self):
        """
        Создание полей для ввода данных
        """
        tkinter.Entry(self, width=5, textvariable=self.year).place(relx=0.2433, rely=0.51)
        tkinter.Entry(self, width=5, textvariable=self.month).place(relx=0.444, rely=0.51)
        tkinter.Entry(self, width=5, textvariable=self.day).place(relx=0.64, rely=0.51)

        tkinter.Entry(self, width=5, textvariable=self.hour).place(relx=0.3585, rely=0.81)
        tkinter.Entry(self, width=5, textvariable=self.minute).place(relx=0.535, rely=0.81)

    def set_date(self):
        """
        Установление текущей даты
        """
        today = datetime.datetime.today()
        self.year.set(today.year)
        self.month.set(today.month)
        self.day.set(today.day)
        self.hour.set(today.hour)
        self.minute.set(today.minute)


class MainPositionFrame(tkinter.Frame):
    """
    Фрейм, содержащий поля для введения координат наблюдателя
    Возможен ввод данных в десятичном и географическом форматах
    """
    def __init__(self, master):
        super().__init__(master, width=350, height=90)
        tkinter.Label(self, text='Position of the observer').place(relx=0.5, rely=0.1, anchor=tkinter.CENTER)

        self.dec = DecimalPositionFrame(self)

        self.dec.place(relx=0.5, rely=0.3333333, anchor=tkinter.N)


class DecimalPositionFrame(tkinter.Frame):
    """
    Фрейм, отвечающий за десятичный ввод данных
    """
    def __init__(self, master):
        super().__init__(master, width=200, height=60)
        self.latitude, self.longitude = tkinter.StringVar(), tkinter.StringVar()

        tkinter.Label(self, text='Latitude').place(relx=0,  rely=0.13)
        tkinter.Entry(self, width=18, textvariable=self.latitude).place(relx=0.35, rely=0.15)

        tkinter.Label(self, text='Longitude').place(relx=0, rely=0.53)
        tkinter.Entry(self, width=18, textvariable=self.longitude).place(relx=0.35, rely=0.55)


class VectorFrame(tkinter.Frame):
    """
    Фрейм, содержащий поля для ввода вектора наблюдения
    """
    def __init__(self, master):
        super().__init__(master, width=350, height=50)
        tkinter.Label(self, text='View vector').pack(side=tkinter.TOP)

        self.x, self.y, self.z = tkinter.StringVar(), tkinter.StringVar(), tkinter.StringVar()

        self.coordinates_frame = tkinter.Frame(self, width=350, height=25)
        self.coordinates_frame.pack(side=tkinter.TOP)
        self.generate_coordinates()

    def generate_coordinates(self):
        tkinter.Label(self.coordinates_frame, text='X:').place(anchor=tkinter.CENTER, relx=0.30, rely=0.5)
        tkinter.Entry(self.coordinates_frame, width=3, textvariable=self.x).place(anchor=tkinter.CENTER,
                                                                                  relx=0.355, rely=0.5)

        tkinter.Label(self.coordinates_frame, text='Y:').place(anchor=tkinter.CENTER, relx=0.46, rely=0.5)
        tkinter.Entry(self.coordinates_frame, width=3, textvariable=self.y).place(anchor=tkinter.CENTER,
                                                                                  relx=0.515, rely=0.5)

        tkinter.Label(self.coordinates_frame, text='Z:').place(anchor=tkinter.CENTER, relx=0.62, rely=0.5)
        tkinter.Entry(self.coordinates_frame, width=3, textvariable=self.z).place(anchor=tkinter.CENTER,
                                                                                  relx=0.675, rely=0.5)


class CanvasFrame(tkinter.Canvas):
    """
    Фрейм, отвечающий за отображение небесных тел
    """
    def __init__(self, master, stars, observer, fov, music_path, **kwargs):
        super().__init__(master, **kwargs)
        self.width, self.height = self.winfo_reqwidth(), self.winfo_reqheight()

        self.fov = fov

        self.stars = stars
        self.displayed = {}
        self.observer = observer
        self.music_paused = False
        mixer.init()
        mixer.music.load(music_path)

        self.text = None
        self.current_x, self.current_y = None, None

        self.bind('<B1-Motion>', self.on_click)
        self.bind('<Configure>', self.on_resize)
        self.bind('<Motion>', self.motion)
        self.bind('<ButtonRelease-3>', self.pause_music)

        projected = star_handler.get_projected_stars(self.stars, self.observer, dist=5,
                                                     width=self.width, height=self.height,
                                                     fov=self.fov)

        self.draw_stars(projected)
        mixer.music.play(-1)

    def pause_music(self, event):
        if self.music_paused:
            mixer.music.unpause()
            self.music_paused = False
        else:
            mixer.music.pause()
            self.music_paused = True

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects
        self.scale(tkinter.ALL, 0, 0, wscale, hscale)

    def on_click(self, event):
        """
        Определяется сдвиг и происходит перерисовка формы
        :param event: Событие
        """
        if self.current_x is None:
            self.current_x = event.x
            self.current_y = event.y
        else:
            delta_x = event.x - self.current_x
            delta_y = event.y - self.current_y
            self.get_projected(delta_x, delta_y)
            self.current_x, self.current_y = None, None

    def motion(self, event):
        position = event.x, event.y
        item = self.find_closest(*position, start='oval')
        try:
            item = item[0]
        except IndexError:
            return
        coords = self.coords(item)
        center = None
        try:
            center = (coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2
        except IndexError:
            return
        if all(abs(x[0] - x[1]) < 3 for x in zip(position, center)):
            if self.text is None:
                place = self.find_place(position)
                if place == 'sw':
                    dx, dy = 10, -10
                elif place == 'nw':
                    dx, dy = 10, 10
                elif place == 'se':
                    dx, dy = -10, -10
                elif place == 'ne':
                    dx, dy = -10, 10
                else:
                    self.text = self.create_text(5, 5, state=tkinter.DISABLED, anchor=tkinter.NW,
                                                 text=self.displayed[item].info, fill='white')
                    return
                self.text = self.create_text(position[0] + dx, position[1] + dy, anchor=place, state=tkinter.DISABLED,
                                             text=self.displayed[item].info, fill='white')
        else:
            self.delete(self.text)
            self.text = None

    def find_place(self, coords, dx=275, dy=75):
        result = ''
        x, y = coords[0], coords[1]
        if 0 < y - dy < self.height:
            result += 's'
        elif 0 < y + dy < self.height:
            result += 'n'
        if 0 < x + dx < self.width:
            result += 'w'
        elif 0 < x - dx < self.width:
            result += 'e'
        if len(result) == 2:
            return result
        return ''

    def get_projected(self, delta_x, delta_y):
        """
        Высчитываются новые координаты с учетом сдвига небесной сферы
        :param delta_x: Сдвиг по оси X
        :param delta_y: Сдвиг по оси Y
        """
        divider_x = abs(10000 * self.observer.view_vector.x) + 1
        divider_y = abs(10000 * self.observer.view_vector.y) + 1
        self.observer.view_vector = self.observer.view_vector + coordinates_handler.Vector(delta_x / divider_x,
                                                                                           -delta_y / divider_y,
                                                                                           0)

        projected = star_handler.get_projected_stars(self.stars, self.observer, dist=5,
                                                     width=self.winfo_reqwidth(),
                                                     height=self.winfo_reqheight(),
                                                     fov=self.fov)
        self.draw_stars(projected)

    def draw_stars(self, projected):
        """
        Отрисовка списка звёзд
        :param projected: Список, содержащий спроецированные координаты звёзд
        """
        self.delete(tkinter.ALL)
        self.displayed.clear()

        for star in projected:
            color = star.get_star_color()
            radius = star.get_star_radius()
            x = star.projected_coordinates.x
            y = star.projected_coordinates.y
            oval = self.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, tag='oval')
            self.update()
            self.displayed[oval] = star


def calibrate_observer(date=None, longitude=None, latitude=None,
                       vector=None, path=None, canvas_width=None,
                       canvas_height=None, fov=None, bright=None,
                       music_path=None):
    """
    Установка параметров наблюдателя
    :param date: Дата наблюдения
    :param longitude: Позиция наблюдения - долгота
    :param latitude: Позиция наблюдения - широта
    :param vector: Вектор взгляда
    :param path: Папка, описывающая небесную сферу
    :param canvas_width: Ширина будущего окна, содержащего звезды
    :param canvas_height: Длина будущего окна, содержащего звезды
    :param fov: Field of view в процентах
    :param bright: Фильтрация яркости
    :param music_path: Путь до проигрываемого файла (музыка)
    """
    observer = coordinates_handler.Observer()
    observer.set_date(date)
    observer.set_decimal_coordinates(longitude, latitude)
    observer.set_view_vector(vector)
    observer.calibrate_sidereal_time()

    initiate_view_form(observer, path, canvas_width, canvas_height, fov, bright, music_path)


def initiate_view_form(observer, path, canvas_width, canvas_height, fov, bright, music_path):
    """
    Создание формы, на которую будут отрисовываться звёзды
    :param observer: Наблюдатель - объект класса coordinates_handler.Observer
    :param path: Папка, описывающая небесную сферу
    :param canvas_width: Ширина будущего окна, содержащего звезды
    :param canvas_height: Длина будущего окна, содержащего звезды
    :param fov: Field of view в процентах
    :param bright: Фильтрация яркости
    :param music_path: Путь до проигрываемого файла (музыка)
    """
    stars_collection = star_handler.star_generator(path)
    stars = []

    bright_operand, bright_value = bright.split()
    bright_value = float(bright_value)

    for star_info in stars_collection:
        try:
            new_star = star_handler.Star(star_info, observer)
        except ValueError:
            continue
        else:
            if bright_operand == 'more':  # The brighter an object appears, the lower its magnitude value
                if new_star.apparent_magnitude >= bright_value:
                    stars.append(new_star)
            else:
                if new_star.apparent_magnitude <= bright_value:
                    stars.append(new_star)
    master = tkinter.Tk()
    canvas = CanvasFrame(master, stars, observer, fov, music_path,
                         width=canvas_width, height=canvas_height,
                         bg='black', highlightthickness=0)
    canvas.pack(fill=tkinter.BOTH, expand=tkinter.YES)

    master.mainloop()
