import json
import os
from datetime import datetime, timedelta

from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup


# =========================
# ЦВЕТА
# =========================

BG = (0.055, 0.09, 0.16, 1)
PANEL = (0.075, 0.13, 0.22, 1)
BLUE = (0.05, 0.20, 0.38, 1)
BLUE_DARK = (0.035, 0.14, 0.28, 1)

WHITE = (0.93, 0.96, 1, 1)
MUTED = (0.62, 0.69, 0.78, 1)

GREEN = (0.20, 0.72, 0.45, 1)
RED = (0.90, 0.30, 0.32, 1)


# =========================
# КНОПКА С ЗАКРУГЛЁННЫМИ УГЛАМИ
# =========================

class RoundedButton(Button):

    def __init__(self, bg_color=BLUE, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)

        self._bg = bg_color

        with self.canvas.before:
            Color(*bg_color)

            self.rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )

        self.bind(
            pos=self._update_rect,
            size=self._update_rect
        )

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


# =========================
# ОСНОВНОЕ ПРИЛОЖЕНИЕ
# =========================

class AttendanceApp(App):

    def build(self):

        Window.clearcolor = BG

        # Файл сохранения
        self.data_file = os.path.join(
            self.user_data_dir,
            "attendance.json"
        )

        self.students = []
        self.attendance = {}

        self.current_date = datetime.now().date()

        self.load_data()

        # Главный контейнер
        root = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        # =========================
        # ВЕРХНЯЯ ПАНЕЛЬ С ДАТОЙ
        # =========================

        header = BoxLayout(
            size_hint_y=None,
            height=dp(55),
            spacing=dp(8)
        )

        self.prev_btn = RoundedButton(
            text="<",
            font_size=dp(24),
            size_hint_x=None,
            width=dp(52)
        )

        self.prev_btn.bind(
            on_release=lambda x: self.change_day(-1)
        )

        self.date_label = Label(
            text="",
            color=WHITE,
            font_size=dp(17),
            halign="center",
            valign="middle"
        )

        self.date_label.bind(
            size=self.date_label.setter("text_size")
        )

        self.next_btn = RoundedButton(
            text=">",
            font_size=dp(24),
            size_hint_x=None,
            width=dp(52)
        )

        self.next_btn.bind(
            on_release=lambda x: self.change_day(1)
        )

        header.add_widget(self.prev_btn)
        header.add_widget(self.date_label)
        header.add_widget(self.next_btn)

        root.add_widget(header)

        # =========================
        # СТАТИСТИКА
        # =========================

        self.stats_label = Label(
            text="",
            color=MUTED,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(30)
        )

        root.add_widget(self.stats_label)

        # =========================
        # СПИСОК СТУДЕНТОВ
        # =========================

        self.scroll = ScrollView(
            do_scroll_x=False
        )

        self.list_box = GridLayout(
            cols=1,
            spacing=dp(7),
            size_hint_y=None,
            padding=(0, dp(2))
        )

        self.list_box.bind(
            minimum_height=self.list_box.setter("height")
        )

        self.scroll.add_widget(self.list_box)

        root.add_widget(self.scroll)

        # =========================
        # ДОБАВЛЕНИЕ СТУДЕНТА
        # =========================

        add_box = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            spacing=dp(7)
        )

        self.name_input = TextInput(
            hint_text="Имя студента",
            multiline=False,
            font_size=dp(16),
            foreground_color=WHITE,
            hint_text_color=MUTED,
            background_color=PANEL,
            padding=[dp(12), dp(13)]
        )

        self.name_input.bind(
            on_text_validate=lambda x: self.add_student()
        )

        add_btn = RoundedButton(
            text="+ Добавить",
            font_size=dp(15)
        )

        add_btn.bind(
            on_release=lambda x: self.add_student()
        )

        add_box.add_widget(self.name_input)
        add_box.add_widget(add_btn)

        root.add_widget(add_box)

        # =========================
        # НИЖНИЕ КНОПКИ
        # =========================

        bottom = BoxLayout(
            size_hint_y=None,
            height=dp(45),
            spacing=dp(7)
        )

        today_btn = RoundedButton(
            text="Сегодня",
            font_size=dp(14)
        )

        today_btn.bind(
            on_release=lambda x: self.go_today()
        )

        all_present_btn = RoundedButton(
            text="Все присутствуют",
            font_size=dp(14),
            bg_color=BLUE_DARK
        )

        all_present_btn.bind(
            on_release=lambda x: self.mark_all_present()
        )

        bottom.add_widget(today_btn)
        bottom.add_widget(all_present_btn)

        root.add_widget(bottom)

        self.refresh()

        return root

    # =========================
    # ЗАГРУЗКА ДАННЫХ
    # =========================

    def load_data(self):

        try:

            if os.path.exists(self.data_file):

                with open(
                    self.data_file,
                    "r",
                    encoding="utf-8"
                ) as f:

                    data = json.load(f)

                self.students = data.get(
                    "students",
                    []
                )

                self.attendance = data.get(
                    "attendance",
                    {}
                )

        except Exception:

            self.students = []
            self.attendance = {}

    # =========================
    # СОХРАНЕНИЕ
    # =========================

    def save_data(self):

        try:

            os.makedirs(
                os.path.dirname(self.data_file),
                exist_ok=True
            )

            with open(
                self.data_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    {
                        "students": self.students,
                        "attendance": self.attendance
                    },
                    f,
                    ensure_ascii=False,
                    indent=2
                )

        except Exception:
            pass

    # =========================
    # КЛЮЧ ТЕКУЩЕЙ ДАТЫ
    # =========================

    def date_key(self):

        return self.current_date.isoformat()

    # =========================
    # ПОЛУЧИТЬ ОТСУТСТВУЮЩИХ
    # =========================

    def get_absent(self):

        return set(
            self.attendance.get(
                self.date_key(),
                []
            )
        )

    # =========================
    # СОХРАНИТЬ ОТСУТСТВУЮЩИХ
    # =========================

    def set_absent(self, absent):

        self.attendance[
            self.date_key()
        ] = list(absent)

        self.save_data()

        self.refresh()

    # =========================
    # СМЕНА ДНЯ
    # =========================

    def change_day(self, delta):

        self.current_date += timedelta(
            days=delta
        )

        self.refresh()

    # =========================
    # СЕГОДНЯ
    # =========================

    def go_today(self):

        self.current_date = datetime.now().date()

        self.refresh()

    # =========================
    # ДОБАВИТЬ СТУДЕНТА
    # =========================

    def add_student(self):

        name = self.name_input.text.strip()

        if not name:
            return

        student_id = str(
            int(
                datetime.now().timestamp()
                * 1000000
            )
        )

        self.students.append(
            {
                "id": student_id,
                "name": name
            }
        )

        self.name_input.text = ""

        self.save_data()

        self.refresh()

    # =========================
    # ОТМЕТИТЬ СТУДЕНТА
    # =========================

    def toggle_student(self, student_id):

        absent = self.get_absent()

        if student_id in absent:

            absent.remove(student_id)

        else:

            absent.add(student_id)

        self.set_absent(absent)

    # =========================
    # ВСЕ ПРИСУТСТВУЮТ
    # =========================

    def mark_all_present(self):

        self.attendance[
            self.date_key()
        ] = []

        self.save_data()

        self.refresh()

    # =========================
    # УДАЛЕНИЕ СТУДЕНТА
    # =========================

    def remove_student(self, student_id):

        student = next(
            (
                s for s in self.students
                if s["id"] == student_id
            ),
            None
        )

        if not student:
            return

        box = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(10)
        )

        text = Label(
            text=f'Удалить "{student["name"]}"?',
            color=WHITE,
            font_size=dp(16)
        )

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(45),
            spacing=dp(8)
        )

        yes = RoundedButton(
            text="Удалить",
            bg_color=RED
        )

        no = RoundedButton(
            text="Отмена",
            bg_color=BLUE_DARK
        )

        popup = Popup(
            title="Подтверждение",
            content=box,
            size_hint=(0.86, None),
            height=dp(180),
            background_color=PANEL,
            separator_color=BLUE
        )

        def confirm(*args):

            self.students = [
                s for s in self.students
                if s["id"] != student_id
            ]

            for key in list(
                self.attendance.keys()
            ):

                self.attendance[key] = [
                    sid for sid in self.attendance[key]
                    if sid != student_id
                ]

            self.save_data()

            popup.dismiss()

            self.refresh()

        yes.bind(
            on_release=confirm
        )

        no.bind(
            on_release=lambda x: popup.dismiss()
        )

        buttons.add_widget(no)
        buttons.add_widget(yes)

        box.add_widget(text)
        box.add_widget(buttons)

        popup.open()

    # =========================
    # СОЗДАНИЕ СТРОКИ
    # =========================

    def make_student_row(
        self,
        student,
        number,
        absent
    ):

        row = BoxLayout(
            size_hint_y=None,
            height=dp(56),
            spacing=dp(7)
        )

        if absent:

            bg = (
                0.30,
                0.08,
                0.10,
                1
            )

            status = "✕"
            status_color = RED

        else:

            bg = PANEL

            status = "✓"
            status_color = GREEN

        with row.canvas.before:

            Color(*bg)

            rect = RoundedRectangle(
                pos=row.pos,
                size=row.size,
                radius=[dp(9)]
            )

        row.bind(
            pos=lambda obj, value:
            setattr(rect, "pos", value),

            size=lambda obj, value:
            setattr(rect, "size", value)
        )

        num = Label(
            text=f"{number:02d}",
            color=MUTED,
            font_size=dp(13),
            size_hint_x=None,
            width=dp(38)
        )

        name = Label(
            text=student["name"],
            color=WHITE,
            font_size=dp(16),
            halign="left",
            valign="middle"
        )

        name.bind(
            size=name.setter("text_size")
        )

        status_label = Label(
            text=status,
            color=status_color,
            font_size=dp(22),
            size_hint_x=None,
            width=dp(38)
        )

        remove = RoundedButton(
            text="×",
            font_size=dp(22),
            bg_color=(
                0.12,
                0.17,
                0.25,
                1
            ),
            size_hint_x=None,
            width=dp(42)
        )

        remove.bind(
            on_release=lambda x,
            sid=student["id"]:
            self.remove_student(sid)
        )

        row.add_widget(num)
        row.add_widget(name)
        row.add_widget(status_label)
        row.add_widget(remove)

        row.bind(
            on_touch_up=lambda obj,
            touch,
            sid=student["id"]:
            self.on_row_touch(
                obj,
                touch,
                sid
            )
        )

        return row

    # =========================
    # НАЖАТИЕ НА СТУДЕНТА
    # =========================

    def on_row_touch(
        self,
        row,
        touch,
        student_id
    ):

        if row.collide_point(
            *touch.pos
        ):

            if touch.is_mouse_scrolling:
                return False

            self.toggle_student(
                student_id
            )

            return True

        return False

    # =========================
    # ОБНОВЛЕНИЕ ЭКРАНА
    # =========================

    def refresh(self):

        if not hasattr(
            self,
            "list_box"
        ):
            return

        absent = self.get_absent()

        present_students = [
            s for s in self.students
            if s["id"] not in absent
        ]

        absent_students = [
            s for s in self.students
            if s["id"] in absent
        ]

        self.list_box.clear_widgets()

        self.date_label.text = (
            self.current_date.strftime(
                "%d.%m.%Y"
            )
        )

        present_count = len(
            present_students
        )

        absent_count = len(
            absent_students
        )

        self.stats_label.text = (
            f"✓ Присутствуют: "
            f"{present_count}    "
            f"✕ Отсутствуют: "
            f"{absent_count}    "
            f"Всего: "
            f"{len(self.students)}"
        )

        if not self.students:

            empty = Label(
                text=(
                    "Список пуст.\n"
                    "Добавьте первого "
                    "студента ниже."
                ),
                color=MUTED,
                font_size=dp(15),
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=dp(100)
            )

            empty.bind(
                size=empty.setter(
                    "text_size"
                )
            )

            self.list_box.add_widget(
                empty
            )

            return

        # =========================
        # ПРИСУТСТВУЮЩИЕ
        # =========================

        if present_students:

            title = Label(
                text="ПРИСУТСТВУЮТ",
                color=GREEN,
                font_size=dp(12),
                halign="left",
                size_hint_y=None,
                height=dp(28)
            )

            title.bind(
                size=title.setter(
                    "text_size"
                )
            )

            self.list_box.add_widget(
                title
            )

            for i, student in enumerate(
                present_students,
                1
            ):

                self.list_box.add_widget(
                    self.make_student_row(
                        student,
                        i,
                        False
                    )
                )

        # =========================
        # ОТСУТСТВУЮЩИЕ
        # =========================

        if absent_students:

            title = Label(
                text="ОТСУТСТВУЮТ",
                color=RED,
                font_size=dp(12),
                halign="left",
                size_hint_y=None,
                height=dp(34)
            )

            title.bind(
                size=title.setter(
                    "text_size"
                )
            )

            self.list_box.add_widget(
                title
            )

            start_number = (
                len(present_students) + 1
            )

            for i, student in enumerate(
                absent_students,
                start_number
            ):

                self.list_box.add_widget(
                    self.make_student_row(
                        student,
                        i,
                        True
                    )
                )


# =========================
# ЗАПУСК
# =========================

if __name__ == "__main__":
    AttendanceApp().run()