from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.app import App  
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.uix.label import Label
import json
import subprocess
import mysql.connector


#Window.size = (1200, 800) # width, height 
Window.maximized = True
Window.clearcolor = (0.298, 0.345, 0.357, 1) 

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

            for idx, (state, symbol) in enumerate([(state, symbol) for state in states for symbol in symbols]):
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
        self.acceptingStates = [s.strip() for s in self.ids.acceptingStates.text.split() if s.strip()]
        self.statesWithStar = [state + '*' if state in self.acceptingStates else state for state in self.states]
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
                input=json.dumps(self.input_data).encode('utf-8'),
                capture_output=True,
                shell=False
                )
            result = checkFaType.stdout.decode('utf-8')
            print("Output from designfaFunction:", result)

            self.input_data["fatype"] = result.strip()
            print("Updated input_data with faType:", json.dumps(self.input_data, indent=4))
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
        for state, transitions in self.input_data['transitions'].items():
            for symbol, nextStates in transitions.items():
                lines.append(f"  S({state} , {symbol}) = {', '.join(nextStates)}")
        # self.ids.jsonDataDisplaying.text = "\n".join(lines)
        lines.append(f"faType: {self.input_data['fatype']}")
        for line in lines:
            label = Label(text=line, 
                        size_hint_y=None, 
                        height=40,
                        color=(0, 0, 0, 1))  # Black text
            self.ids.jsonDataDisplaying.add_widget(label)


    def popUpscreen(self):
        self.popUp = Factory.popUpScreen()
        self.popUp.main_widget = self
        self.popUp.open()

    def getFaInfoFromPopUp(self):
        if hasattr(self, 'popUp'):
            self.faName = self.popUp.ids.faNameInput.text
            self.faDescription = self.popUp.ids.descriptionInput.text
            if not self.faName:
                raise ValueError("Please enter a name for the FA")
    def saveToDatabase(self):
        try:
            mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            database="automata_project",
            password="Gekheang1234"
        )
            if mydb.is_connected():
                print("Connected to the database successfully.")
            
            mycursor = mydb.cursor() 

            startState = self.states[0]

            faName = self.faName
            faDescription = self.faDescription
            if not faName:
                raise ValueError("Please enter a name for the FA")
            mycursor.execute("INSERT INTO fa_headers (name, type, start_state_name, description) VALUES (%s, %s, %s, %s)", 
            (faName, self.input_data["fatype"], startState, faDescription))
            faId = mycursor.lastrowid
            for state in self.states:
                is_accepting = True if state in self.acceptingStates else False
                mycursor.execute("INSERT INTO fa_states (fa_id, name, is_accepting) VALUES (%s, %s, %s)", 
                (faId, state, is_accepting))
            for symbol in self.symbols:
                mycursor.execute("INSERT INTO fa_symbols (fa_id, symbol_char) VALUES (%s, %s)", 
                (faId, symbol))
            for state, transitions in self.input_data['transitions'].items():
                for symbol, nextStates in transitions.items():
                    for nextState in nextStates:
                        mycursor.execute("INSERT INTO fa_transitions (fa_id, from_state_name, symbol_char, to_state_name) VALUES (%s, %s, %s, %s)", 
                        (faId, state, symbol, nextState))
            mydb.commit()
            print(f"{mycursor.rowcount} record inserted.")


        except mysql.connector.Error as err:
            print(f"Error: {err}")
    

class DesignFAScreenManager(ScreenManager):
    pass

designFaScreenKv = Builder.load_file('designFaScreenManager.kv')

class DesignFaScreenApp(App):
    def build(self):
        return designFaScreenKv
if __name__ == '__main__':
    DesignFaScreenApp().run()
