import mysql.connector

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import StringProperty
from kivy.lang import Builder

Window.maximize()


try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        database="automatadb",
        password="root"
    )
    my_cursor = mydb.cursor(dictionary=True)
    my_cursor.execute("select * from fa_headers")
    fa_headers = my_cursor.fetchall()
    # my_cursor.execute("select * from fa_states")
    # fa_states = my_cursor.fetchall()
    # my_cursor.execute("select * from fa_symbols")
    # fa_symbols = my_cursor.fetchall()
    # my_cursor.execute("select * from fa_transitions")
    # fa_transitions = my_cursor.fetchall()

except mysql.connector.Error as err:
    print(f"Error: {err}")
    fa_headers = []

finally:
    if 'my_cursor' in locals() and my_cursor is not None:
        my_cursor.close()
    if 'mydb' in locals() and mydb.is_connected():
        mydb.close()
    
 
# def convert_fa_data_to_dict(fa_name_to_fetch):
#     fa_header = None
#     for header in fa_headers:
#         if header["name"] == fa_name_to_fetch:
#             fa_header = header
#             break

#     if not fa_header:
#         print(f"FA '{fa_name_to_fetch}' not found in the DB headers.")
#         return None

#     fa_id = fa_header["id"]
#     fa_data_dict = {
#         "name": fa_header["name"],
#         "type": fa_header["type"],
#         "start_state": fa_header["start_state_name"]
#     }

#     # 1. Get States
#     fa_data_dict["states"] = []
#     for state_row in fa_states:
#         if state_row["fa_id"] == id:
#             fa_data_dict["states"].append({
#                 "name": state_row["name"],
#                 "is_accepting": state_row["is_accepting"]
#             })

#     # 2. Get Symbols
#     fa_data_dict["alphabet"] = []
#     for symbol_row in fa_symbols:
#         if symbol_row["fa_id"] == fa_id:
#             fa_data_dict["alphabet"].append(symbol_row["symbol_char"])

#     # 3. Get and Group Transitions (integrating Code 2 logic)
#     raw_transitions_for_fa = []
#     for trans_row in fa_transitions:
#         if trans_row["fa_id"] == fa_id:
#             raw_transitions_for_fa.append(trans_row)

#     # Intermediate dictionary to group transitions
#     grouped_transitions = {}
#     for row in raw_transitions_for_fa:
#         from_state = row['from_state_name']
#         symbol = row['symbol_char']
#         to_state = row['to_state_name']

#         key = (from_state, symbol)
#         if key not in grouped_transitions:
#             grouped_transitions[key] = [] # Initialize with an empty list
        
#         # Only add to_state if it's not None (representing no transition)
#         if to_state is not None:
#             grouped_transitions[key].append(to_state)

#     # Now, transform into the list of dictionaries needed for the final JSON
#     fa_data_dict["transitions"] = []
#     for (from_state, symbol), to_states_list in grouped_transitions.items():
#         fa_data_dict["transitions"].append({
#             "from": from_state,
#             "symbol": symbol,
#             "to": to_states_list # This is already a list, perfect for JSON array
#         })
    
#     # Sort transitions for consistent output (optional, but good for debugging)
#     # Sort by from_state, then by symbol
#     fa_data_dict["transitions"].sort(key=lambda x: (x['from'], x['symbol']))

#     # Option selected on the GUI
#     fa_data_dict["toConvertNFA"] = True;
#     fa_data_dict["toTestInput"] = False;
#     fa_data_dict["toMinimize"] = False;

#     return fa_data_dict

class FA(BoxLayout):
    fa_name = StringProperty('')
    fa_type = StringProperty('')
    fa_description = StringProperty('')

    def __init__(self,fa, **kwargs):
        super().__init__(**kwargs)
        self.fa_name = fa['name']
        self.fa_type = fa['type']
        self.fa_description = fa['description']
class MainWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for fa in fa_headers:
            self.add_widget(FA(fa))

        


class AutomataApp(App):
   
    def build(self):
        return MainWidget()

if __name__ == '__main__':
    AutomataApp().run()


