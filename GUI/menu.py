from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.app import App  
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from designFaScreenManager import DesignFaScreen

# Window.size = (1200, 800) # width, height 
Window.maximized = True
Window.clearcolor = (0.298, 0.345, 0.357, 1)

# Define different screens
class WelcomeScreen(Screen): 
    pass

class FaListsScreen(Screen):
    pass

class WindowScreenManager(ScreenManager):
    pass



# kv file
menuKv = Builder.load_file('menu.kv')   


class MenuApp(App):
    def build(self):
        mainScreen = WindowScreenManager()
        mainScreen.add_widget(WelcomeScreen(name='welcome'))
        mainScreen.add_widget(FaListsScreen(name='fa_lists'))
        mainScreen.add_widget(DesignFaScreen(name='design_fa'))
        return mainScreen
    
if __name__ == '__main__':
    MenuApp().run()  