from kivy.uix.scrollview import ScrollView
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
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.graphics import Color, Line, Rectangle
from kivy.metrics import dp
from kivy.uix.textinput import TextInput

Window.maximize()
Window.clearcolor = (1, 1, 1, 1)
EPSILON_SYMBOL = "ep"  # Our chosen multi-character epsilon symbol


# define different screens
class FirstWindow(Screen):
    pass


class SecondWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class FAWidget(BoxLayout):
    fa_id = NumericProperty(0)
    fa_name = StringProperty("")
    fa_type = StringProperty("")
    fa_description = StringProperty("")

    def __init__(self, fa, **kwargs):
        super().__init__(**kwargs)
        self.fa_id = fa["id"]
        self.fa_name = fa["name"]
        self.fa_type = fa["type"]
        self.fa_description = fa["description"]
        print(self.fa_id)


class FAListWidget(BoxLayout):
    def populate(self):
        app = App.get_running_app()
        self.clear_widgets()
        title = Label(
            text="LIST OF FINITE AUTOMATA",
            bold=True,
            color=(0, 0, 0, 1),
            font_size=dp(35),
            size_hint_y=None,
            height=dp(70),
        )
        with title.canvas.before:
            Color(0.65, 0.75, 0.65, 1)
            self.rect_label = Rectangle(size=title.size, pos=title.pos)
        title.bind(size=self._update_label_rect, pos=self._update_label_rect)
        self.add_widget(title)
        if app.fa_headers:
            another = BoxLayout()
            another.orientation = "horizontal"
            another.size_hint_y = None
            another.height = dp(75)
            label1 = Label(
                text="Name",
                color=(0, 0, 0, 1),
            )
            label2 = Label(
                text="Type",
                color=(0, 0, 0, 1),
            )
            label3 = Label(
                text="Description",
                color=(0, 0, 0, 1),
            )
            label4 = Label(
                text="", color=(0, 0, 0, 1), size_hint=(None, 1), width=dp(100)
            )
            another.add_widget(label1)
            another.add_widget(label2)
            another.add_widget(label3)
            another.add_widget(label4)
            self.add_widget(another)

            scroll_view = ScrollView()

            boxlayout = BoxLayout()
            boxlayout.size_hint_y = None
            boxlayout.bind(minimum_height=boxlayout.setter("height"))

            boxlayout.orientation = "vertical"

            for fa in app.fa_headers:
                FA = FAWidget(fa)
                boxlayout.add_widget(FA)
            scroll_view.add_widget(boxlayout)
            self.add_widget(scroll_view)
        layout = BoxLayout()
        layout.orientation = "horizontal"
        layout.spacing = dp(60)

        button_1 = Button()
        button_1.text = "Define a new finite automaton"
        button_1.color = (0, 0, 0, 1)
        button_1.on_release = self.button_1_pressed
        button_1.size_hint = (None, None)
        button_1.width = dp(300)
        button_1.height = dp(70)
        button_1.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        button_1.background_color = (0.65, 0.75, 0.65, 1)
        button_1.background_normal = ""

        button_2 = Button()
        button_2.color = (0, 0, 0, 1)
        button_2.background_normal = ""
        button_2.text = "Refresh"
        button_2.size_hint = (None, None)
        button_2.background_color = (0.65, 0.75, 0.65, 1)
        button_2.width = dp(300)
        button_2.height = dp(70)
        button_2.pos_hint = {"center_x": 1, "center_y": 0.5}
        button_2.on_release = lambda: (app.update_fa_list_widget(),)
        layout.add_widget(Widget())
        layout.add_widget(button_1)
        layout.add_widget(button_2)
        layout.add_widget(Widget())
        self.add_widget(layout)

    def button_1_pressed(self):
        app = App.get_running_app()
        app.root.current = "design_fa"
        app.root.transition.direction = "left"

    def _update_label_rect(self, instance, value):
        self.rect_label.pos = instance.pos
        self.rect_label.size = instance.size


from kivy.uix.relativelayout import RelativeLayout


