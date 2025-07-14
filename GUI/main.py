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
from kivy.graphics import Color, Line
from kivy.metrics import dp

Window.maximize()

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
        if app.fa_headers:
            for fa in app.fa_headers:
                self.add_widget(FAWidget(fa))
        layout = BoxLayout()
        layout.orientation = "horizontal"
        button_1 = Button()
        button_1.text = "Define a new finite automaton"
        button_1.on_release = self.button_1_pressed
        button_2 = Button()
        button_2.text = "Refresh"
        button_2.on_release = lambda: (app.update_fa_list_widget(),)
        layout.add_widget(button_1)
        layout.add_widget(button_2)
        self.add_widget(layout)

    def button_1_pressed(self):
        app = App.get_running_app()
        app.root.current = "design_fa"


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
    current_pos = ObjectProperty(Vector(dp(150), dp(400)))
    font_size = NumericProperty(dp(75) / 5)
    width = NumericProperty(dp(1))
    transitions = ()
    fa_header = ListProperty()
    fa_states = ListProperty()
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

    def __init__(self, fa, **kwargs):
        super().__init__(**kwargs)
        self.current_pos = Vector(dp(150), dp(400))
        self.fa_data_dicts = fa
        self.fa_header = self.fa_data_dicts["fa_header"]
        self.fa_states = self.fa_data_dicts["fa_states"]
        self.transitions = self.fa_data_dicts["fa_transitions"]
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

            for transition in self.transitions:
                from_state = self.find_state(
                    self.extrapolated_map, transition["from_state_name"]
                )

                symbol = transition["symbol_char"]

                to_state = self.find_state(
                    self.extrapolated_map, transition["to_state_name"]
                )
                self.draw_connection(from_state, symbol, to_state)


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
        }
    )

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
                    self.fa_data_dicts = parsed_fa_data["converted_dfa"]
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
        name = Label()
        name.text = "Name: " + ", ".join(
            [s["name"] for s in self.fa_data_dicts["fa_header"]]
        )
        type = Label()
        type.text = "Type: " + ", ".join(
            [s["type"] for s in self.fa_data_dicts["fa_header"]]
        )
        symbols = Label()
        symbols.text = "Symbols: " + ", ".join(
            [s["symbol_char"] for s in self.fa_data_dicts["fa_symbols"]]
        )
        start_state = Label()
        start_state.text = "Start State(s): " + ", ".join(
            [s["start_state_name"] for s in self.fa_data_dicts["fa_header"]]
        )
        states = Label()
        states.text = "States: " + ", ".join(
            [s["name"] for s in self.fa_data_dicts["fa_states"]]
        )
        transitions = Label()
        transitions.text = "Transition: " + ", ".join(
            [
                f"{t['from_state_name']} - {t['symbol_char']} > {t['to_state_name']}"
                for t in self.fa_data_dicts["fa_transitions"]
            ]
        )
        self.add_widget(name)
        self.add_widget(type)
        self.add_widget(symbols)
        self.add_widget(start_state)
        self.add_widget(states)
        self.add_widget(transitions)
        self.add_widget(Drawing(self.fa_data_dicts))
        layout = BoxLayout()
        test_input = Button()
        test_input.text = "Test Input"

        test_input.on_release = self.test_input_button

        convertNFA = Button()
        convertNFA.text = "Convert to DFA"

        convertNFA.on_release = self.convertNFA_button

        minimization = Button()
        minimization.text = "Minimization"

        minimization.on_release = self.minimization_button

        back = Button()
        back.text = "Back"

        back.on_release = self.back_button

        delete = Button()
        delete.text = "Delete"
        delete.on_release = self.delete_button

        layout.add_widget(test_input)
        layout.add_widget(convertNFA)
        layout.add_widget(minimization)
        layout.add_widget(delete)
        layout.add_widget(back)
        self.add_widget(layout)

    def print_data(self):
        print(json.dumps(self.fa_data_dicts, indent=4))

    def test_input_button(self):
        self.fa_data_dicts["toTestinput"] = (True,)
        self.print_data(),
        self.call_cpp_processor(self.fa_data_dicts)

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
            text = Label()
            text.text = "This Finite Automaton is already a DFA"
            text.font_size = "46dp"
            message.add_widget(text)
            message.open()

    def minimization_button(self):
        self.fa_data_dicts["toMinimize"] = True
        self.print_data()

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
        app = App.get_running_app()
        cursor = app.db_cursor
        cursor.execute(
            "insert into fa_headers (name,type,start_state_name,description) values (%s,%s,%s,%s)",
            (
                self.fa_data_dicts["fa_header"]["name"],
                self.fa_data_dicts["fa_header"]["type"],
                self.fa_data_dicts["fa_header"]["start_state_name"],
                "A converted DFA converted from an NFA",
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
        text.text = "Successfully saved the automaton to the database. \nNavigate to:"
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

    def update_display(self):
        self.clear_widgets()
        name = Label()
        name.text = (
            "Name: " + self.fa_data_dicts["fa_header"]["name"]
        )  # cpp send fa_header in dict not array
        type = Label()
        type.text = "Type: " + self.fa_data_dicts["fa_header"]["type"]
        symbols = Label()
        symbols.text = "Symbols: " + ", ".join(
            [s for s in self.fa_data_dicts["fa_symbols"]]
        )
        start_state = Label()
        start_state.text = (
            "Start State: " + self.fa_data_dicts["fa_header"]["start_state_name"]
        )
        states = Label()
        states.text = "States: " + ", ".join(
            [s["name"] for s in self.fa_data_dicts["fa_states"]]
        )
        transitions = Label()
        transitions.text = "Transition: " + ", ".join(
            [
                f"{t['from_state_name']} - {t['symbol_char']} > {t['to_state_name']}"
                for t in self.fa_data_dicts["fa_transitions"]
            ]
        )
        self.add_widget(name)
        self.add_widget(type)
        self.add_widget(symbols)
        self.add_widget(start_state)
        self.add_widget(states)
        self.add_widget(transitions)
        layout = BoxLayout()
        save_database = Button()
        save_database.text = "Save to Database"

        save_database.on_release = self.save_database_button

        back_nfa = Button()
        back_nfa.text = "Back to NFA"

        back_nfa.on_release = self.back_nfa_button

        layout.add_widget(save_database)
        layout.add_widget(back_nfa)
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
                row.ids.transitionLabel.hint_text = f"{state} , {symbol} = ?"
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

            transitions[state][symbol] = [nextState]

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
            checkFaType = subprocess.run(
                ["./designFaFunction"],
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

        # with open("inputData.json", "w") as f:
        #     json.dump(self.input_data, f, indent=4)

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
                        if "," in nextState:
                            splitStates = nextState.split(",")
                            for splitState in splitStates:
                                mycursor.execute(
                                    "INSERT INTO fa_transitions (fa_id, from_state_name, symbol_char, to_state_name) VALUES (%s, %s, %s, %s)",
                                    (faId, state, symbol, splitState.strip()),
                                )
                        else:
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
