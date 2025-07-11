import os
from kivy.uix.accordion import DictProperty
from kivy.uix.accordion import NumericProperty
import mysql.connector
import subprocess
import json
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
        button_2 = Button()
        button_2.text = "Refresh"
        button_2.on_release = lambda: (app.update_fa_list_widget(),)
        layout.add_widget(button_1)
        layout.add_widget(button_2)
        self.add_widget(layout)


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

        layout.add_widget(test_input)
        layout.add_widget(convertNFA)
        layout.add_widget(minimization)
        layout.add_widget(back)
        self.add_widget(layout)

    def print_data(self):
        print(json.dumps(self.fa_data_dicts, indent=4))

    def test_input_button(self):
        self.fa_data_dicts["toTestinput"] = (True,)
        self.print_data(),
        self.call_cpp_processor(self.fa_data_dicts)

    def convertNFA_button(self):
        self.fa_data_dicts["toConvertNFA"] = True
        self.print_data()
        self.call_cpp_processor(self.fa_data_dicts)
        self.update_display()

    def minimization_button(self):
        self.fa_data_dicts["toMinimize"] = True
        self.print_data()

    def back_button(self):
        app = App.get_running_app()
        app.root.current = "first"
        app.root.transition.direction = "right"

    def back_nfa_button(self):
        self.populate()

    def save_database_button(self):
        app = App.get_running_app
        cursor = app.db_cursor
        cursor.execute(
            "insert into fa_headers values (%s,%s,%s)",
            (
                self.fa_data_dicts["fa_header"]["name"],
                self.fa_data_dicts["fa_header"]["type"],
                self.fa_data_dicts["fa_header"]["start_state_name"],
            ),
        )
        fa_id = cursor.lastrowid
        for state in self.fa_data_dicts["fa_states"]:
            cursor.execute(
                "Insert into fa_states values (%s,%s,%s)",
                (fa_id, state["name"], state["is_accepting"]),
            )
        for symbol in self.fa_data_dicts["fa_symbols"]:
            cursor.execute("insert into fa_symbols values (%s,%s)", (fa_id, symbol))

        for transition in self.fa_data_dicts["fa_transitions"]:
            cursor.execute(
                "insert into fa_transitions values (%s,%s,%s,%s)",
                (
                    fa_id,
                    transition["from_state_name"],
                    transition["symbol_char"],
                    transition["to_state_name"],
                ),
            )

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

        save_database.on_release = self.test_input_button

        back_nfa = Button()
        back_nfa.text = "Back to NFA"

        back_nfa.on_release = self.back_nfa_button

        layout.add_widget(save_database)
        layout.add_widget(back_nfa)
        self.add_widget(layout)


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