class Drawing(Widget):
    fa_data_dicts = DictProperty(
        {
            "fa_header": "",
            "fa_symbols": "",
            "fa_states": "",
            "fa_transitions": "",
            "toTestInput": False,
            "toConvertNFA": False,
            "toMinimize": False,
        }
    )
    diameter = NumericProperty(dp(75))
    radius = NumericProperty(dp(75) / 2)
    gap = NumericProperty(dp(100))
    font_size = NumericProperty(dp(75) / 5)
    line_width = NumericProperty(dp(1))
    transitions = ()
    fa_header = ListProperty()
    fa_states = ListProperty()
    extrapolated_map = ListProperty([])

    occupied_coordinate = ListProperty([])

    def extrapolate(self):
        go_right = True
        layout_pos = Vector(dp(150), dp(150))
        max_x = 0
        max_y = 0
        step = self.gap * 2 + self.radius
        layout_width = Window.width

        for state in self.fa_states:
            temp = {
                "name": state["name"],
                "pos": Vector(layout_pos.x, layout_pos.y),
                "is_accepting": state["is_accepting"],
            }
            self.extrapolated_map.append(temp)

            max_x = max(max_x, layout_pos.x)
            max_y = max(max_y, layout_pos.y)

            if go_right:
                if layout_pos.x + step < layout_width:
                    layout_pos.x += step
                else:
                    layout_pos.y += step
                    go_right = False
            else:
                if layout_pos.x - step > 0:
                    layout_pos.x -= step
                else:
                    layout_pos.y += step
                    go_right = True

        padding = dp(150)
        self.width = max_x + self.radius + padding
        self.height = max_y + self.radius + padding

        # Convert positions from top-left origin to Kivy's bottom-left origin for drawing.
        for state in self.extrapolated_map:
            state["pos"].y = self.height - state["pos"].y

        print(json.dumps(self.extrapolated_map, indent=4))

    def is_overlap(self, data, pos):
        for i in data:
            while (i.x <= pos.x + 25 and i.x >= pos.x - 25) and (
                i.y <= pos.y + 25 and i.y >= pos.y - 25
            ):
                pos.x += 10
        return False

    def is_line_drawn(self, from_pos, to_pos):
        for line in self.drawn_lines:
            if (line[0] == from_pos and line[1] == to_pos) or (
                line[0] == to_pos and line[1] == from_pos
            ):
                return True
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
            Color(0, 0, 0, 1)
            if from_state["name"] != to_state["name"]:
                from_pos = from_state["pos"]
                to_pos = to_state["pos"]

                # Adjust start and end points to be on the circle border
                direction = (to_pos - from_pos).normalize()
                from_pos_adj = from_pos + direction * self.radius
                to_pos_adj = to_pos - direction * self.radius

                # Check for intervening states or parallel lines
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

                if self.is_line_drawn(from_pos, to_pos):
                    intervenes = True  # Force a curved line for parallel transitions

                if intervenes:
                    # Draw a curved line (Bezier)
                    mid_point = (from_pos_adj + to_pos_adj) / 2
                    perp_vec = Vector(
                        -(to_pos_adj - from_pos_adj).y, (to_pos_adj - from_pos_adj).x
                    ).normalize()
                    dist_between = from_pos.distance(to_pos)
                    control_offset = dist_between / 4
                    control_point = mid_point + perp_vec * control_offset
                    Color(0, 0, 0, 1)
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
                    Color(0, 0, 0, 1)
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

                self.drawn_lines.append((from_pos, to_pos))

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
                Color(0, 0, 0, 1)
                Line(points=(to_pos_adj.x, to_pos_adj.y, p1.x, p1.y))
                Color(0, 0, 0, 1)
                Line(points=(to_pos_adj.x, to_pos_adj.y, p2.x, p2.y))

                if self.is_overlap(self.occupied_coordinate, symbol_pos):
                    symbol_pos.y -= 25
                # Stored for later use
                self.occupied_coordinate.append(symbol_pos)

                Symbol = Label()
                Symbol.text = symbol
                Symbol.size_hint = (None, None)
                Symbol.font_size = dp(20)
                Symbol.color = (0, 0, 0, 1)
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
                Color(0, 0, 0, 1)
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
                Symbol.color = (0, 0, 0, 1)
                Symbol.pos = Vector(
                    symbol_pos.x - Symbol.width / 2, symbol_pos.y - Symbol.height / 2
                )
                self.add_widget(Symbol)

    def find_state(self, data_list, target_state_name):
        for i in data_list:
            if i["name"] == target_state_name:
                return i
        return None

    def __init__(self, fa, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.drawn_lines = []
        self.fa_data_dicts = fa
        self.fa_header = self.fa_data_dicts["fa_header"]
        self.fa_states = self.fa_data_dicts["fa_states"]
        self.transitions = self.fa_data_dicts["fa_transitions"]
        self.extrapolate()
        self.size = (self.width, self.height)

        with self.canvas:
            Color(0, 0, 0, 1)
            for state in self.extrapolated_map:
                Color(0, 0, 0, 1)
                Line(
                    circle=(state["pos"].x, state["pos"].y, self.radius),
                    width=self.line_width,
                )
                if state["is_accepting"] == 1:
                    Color(0, 0, 0, 1)
                    Line(
                        circle=(state["pos"].x, state["pos"].y, self.radius - 10),
                        width=self.line_width,
                    )
                my_label = Label()
                my_label.text = state["name"]
                my_label.pos = (
                    state["pos"].x - my_label.width / 2,
                    state["pos"].y - my_label.height / 2,
                )
                my_label.font_size = self.font_size
                my_label.color = (0, 0, 0, 1)
                self.add_widget(my_label)

            for transition in self.transitions:
                from_state = self.find_state(
                    self.extrapolated_map, transition["from_state_name"]
                )

                symbol = transition["symbol_char"]

                to_state = self.find_state(
                    self.extrapolated_map, transition["to_state_name"]
                )
                self.draw_connection(from_state, symbol, to_state)

            print("Height drawing: ", self.height)


class FADetailWidget(BoxLayout):
    fa_data_dicts = DictProperty(
        {
            "fa_header": "",
            "fa_symbols": "",
            "fa_states": "",
            "fa_transitions": "",
            "toTestInput": False,
            "toConvertNFA": False,
            "toMinimize": False,
            "Input": "",
        }
    )
    test_output = StringProperty("Result")

    def call_cpp_processor(self, fa_data_dict):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.abspath(os.path.join(script_dir, ".."))
        cpp_executable = os.path.join(repo_root, "src", "cpp", "fa_processor.exe")
        json_input_string = json.dumps(fa_data_dict)

        try:
            result = subprocess.run(
                [cpp_executable],
                input=json_input_string,  # Send JSON via stdin
                capture_output=True,  # Capture stdout and stderr
                text=True,  # Decode output as text (UTF-8 by default)
                check=True,  # Raise CalledProcessError if C++ returns non-zero exit code
            )

            if result.stderr:
                print("\n--- C++ STDERR Output ---")
                print(result.stderr)
                print("-------------------------\n")

            if result.stdout:
                print("--- C++ Output (JSON) ---")
                # print(result.stdout) # Raw output for debugging
                try:
                    # Parse the JSON output from C++
                    parsed_fa_data = json.loads(result.stdout)
                    print("\n--- Parsed FA Data (from C++) in Python ---")
                    print(json.dumps(parsed_fa_data, indent=4))
                    if self.fa_data_dicts["toConvertNFA"] == True:
                        self.fa_data_dicts = parsed_fa_data["converted_dfa"]
                    else:
                        self.fa_data_dicts = parsed_fa_data["minimized_dfa"]

                    self.fa_data_dicts["toTestInput"] = False
                    self.fa_data_dicts["toConvertNFA"] = False
                    self.fa_data_dicts["toMinimize"] = False
                    self.print_data()
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from C++ stdout: {e}")
                    print(f"Raw C++ stdout: {result.stdout}")
                    return None
            else:
                print("C++ program produced no stdout.")
                return None

        except FileNotFoundError:
            print(f"Error: C++ executable '{cpp_executable}' not found.")
            print("Please ensure it's compiled and in the same directory.")
            return None
        except subprocess.CalledProcessError as e:
            print(f"C++ program failed with exit code {e.returncode}")
            print(f"Stdout:\n{e.stdout}")
            print(f"Stderr:\n{e.stderr}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def call_cpp_processor_test_input(self, fa_data_dict):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.abspath(os.path.join(script_dir, ".."))
        cpp_executable = os.path.join(repo_root, "src", "cpp", "fa_processor.exe")
        json_input_string = json.dumps(fa_data_dict)

        try:
            result = subprocess.run(
                [cpp_executable],
                input=json_input_string,  # Send JSON via stdin
                capture_output=True,  # Capture stdout and stderr
                text=True,  # Decode output as text (UTF-8 by default)
                check=True,  # Raise CalledProcessError if C++ returns non-zero exit code
            )

            if result.stderr:
                print("\n--- C++ STDERR Output ---")
                print(result.stderr)
                print("-------------------------\n")

            if result.stdout:
                print("--- C++ Output (JSON) ---")
                # print(result.stdout) # Raw output for debugging
                try:
                    # Parse the JSON output from C++
                    parsed_fa_data = json.loads(result.stdout)
                    print("\n--- Parsed FA Data (from C++) in Python ---")
                    print(json.dumps(parsed_fa_data, indent=4))

                    self.test_output = parsed_fa_data["test_output"]
                    self.popUp.ids.result.text = self.test_output
                    self.print_data()
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from C++ stdout: {e}")
                    print(f"Raw C++ stdout: {result.stdout}")
                    return None
            else:
                print("C++ program produced no stdout.")
                return None

        except FileNotFoundError:
            print(f"Error: C++ executable '{cpp_executable}' not found.")
            print("Please ensure it's compiled and in the same directory.")
            return None
        except subprocess.CalledProcessError as e:
            print(f"C++ program failed with exit code {e.returncode}")
            print(f"Stdout:\n{e.stdout}")
            print(f"Stderr:\n{e.stderr}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def populate(self):
        app = App.get_running_app()
        self.clear_widgets()
        cursor = app.db_cursor
        sql_query_header = """
                SELECT * from fa_headers
                where id = %s
            """
        sql_query_states = """
                SELECT * from fa_states
                where fa_id = %s
            """
        sql_query_symbols = """
                SELECT * from fa_symbols
                where fa_id = %s
            """
        sql_query_transitions = """
                SELECT * from fa_transitions
                where fa_id = %s
            """
        cursor.execute(sql_query_header, (app.selected_fa_id,))
        self.fa_data_dicts["fa_header"] = cursor.fetchall()

        cursor.execute(sql_query_states, (app.selected_fa_id,))
        self.fa_data_dicts["fa_states"] = cursor.fetchall()

        cursor.execute(sql_query_symbols, (app.selected_fa_id,))
        self.fa_data_dicts["fa_symbols"] = cursor.fetchall()

        cursor.execute(sql_query_transitions, (app.selected_fa_id,))
        self.fa_data_dicts["fa_transitions"] = cursor.fetchall()
        self.fa_data_dicts["Input"] = ""
        name = Label()
        name.valign = "center"
        name.text_size = (None, name.height)
        name.bold = True
        name.text = "Finite Automaton: " + "".join(
            [f"[ {s["name"]} ]" for s in self.fa_data_dicts["fa_header"]]
        )
        name.color = (0, 0, 0, 1)
        name.size_hint = (1, None)
        name.font_size = dp(30)
        with name.canvas.before:
            Color(0.65, 0.75, 0.65, 1)
            self.rect_label = Rectangle(size=name.size, pos=name.pos)
        name.bind(size=self._update_label_rect, pos=self._update_label_rect)

        type = Label()
        type.font_size = dp(20)
        type.text = "Type: " + ", ".join(
            [s["type"] for s in self.fa_data_dicts["fa_header"]]
        )
        type.color = (0, 0, 0, 1)
        type.valign = "top"
        type.text_size = (None, type.height)

        symbols = Label()
        symbols.font_size = dp(20)
        symbols.text = "Symbols: " + ", ".join(
            [s["symbol_char"] for s in self.fa_data_dicts["fa_symbols"]]
        )
        symbols.color = (0, 0, 0, 1)
        symbols.valign = "top"
        symbols.text_size = (None, symbols.height)

        start_state = Label()
        start_state.font_size = dp(20)
        start_state.text = "Start State: " + ", ".join(
            [s["start_state_name"] for s in self.fa_data_dicts["fa_header"]]
        )
        start_state.color = (0, 0, 0, 1)
        start_state.valign = "top"
        start_state.text_size = (None, start_state.height)

        states = Label()
        states.font_size = dp(20)
        states.text = "States: " + ", ".join(
            [s["name"] for s in self.fa_data_dicts["fa_states"]]
        )
        states.color = (0, 0, 0, 1)
        states.valign = "top"
        states.text_size = (None, states.height)

        box = BoxLayout(
            orientation="vertical", size_hint_y=None, padding=[dp(100), 0, 0, 0]
        )
        box.bind(minimum_height=box.setter("height"))
        transitions_scroll = ScrollView(bar_width=dp(10))
        for t in self.fa_data_dicts["fa_transitions"]:
            transitions = Label(
                font_size=dp(20),
                text=f"{t['from_state_name']} -- ({t['symbol_char']}) -> {t['to_state_name']}",
                color=(0, 0, 0, 1),
                size_hint_y=None,
                height=dp(30),
                halign="left",
                valign="middle",
            )
            transitions.bind(
                width=lambda instance, value: setattr(
                    instance, "text_size", (value, None)
                )
            )

            box.add_widget(transitions)

        transitions_scroll.add_widget(box)
        self.add_widget(name)
        layout1 = BoxLayout(orientation="horizontal")
        layout1.add_widget(type)
        layout1.add_widget(symbols)
        layout1.add_widget(start_state)
        layout1.add_widget(states)
        transition_container = BoxLayout(orientation="vertical")
        transition_container.add_widget(
            Label(
                text="Transitions (scroll for more)",
                size_hint_y=None,
                height=dp(40),
                color=(0, 0, 0, 1),
            )
        )
        transition_container.add_widget(transitions_scroll)
        layout1.add_widget(transition_container)
        self.add_widget(layout1)
        scroll_drawing = ScrollView(bar_width=dp(10))
        drawing_widget = Drawing(self.fa_data_dicts)
        scroll_drawing.add_widget(drawing_widget)
        self.add_widget(scroll_drawing)

        layout = BoxLayout()
        test_input = Button()
        test_input.font_size = dp(20)
        test_input.size_hint = (1, 0.5)
        test_input.pos_hint = {"center_x": 0, "center_y": 0.5}

        test_input.text = "Test Input"
        test_input.color = (0, 0, 0, 1)
        test_input.background_normal = ""
        test_input.background_color = (0.65, 0.75, 0.65, 1)

        test_input.on_release = self.test_input_button

        convertNFA = Button()
        convertNFA.font_size = dp(20)
        convertNFA.size_hint = (1, 0.5)
        convertNFA.pos_hint = {"center_x": 0, "center_y": 0.5}
        convertNFA.text = "Convert to DFA"
        convertNFA.color = (0, 0, 0, 1)
        convertNFA.background_normal = ""
        convertNFA.background_color = (0.65, 0.75, 0.65, 1)
        convertNFA.on_release = self.convertNFA_button

        minimization = Button()
        minimization.font_size = dp(20)
        minimization.size_hint = (1, 0.5)
        minimization.pos_hint = {"center_x": 0, "center_y": 0.5}
        minimization.text = "Minimization"
        minimization.color = (0, 0, 0, 1)
        minimization.background_normal = ""
        minimization.background_color = (0.65, 0.75, 0.65, 1)
        minimization.on_release = self.minimization_button

        back = Button()
        back.font_size = dp(20)
        back.size_hint = (1, 0.5)
        back.pos_hint = {"center_x": 0, "center_y": 0.5}
        back.text = "Back"
        back.color = (0, 0, 0, 1)
        back.background_normal = ""
        back.background_color = (0.65, 0.75, 0.65, 1)
        back.on_release = self.back_button

        delete = Button()
        delete.font_size = dp(20)
        delete.size_hint = (1, 0.5)
        delete.pos_hint = {"center_x": 0, "center_y": 0.5}
        delete.text = "Delete"
        delete.color = (0, 0, 0, 1)
        delete.background_normal = ""
        delete.background_color = (0.65, 0.75, 0.65, 1)
        delete.on_release = self.delete_button

        layout.add_widget(test_input)
        layout.add_widget(convertNFA)
        layout.add_widget(minimization)
        layout.add_widget(delete)
        layout.add_widget(back)
        layout.padding = dp(50)
        layout.spacing = dp(20)
        self.add_widget(layout)

    def _update_label_rect(self, instance, value):
        self.rect_label.pos = instance.pos
        self.rect_label.size = instance.size

    def print_data(self):
        print(json.dumps(self.fa_data_dicts, indent=4))

    def test_input_button(self):
        self.fa_data_dicts["toTestInput"] = True
        self.print_data(),
        self.popUpScreenTestInput()

    def convertNFA_button(self):
        if self.fa_data_dicts["fa_header"][0]["type"] == "NFA":
            self.fa_data_dicts["toConvertNFA"] = True
            self.print_data()
            self.call_cpp_processor(self.fa_data_dicts)
            self.update_display()
        else:
            message = Popup()
            message.title = "Important"
            message.size_hint = (0.6, 0.6)
            message.size_hint = (None, None)
            message.size = (dp(400), dp(250))
            message.separator_color = (0.65, 0.75, 0.65, 1)

            text = Label()
            text.text = "This Finite Automaton is already a DFA"
            text.font_size = "20dp"
            message.add_widget(text)
            message.open()

    def minimization_button(self):
        if self.fa_data_dicts["fa_header"][0]["type"] != "NFA":
            self.fa_data_dicts["toMinimize"] = True
            self.call_cpp_processor(self.fa_data_dicts)
            self.print_data()
            self.update_display()
        else:
            message = Popup()
            message.title = "Important"
            message.size_hint = (0.6, 0.6)
            message.size_hint = (None, None)
            message.size = (dp(400), dp(250))
            message.separator_color = (0.65, 0.75, 0.65, 1)

            text = Label()
            text.text = "This Finite Automaton need to be a DFA"
            text.font_size = "20dp"
            message.add_widget(text)
            message.open()

    def back_button(self):
        app = App.get_running_app()
        app.root.current = "first"
        app.root.transition.direction = "right"
        app.update_fa_list_widget()

    def delete_button(self):
        app = App.get_running_app()
        cursor = app.db_cursor

        cursor.execute("Delete from fa_headers WHERE id = %s", (app.selected_fa_id,))
        app.db_connection.commit()
        self.back_button()

    def back_nfa_button(self):
        self.populate()

    def open_the_save_automaton(self, fa_id):
        app = App.get_running_app()
        app.selected_fa_id = fa_id
        self.populate()

    def save_database_button(self):
        self.popUpscreen()

    def popUpscreen(self):
        self.popUp = Factory.popUpScreen()
        self.popUp.main_widget = self
        self.popUp.open()

    def popUpScreenTestInput(self):
        self.popUp = Factory.popUpScreenTestInput()
        self.popUp.main_widget = self
        self.popUp.open()

    def getFaInfoFromPopUp(self):
        if hasattr(self, "popUp"):
            if self.popUp.ids.faNameInput.text:
                self.fa_data_dicts["fa_header"][
                    "name"
                ] = self.popUp.ids.faNameInput.text
            else:
                self.fa_data_dicts["fa_header"]["name"] = "Placeholder"
            if self.popUp.ids.descriptionInput.text:
                self.fa_data_dicts["fa_header"][
                    "description"
                ] = self.popUp.ids.descriptionInput.text
            else:
                self.fa_data_dicts["fa_header"]["description"] = "Placeholder"

    def getInputText(self):
        if hasattr(self, "popUp"):
            self.fa_data_dicts["Input"] = self.popUp.ids.faNameInput.text

    def saveToDatabase(self):
        app = App.get_running_app()
        cursor = app.db_cursor
        try:
            cursor.execute(
                "insert into fa_headers (name,type,start_state_name,description) values (%s,%s,%s,%s)",
                (
                    self.fa_data_dicts["fa_header"]["name"],
                    self.fa_data_dicts["fa_header"]["type"],
                    self.fa_data_dicts["fa_header"]["start_state_name"],
                    "Placeholder",
                ),
            )
            fa_id = cursor.lastrowid
            for state in self.fa_data_dicts["fa_states"]:
                cursor.execute(
                    "Insert into fa_states (fa_id,name,is_accepting) values (%s,%s,%s)",
                    (fa_id, state["name"], state["is_accepting"]),
                )
            for symbol in self.fa_data_dicts["fa_symbols"]:
                cursor.execute(
                    "insert into fa_symbols (fa_id,symbol_char) values (%s,%s)",
                    (fa_id, symbol),
                )

            for transition in self.fa_data_dicts["fa_transitions"]:
                cursor.execute(
                    "insert into fa_transitions (fa_id,from_state_name,symbol_char,to_state_name) values (%s,%s,%s,%s)",
                    (
                        fa_id,
                        transition["from_state_name"],
                        transition["symbol_char"],
                        transition["to_state_name"],
                    ),
                )
            app.db_connection.commit()
            message = Popup()
            message.auto_dismiss = False
            message.title = "Important"
            message.size_hint = (0.6, 0.6)
            text = Label()
            text.text = (
                "Successfully saved the automaton to the database. \nNavigate to:"
            )
            text.font_size = "33dp"
            button1 = Button()
            button1.text = "FA List"
            button1.on_release = lambda: (self.back_button(), message.dismiss())
            button2 = Button()
            button2.text = "The saved automaton"
            button2.on_release = lambda: (
                self.open_the_save_automaton(fa_id),
                message.dismiss(),
            )

            layout = BoxLayout()
            layout.orientation = "vertical"
            layout.add_widget(text)
            layout.add_widget(button1)
            layout.add_widget(button2)

            message.add_widget(layout)
            message.open()

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            message = Popup()
            message.title = "Error"
            message.size_hint = (0.6, 0.6)
            text = Label()
            text.text = "The FA name has already been used.\nPlease make sure your FA name is unique"
            text.font_size = "33dp"

            message.add_widget(text)
            message.open()

    def update_display(self):
        self.clear_widgets()
        fa_header_data = self.fa_data_dicts["fa_header"]
        if isinstance(fa_header_data, list):
            if not fa_header_data:
                return
            fa_header_data = fa_header_data[0]
        fa_symbols_data = self.fa_data_dicts["fa_symbols"]
        if fa_symbols_data and isinstance(fa_symbols_data[0], dict):
            symbols_list = [s["symbol_char"] for s in fa_symbols_data]
        else:
            symbols_list = fa_symbols_data
        name = Label()
        name.text = "Name: " + fa_header_data["name"]
        name.color = (0, 0, 0, 1)
        type = Label()
        type.text = "Type: " + fa_header_data["type"]
        type.color = (0, 0, 0, 1)
        symbols = Label()
        symbols.text = "Symbols: " + ", ".join(symbols_list)
        symbols.color = (0, 0, 0, 1)
        start_state = Label()
        start_state.text = "Start State: " + fa_header_data["start_state_name"]
        start_state.color = (0, 0, 0, 1)
        states = Label()
        states.text = "States: " + ", ".join(
            [s["name"] for s in self.fa_data_dicts["fa_states"]]
        )
        states.color = (0, 0, 0, 1)
        transitions = Label()
        transitions.text = "Transition " + ", ".join(
            [
                f"{t['from_state_name']} -- ({t['symbol_char']}) -> {t['to_state_name']}"
                for t in self.fa_data_dicts["fa_transitions"]
            ]
        )
        transitions.color = (0, 0, 0, 1)
        self.add_widget(name)
        self.add_widget(type)
        self.add_widget(symbols)
        self.add_widget(start_state)
        self.add_widget(states)
        self.add_widget(transitions)
        layout = BoxLayout()
        save_database = Button()
        save_database.text = "Save to Database"
        save_database.color = (0, 0, 0, 1)
        save_database.background_normal = ""
        save_database.background_color = (0.65, 0.75, 0.65, 1)
        save_database.on_release = self.save_database_button
        back_nfa = Button()
        back_nfa.text = "Stop Previewing"
        back_nfa.color = (0, 0, 0, 1)
        back_nfa.background_normal = ""
        back_nfa.background_color = (0.65, 0.75, 0.65, 1)
        back_nfa.on_release = self.back_nfa_button
        layout.add_widget(save_database)
        layout.add_widget(back_nfa)
        layout.padding = dp(30)
        layout.spacing = dp(50)
        self.add_widget(layout)


class DesignFaScreen(Screen):
    def update_transition_table(self):
        self.ids.transition_table_container.clear_widgets()

        try:
            states = self.ids.states.text.split()
            if not states:
                raise ValueError("Please enter at least one state")

            symbols = self.ids.symbols.text.split()
            if not symbols:
                raise ValueError("Please enter at least one symbol")
            if any(len(symbol) > 1 for symbol in symbols):
                raise ValueError("Symbol must be a single character")

            include_epsilon = self.ids.yesCheckBox.active
            if include_epsilon:
                symbols.append("ep")

            header = Factory.TransitionTableHeader()
            self.ids.transition_table_container.add_widget(header)

            for idx, (state, symbol) in enumerate(
                [(state, symbol) for state in states for symbol in symbols]
            ):
                row = Factory.TransitionTableRow()
                row.ids.stateLabel.text = state
                row.ids.symbolLabel.text = symbol
                row.ids.transitionLabel.hint_text = "e.g. q1 or q1,q2"
                row.index = idx
                self.ids.transition_table_container.add_widget(row)
        except ValueError as e:
            error_label = Label(text=str(e), color=(1, 0, 0, 1))
            self.ids.transition_table_container.add_widget(error_label)

    def get_inputs(self):
        self.states = [s.strip() for s in self.ids.states.text.split() if s.strip()]
        self.symbols = [s.strip() for s in self.ids.symbols.text.split() if s.strip()]
        self.acceptingStates = [
            s.strip() for s in self.ids.acceptingStates.text.split() if s.strip()
        ]
        self.statesWithStar = [
            state + "*" if state in self.acceptingStates else state
            for state in self.states
        ]
        hasEpsilon = self.ids.yesCheckBox.active

        transitions = {}
        for row in reversed(self.ids.transition_table_container.children[:-1]):
            state = row.ids.stateLabel.text.strip()
            symbol = row.ids.symbolLabel.text.strip()
            nextState = row.ids.transitionLabel.text.strip()
            if not nextState:
                nextState = "-"
            if state not in transitions:
                transitions[state] = {}

            transitions[state][symbol] = [s.strip() for s in nextState.split(",")]

        print("Number of State is: ", len(self.states))
        print("Number of symbols is: ", len(self.symbols))
        print("The symbols are: ", self.symbols)
        epsilon_display = "yes" if hasEpsilon else "no"
        print(f"Has Epsilon: {epsilon_display}")
        print("The accepting state: ", self.acceptingStates)
        print("The transistion are: ", transitions)

        self.input_data = {
            "states": self.states,
            "numOfState": len(self.states),
            "symbols": self.symbols,
            "numOfSymbol": len(self.symbols),
            "hasEpsilon": hasEpsilon,
            "transitions": transitions,
        }

    def run_designfa_function(self):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            repo_root = os.path.abspath(os.path.join(script_dir, ".."))
            cpp_executable = os.path.join(repo_root, "src", "cpp", "check_fa_type.exe")
            checkFaType = subprocess.run(
                cpp_executable,
                input=json.dumps(self.input_data).encode("utf-8"),
                capture_output=True,
                shell=False,
            )
            result = checkFaType.stdout.decode("utf-8")
            print("Output from designfaFunction:", result)

            self.input_data["fatype"] = result.strip()
            print(
                "Updated input_data with faType:", json.dumps(self.input_data, indent=4)
            )
        except Exception as e:
            print(f"Error running designfa Function: {e}")

    def on_submit(self):
        self.get_inputs()
        self.run_designfa_function()

        self.ids.jsonDataDisplaying.clear_widgets()
        lines = []
        lines.append(f"states: {', '.join(self.input_data['states'])}")
        lines.append(f"numOfState: {self.input_data['numOfState']}")
        lines.append(f"symbols: {', '.join(self.input_data['symbols'])}")
        lines.append(f"numOfSymbol: {self.input_data['numOfSymbol']}")
        lines.append(f"hasEpsilon: {'yes' if self.input_data['hasEpsilon'] else 'no'}")
        lines.append("transitions:")
        for state, transitions in self.input_data["transitions"].items():
            for symbol, nextStates in transitions.items():
                lines.append(f"  S({state} , {symbol}) = {', '.join(nextStates)}")
        # self.ids.jsonDataDisplaying.text = "\n".join(lines)
        lines.append(f"faType: {self.input_data['fatype']}")
        for line in lines:
            label = Label(
                text=line, size_hint_y=None, height=40, color=(0, 0, 0, 1)
            )  # Black text
            self.ids.jsonDataDisplaying.add_widget(label)

    def popUpscreen(self):
        self.popUp = Factory.popUpScreen()
        self.popUp.main_widget = self
        self.popUp.open()

    def getFaInfoFromPopUp(self):
        if hasattr(self, "popUp"):
            self.faName = self.popUp.ids.faNameInput.text
            self.faDescription = self.popUp.ids.descriptionInput.text
            if not self.faName:
                raise ValueError("Please enter a name for the FA")

    def saveToDatabase(self):
        try:
            app = App.get_running_app()
            mycursor = app.db_cursor

            startState = self.states[0]

            faName = self.faName
            faDescription = self.faDescription
            if not faName:
                raise ValueError("Please enter a name for the FA")
            mycursor.execute(
                "INSERT INTO fa_headers (name, type, start_state_name, description) VALUES (%s, %s, %s, %s)",
                (faName, self.input_data["fatype"], startState, faDescription),
            )
            faId = mycursor.lastrowid
            for state in self.states:
                is_accepting = True if state in self.acceptingStates else False
                mycursor.execute(
                    "INSERT INTO fa_states (fa_id, name, is_accepting) VALUES (%s, %s, %s)",
                    (faId, state, is_accepting),
                )
            for symbol in self.symbols:
                mycursor.execute(
                    "INSERT INTO fa_symbols (fa_id, symbol_char) VALUES (%s, %s)",
                    (faId, symbol),
                )
            for state, transitions in self.input_data["transitions"].items():
                for symbol, nextStates in transitions.items():
                    for nextState in nextStates:
                        if nextState != "-":
                            mycursor.execute(
                                "INSERT INTO fa_transitions (fa_id, from_state_name, symbol_char, to_state_name) VALUES (%s, %s, %s, %s)",
                                (faId, state, symbol, nextState),
                            )
            app.db_connection.commit()
            print(f"{mycursor.rowcount} record inserted.")

        except mysql.connector.Error as err:
            print(f"Error: {err}")


class AutomataApp(App):
    fa_headers = ObjectProperty(None)
    db_connection = None
    db_cursor = None
    selected_fa_id = NumericProperty(0)

    def build(self):
        self.connect_db()

    def connect_db(self):
        try:
            self.db_connection = mysql.connector.connect(
                host="localhost", password="root", user="root", database="automatadb"
            )
            self.db_cursor = self.db_connection.cursor(dictionary=True)
        except mysql.connector.errors as err:
            print(f"Error: {err}")

    def update_fa_list_widget(self):
        self.db_cursor.execute("Select * from fa_headers")
        self.fa_headers = self.db_cursor.fetchall()
        first_window = self.root.get_screen("first")
        fa_list_widget = first_window.ids.get("fa_list_widget_id")
        if fa_list_widget:
            fa_list_widget.populate()

    def update_fa_details_widget(self):
        second_window = self.root.get_screen("second")
        fa_detail_widget = second_window.ids.get("fa_detail_widget_id")
        if fa_detail_widget:
            fa_detail_widget.populate()

        print("I updated")

    def on_stop(self):
        # This method is called when the app is closing
        if self.db_connection and self.db_connection.is_connected():
            self.db_connection.close()
            print("Database connection closed gracefully on app stop.")
        else:
            print("No active database connection to close.")


if __name__ == "__main__":
    AutomataApp().run()
