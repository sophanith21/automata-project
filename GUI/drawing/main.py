from kivy.uix.accordion import ListProperty
from kivy.uix.gesturesurface import Vector
from kivy.uix.accordion import Widget
import os
from kivy.uix.accordion import DictProperty
from kivy.uix.accordion import NumericProperty
import mysql.connector
import subprocess
import json
from kivy.factory import Factory
from kivy.app import App
from kivy.uix.accordion import StringProperty
from kivy.uix.actionbar import Button
from kivy.uix.accordion import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Ellipse, Line
from kivy.metrics import dp

Window.maximize()


class Drawing(Widget):
    diameter = NumericProperty(dp(75))
    radius = NumericProperty(dp(75) / 2)
    gap = NumericProperty(dp(50))
    current_pos = ObjectProperty(Vector(dp(150), dp(400)))
    font_size = NumericProperty(dp(75) / 5)
    width = NumericProperty(dp(1))
    transitions = (
        [
            {
                "id": 7,
                "fa_id": 2,
                "from_state_name": "A",
                "symbol_char": "a",
                "to_state_name": "A",
            },
            {
                "id": 8,
                "fa_id": 2,
                "from_state_name": "A",
                "symbol_char": "ep",
                "to_state_name": "B",
            },
            {
                "id": 9,
                "fa_id": 2,
                "from_state_name": "B",
                "symbol_char": "a",
                "to_state_name": "C",
            },
            {
                "id": 10,
                "fa_id": 2,
                "from_state_name": "B",
                "symbol_char": "b",
                "to_state_name": "C",
            },
            {
                "id": 11,
                "fa_id": 2,
                "from_state_name": "B",
                "symbol_char": "ep",
                "to_state_name": "C",
            },
            {
                "id": 12,
                "fa_id": 2,
                "from_state_name": "C",
                "symbol_char": "a",
                "to_state_name": "C",
            },
        ],
    )
    fa_header = ListProperty(
        [
            {
                "id": 2,
                "name": "NFA_test",
                "type": "NFA",
                "start_state_name": "A",
                "description": "A basic NFA with epsilon transitions.",
            }
        ]
    )

    fa_states = [
        {"id": 4, "fa_id": 2, "name": "A", "is_accepting": 1},
        {"id": 5, "fa_id": 2, "name": "B", "is_accepting": 1},
        {"id": 6, "fa_id": 2, "name": "C", "is_accepting": 1},
    ]
    extrapolated_map = ListProperty([])

    def get_center_x(self):
        return super().get_center_x()

    def get_center_y(self):
        return super().get_center_y()

    def extrapolate(self):
        go_right = True
        height = Window.height
        width = Window.width
        for i in range(len(self.fa_states)):
            temp = {
                "name": self.fa_states[i]["name"],
                "pos": Vector(self.current_pos.x, height - self.current_pos.y),
                "is_accepting": self.fa_states[i]["is_accepting"],
            }
            self.extrapolated_map.append(temp)
            if self.current_pos.x + (self.gap * 2) < Window.width and go_right:
                self.current_pos.x = self.current_pos.x + self.gap * 2
            elif height - self.current_pos.y + self.gap * 2 > 0 and go_right:
                self.current_pos.y = self.current_pos.y + self.gap * 2
                go_right = False
            elif self.current_pos.x - (self.gap * 2) > 0 and not go_right:
                self.current_pos.x = self.current_pos.x - (self.gap * 2)
            elif height - self.current_pos.y + self.gap * 2 > 0 and not go_right:
                self.current_pos.y = self.current_pos.y + self.gap * 2
                go_right = True

        print(json.dumps(self.extrapolated_map, indent=4))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extrapolate()
        with self.canvas:
            for state in self.extrapolated_map:
                Line(
                    circle=(state["pos"].x, state["pos"].y, self.radius),
                    width=self.width,
                )
                my_label = Label()
                my_label.text = state["name"]
                my_label.pos = (
                    state["pos"].x - my_label.width / 2,
                    state["pos"].y - my_label.height / 2,
                )
                my_label.font_size = self.font_size

                self.add_widget(my_label)
                # self.current_pos = Vector(
                #     self.current_pos.x + self.radius, self.current_pos.y
                # )

                # Line(
                #     points=(
                #         self.current_pos.x,
                #         self.current_pos.y,
                #         self.current_pos.x + self.gap,
                #         self.current_pos.y,
                #     )
                # )
                # self.current_pos = Vector(
                #     self.current_pos.x + self.gap, self.current_pos.y
                # )

                # my_label = Label()
                # my_label.text = self.transitions[0][i]["symbol_char"]
                # my_label.pos = (
                #     self.current_pos.x - my_label.width / 2,
                #     self.current_pos.y - my_label.height / 4,
                # )
                # my_label.font_size = self.font_size

                # self.add_widget(my_label)

                # Line(
                #     points=(
                #         self.current_pos.x,
                #         self.current_pos.y,
                #         self.current_pos.x + self.gap,
                #         self.current_pos.y,
                #     )
                # )
                # self.current_pos = Vector(
                #     self.current_pos.x + self.gap + self.radius, self.current_pos.y
                # )

                # Line(
                #     circle=(self.current_pos.x, self.current_pos.y, self.radius),
                #     width=self.width,
                # )
                # my_label = Label()
                # my_label.text = self.transitions[0][i]["to_state_name"]
                # my_label.pos = (
                #     self.current_pos.x - my_label.width / 2,
                #     self.current_pos.y - my_label.height / 2,
                # )
                # my_label.font_size = self.font_size

                # self.add_widget(my_label)


class drawApp(App):
    pass


if __name__ == "__main__":
    drawApp().run()
