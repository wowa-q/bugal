import pathlib

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
# from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty, NumericProperty
# set the App size at the start

Window.size = (500, 150)
Logger.info("Loading layout.kv file...")
# load the kivy layout file
kv_path = pathlib.Path(__file__).parent / 'sandbox.kv'
# kv_path = pathlib.Path(__file__).parent / 'bugal_gui.kv'
Builder.load_file(str(kv_path))

class BugalWinTemplate(BoxLayout):
    def do_open_import_config_window(self):
        App.get_running_app().stop()
        BugalImportConfigApp().run()

    def do_open_export_config_window(self):
        App.get_running_app().stop()
        BugalExportApp().run()

    def do_open_start_window(self):
        App.get_running_app().stop()
        BugalStartApp().run()


    def close_app(self):
        App.get_running_app().stop()

class BugalStartWindow(BugalWinTemplate):
    def do_open_import_config_window(self):
        App.get_running_app().stop()
        BugalImportConfigApp().run()

    def do_open_export_config_window(self):
        App.get_running_app().stop()
        BugalExportApp().run()

    def close_app(self):
        App.get_running_app().stop()

class BugalImportConfigWindow(BugalWinTemplate):
    def do_get_csv_file(self, file_path, usr_path):
        if file_path:
            # Zeigt die ausgewählte Datei an
            print(f"Selected file: {file_path[0]}")
            # popup = Popup(title="File Selected",
            #               content=Label(text=f"Selected: {file_path[0]}"),
            #               size_hint=(0.5, 0.5))
            # popup.open()
            print(file_path)
        else:
            print("No file selected")

    def cancel_selection(self):
        print("Selection canceled")

    def on_spinner_select(self, text):
        print(f"Selected: {text}")

class BugalProcessWindow(BugalWinTemplate):
    pass

class BugalExportConfigWindow(BugalWinTemplate):
    FLOOR = NumericProperty(0)  # Definiert eine numerische Eigenschaft mit einem Standardwert von 0
    lower_len = 100  # Beispielwert
    PCAP_HEIGHT = 20  # Beispielwert
    PIPE_GAP = 10 # Beispielwert
    upper_len = 100  # Beispielwert
    tx_pipe = ObjectProperty(None)  # Beispielwert
    tx_pcap = ObjectProperty(None)  # Beispielwert
    lower_coords = ListProperty([0, 0, 1, 1])  # Beispielwert
    upper_coords = ListProperty([0, 0, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.zoom = 1

    def do_open_start_window(self):
        App.get_running_app().stop()
        BugalStartApp().run()

    def close_app(self):
        App.get_running_app().stop()

class BugalStartApp(App):
    def build(self):
        return BugalStartWindow()

    def do_open_import_config_window(self):
        # Beende das aktuelle Fenster und öffne das zweite
        self.stop()  # Schließe die aktuelle App
        BugalImportConfigApp().run()  # Starte eine neue App

    def open_first_window(self):
        # Beende das aktuelle Fenster und öffne das erste
        self.stop()  # Schließe die aktuelle App
        BugalStartApp().run()  # Starte die ursprüngliche App

class BugalImportConfigApp(App):
    def build(self):
        Window.size = (700, 500)
        return BugalImportConfigWindow()

class BugalProcessApp(App):
    def build(self):
        return BugalProcessWindow()

class BugalExportApp(App):
    def build(self):
        return BugalExportConfigWindow()

if __name__ == '__main__':

    print(kv_path)
    BugalStartApp().run()
