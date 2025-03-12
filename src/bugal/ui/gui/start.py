import pathlib

from kivy.app import App
# from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.popup import Popup
# from kivy.uix.label import Label
# from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty, NumericProperty
# set the App size at the start
from pathlib import Path

from cfg import config as cfg
from libs import exceptions as err
from bugal.srvc import service as srvc

Window.size = (500, 150)
Logger.info("Loading layout.kv file...")
# load the kivy layout file
kv_path = pathlib.Path(__file__).parent / 'sandbox.kv'
# kv_path = pathlib.Path(__file__).parent / 'bugal_gui.kv'
Builder.load_file(str(kv_path))
global_config = cfg.get_config()

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
    def do_select_file(self, file_path, usr_path):
        if file_path:            
            # Zeigt die ausgewählte Datei an
            print(f"Selected file: {file_path[0]}")
            file_ = Path(file_path[0])
            if file_.is_file():
                match file_.suffix:
                    case '.csv':
                        self._print_log(f'csv file configured: {file_}')
                        global_config.import_path = file_
                    case '.db':
                        self._print_log(f'db file configured: {file_}')
                        global_config.dbpath = file_
                    case '.zip':
                        self._print_log(f'zip file configured: {file_}')
                        global_config.archive = file_
                    case '.xls':
                        self._print_log(f'Excel file configured: {file_}')
                        global_config.export_path = file_
                    case _:
                        msg = f'File selector selected wrong file type: {file_.suffix}'
                        self._print_log(msg)
                        raise err.NoValidInputFilesFound(msg)
                        # return None # TODO: einen Fehler schmeißen
        else:
            print("No file selected")
            return None
    
    def _print_log(self, message):
        # addressing the IDs from the gui
        self.ids.gui_log.text = message

    def do_run_import(self):
        self._print_log('Import process started')
        
        if global_config is None:
            self._print_log('Configuration Failed!')
            print('Configuration Failed!')
            raise err.BaseBugalModelError('configuration Gui failed')
        
        result = srvc.import_data(global_config)
        msg = f'''
            Import finished with following configuration:
            csv file: {global_config.import_path}
            db file:  {global_config.dbpath}
            zip file: {global_config.archive}
            Import result: {result}
        '''
        self._print_log(msg)

    def on_spinner_import_type_select(self, text):
        self._print_log(f'Import type configured: {text}')
        global_config.import_type = text

    def on_spinner_db_type_select(self, text):
        self._print_log(f'DB type configured: {text}')
        global_config.dbtype = text
    

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
