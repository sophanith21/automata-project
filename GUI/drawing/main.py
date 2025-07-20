from kivy.uix.accordion import ListProperty
from kivy.uix.gesturesurface import Vector
from kivy.uix.accordion import Widget
import math
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
    gap = NumericProperty(dp(100))
    current_pos = ObjectProperty(Vector(dp(150), dp(400)))
    font_size = NumericProperty(dp(75) / 5)
    width = NumericProperty(dp(1))
    transitions = (
        # [
        #     {
        #         "id": 7,
        #         "fa_id": 2,
        #         "from_state_name": "A",
        #         "symbol_char": "a",
        #         "to_state_name": "A",
        #     },
        #     {
        #         "id": 8,
        #         "fa_id": 2,
        #         "from_state_name": "A",
        #         "symbol_char": "ep",
        #         "to_state_name": "B",
        #     },
        #     {
        #         "id": 9,
        #         "fa_id": 2,
        #         "from_state_name": "B",
        #         "symbol_char": "a",
        #         "to_state_name": "C",
        #     },
        #     {
        #         "id": 10,
        #         "fa_id": 2,
        #         "from_state_name": "B",
        #         "symbol_char": "b",
        #         "to_state_name": "C",
        #     },
        #     {
        #         "id": 11,
        #         "fa_id": 2,
        #         "from_state_name": "B",
        #         "symbol_char": "ep",
        #         "to_state_name": "C",
        #     },
        #     {
        #         "id": 12,
        #         "fa_id": 2,
        #         "from_state_name": "C",
        #         "symbol_char": "a",
        #         "to_state_name": "C",
        #     },
        # ],
        [
            {
                "id": 1,
                "fa_id": 1,
                "from_state_name": "A",
                "symbol_char": "a",
                "to_state_name": "B",
            },
            {
                "id": 2,
                "fa_id": 1,
                "from_state_name": "A",
                "symbol_char": "b",
                "to_state_name": "C",
            },
            {
                "id": 3,
                "fa_id": 1,
                "from_state_name": "B",
                "symbol_char": "a",
                "to_state_name": "A",
            },
            {
                "id": 4,
                "fa_id": 1,
                "from_state_name": "B",
                "symbol_char": "b",
                "to_state_name": "B",
            },
            {
                "id": 5,
                "fa_id": 1,
                "from_state_name": "C",
                "symbol_char": "a",
                "to_state_name": "C",
            },
            {
                "id": 6,
                "fa_id": 1,
                "from_state_name": "C",
                "symbol_char": "b",
                "to_state_name": "A",
            },
        ],
    )
    fa_header = ListProperty(
        # [
        #     {
        #         "id": 2,
        #         "name": "NFA_test",
        #         "type": "NFA",
        #         "start_state_name": "A",
        #         "description": "A basic NFA with epsilon transitions.",
        #     }
        # ]
        [
            {
                "id": 1,
                "name": "test2",
                "type": "DFA",
                "start_state_name": "A",
                "description": "A simple DFA.",
            }
        ]
    )

    fa_states = ListProperty(
        # [
        #     {"id": 4, "fa_id": 2, "name": "A", "is_accepting": 1},
        #     {"id": 5, "fa_id": 2, "name": "B", "is_accepting": 1},
        #     {"id": 6, "fa_id": 2, "name": "C", "is_accepting": 1},
        # ]
        [
            {"id": 1, "fa_id": 1, "name": "A", "is_accepting": 1},
            {"id": 2, "fa_id": 1, "name": "B", "is_accepting": 0},
            {"id": 3, "fa_id": 1, "name": "C", "is_accepting": 1},
        ]
    )
    extrapolated_map = ListProperty([])

    occupied_coordinate = ListProperty([])

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
            if (
                self.current_pos.x + (self.gap * 2) + self.radius < Window.width
                and go_right
            ):
                self.current_pos.x = self.current_pos.x + self.gap * 2 + self.radius
            elif (
                height - self.current_pos.y + self.gap * 2 + self.radius > 0
                and go_right
            ):
                self.current_pos.y = self.current_pos.y + self.gap * 2 + self.radius
                go_right = False
            elif self.current_pos.x - (self.gap * 2) + self.radius > 0 and not go_right:
                self.current_pos.x = self.current_pos.x - (self.gap * 2) - self.radius
            elif (
                height - self.current_pos.y + self.gap * 2 + self.radius > 0
                and not go_right
            ):
                self.current_pos.y = self.current_pos.y + self.gap * 2 + self.radius
                go_right = True

        print(json.dumps(self.extrapolated_map, indent=4))

    def is_overlap(self, data, pos):
        for i in data:
            while (i.x <= pos.x + 10 and i.x >= pos.x - 10) and (
                i.y <= pos.y + 10 and i.y >= pos.y - 10
            ):
                pos.y -= 10
        return False

    def _distance_point_to_segment(self, p, a, b):
        if a.distance2(b) == 0:
            return p.distance(a)

        ab = b - a
        ap = p - a

        t = ap.dot(ab) / ab.length2()

        if t < 0.0:
            return p.distance(a)
        elif t > 1.0:
            return p.distance(b)

        projection = a + t * ab
        return p.distance(projection)

    def draw_connection(self, from_state, symbol, to_state):
        with self.canvas:
            if from_state["name"] != to_state["name"]:
                from_pos = from_state["pos"]
                to_pos = to_state["pos"]

                # Check for intervening states
                intervenes = False
                for state in self.extrapolated_map:
                    if (
                        state["name"] != from_state["name"]
                        and state["name"] != to_state["name"]
                    ):
                        state_pos = state["pos"]
                        if (
                            self._distance_point_to_segment(state_pos, from_pos, to_pos)
                            < self.radius
                        ):
                            intervenes = True
                            break

                # Adjust start and end points to be on the circle border
                direction = (to_pos - from_pos).normalize()
                from_pos_adj = from_pos + direction * self.radius
                to_pos_adj = to_pos - direction * self.radius

                if intervenes:
                    # Draw a curved line (Bezier)
                    mid_point = (from_pos_adj + to_pos_adj) / 2
                    perp_vec = Vector(
                        -(to_pos_adj - from_pos_adj).y, (to_pos_adj - from_pos_adj).x
                    ).normalize()
                    dist_between = from_pos.distance(to_pos)
                    control_offset = dist_between / 4
                    control_point = mid_point + perp_vec * control_offset

                    Line(
                        bezier=(
                            from_pos_adj.x,
                            from_pos_adj.y,
                            control_point.x,
                            control_point.y,
                            to_pos_adj.x,
                            to_pos_adj.y,
                        )
                    )
                    arrow_direction = (to_pos_adj - control_point).normalize()
                    symbol_pos = (
                        0.25 * from_pos_adj + 0.5 * control_point + 0.25 * to_pos_adj
                    )
                else:
                    # Draw a straight line
                    Line(
                        points=(
                            from_pos_adj.x,
                            from_pos_adj.y,
                            to_pos_adj.x,
                            to_pos_adj.y,
                        )
                    )
                    arrow_direction = (to_pos_adj - from_pos_adj).normalize()
                    symbol_pos = (from_pos + to_pos) / 2

                # Draw arrowhead
                arrow_len = self.gap / 10
                angle = math.radians(30)
                rev_direction = -arrow_direction

                p1_x = rev_direction.x * math.cos(angle) - rev_direction.y * math.sin(
                    angle
                )
                p1_y = rev_direction.x * math.sin(angle) + rev_direction.y * math.cos(
                    angle
                )
                p1 = Vector(p1_x, p1_y).normalize() * arrow_len + to_pos_adj

                p2_x = rev_direction.x * math.cos(-angle) - rev_direction.y * math.sin(
                    -angle
                )
                p2_y = rev_direction.x * math.sin(-angle) + rev_direction.y * math.cos(
                    -angle
                )
                p2 = Vector(p2_x, p2_y).normalize() * arrow_len + to_pos_adj

                Line(points=(to_pos_adj.x, to_pos_adj.y, p1.x, p1.y))
                Line(points=(to_pos_adj.x, to_pos_adj.y, p2.x, p2.y))

                if self.is_overlap(self.occupied_coordinate, symbol_pos):
                    symbol_pos.y -= 25
                # Stored for later use
                self.occupied_coordinate.append(symbol_pos)

                Symbol = Label()
                Symbol.text = symbol
                Symbol.size_hint = (None, None)
                Symbol.font_size = dp(20)
                Symbol.pos = Vector(
                    symbol_pos.x - Symbol.width / 2, symbol_pos.y - Symbol.height / 2
                )
                self.add_widget(Symbol)
            elif from_state["name"] == to_state["name"]:
                pos = Vector(
                    from_state["pos"].x - self.radius / 1.3,
                    from_state["pos"].y + self.radius / 3,
                )

                ellipse_bbox_x = pos.x
                ellipse_bbox_y = pos.y
                ellipse_width = self.radius + self.gap / 6
                ellipse_height = self.radius + self.gap / 5
                angle_start = 120
                angle_end = -120

                Line(
                    ellipse=(
                        ellipse_bbox_x,
                        ellipse_bbox_y,
                        ellipse_width,
                        ellipse_height,
                        angle_start,
                        angle_end,
                    )
                )

                symbol_pos = Vector(
                    from_state["pos"].x, from_state["pos"].y + self.radius * 2
                )
                if self.is_overlap(self.occupied_coordinate, symbol_pos):
                    symbol_pos.y -= 25

                self.occupied_coordinate.append(symbol_pos)

                Symbol = Label()
                Symbol.text = symbol
                Symbol.size_hint = (None, None)
                Symbol.font_size = dp(20)
                Symbol.pos = Vector(
                    symbol_pos.x - Symbol.width / 2, symbol_pos.y - Symbol.height / 2
                )
                self.add_widget(Symbol)

    def find_state(self, data_list, target_state_name):
        for i in data_list:
            if i["name"] == target_state_name:
                return i
        return None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extrapolate()
        with self.canvas:
            for state in self.extrapolated_map:
                Line(
                    circle=(state["pos"].x, state["pos"].y, self.radius),
                    width=self.width,
                )
                if state["is_accepting"] == 1:
                    Line(
                        circle=(state["pos"].x, state["pos"].y, self.radius - 10),
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

            for transition in self.transitions[0]:
                from_state = self.find_state(
                    self.extrapolated_map, transition["from_state_name"]
                )

                symbol = transition["symbol_char"]

                to_state = self.find_state(
                    self.extrapolated_map, transition["to_state_name"]
                )
                self.draw_connection(from_state, symbol, to_state)


class drawApp(App):
    pass


if __name__ == "__main__":
    drawApp().run()
