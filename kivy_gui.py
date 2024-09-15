"""gui for the bugal App
The user can access the services from bugal App throug this GUI
to package with the pyinstaller:
 - open the kivy_gui.spec after exxecution the of the pyinstaller
 - import kivy packages:
    from kivy_deps import sdl2, glew
 - designate the kv file:
    after pyz .. enter
    a.data += [('Code\bugal.kv', 'absolute path to the file', 'DATA')]
    Example: c:\\projects\\910_prprojects\\bugal\\bugal.kv
 - extend coll
    - after exe add the path: COLLECT(exe, Tree('c:\\projects\\910_prprojects\\bugal\\'),)
    - after a.datas add: *[Tree(p) for p in (sdl2.dep_bins + glew.de_bins)]
 - rebuild pyinstaller bugal.spec -y
"""

from pathlib import Path
import logging
# import sys

# import kivy
from kivy.app import App
# from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.properties import ObjectProperty

from bugal import service
from bugal import model
from bugal import repo
from bugal import csv_adapter
from bugal import handler
from bugal import cfg

logging.basicConfig(filename='bugal.log',
                    filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


# set the App size at the start
Window.size = (1000, 500)
Logger.info("Loading layout.kv file...")
# load the kivy layout file
relativer_pfad = Path(__file__).parent / 'layout.kv'
Builder.load_file(str(relativer_pfad))


class BugalRoot(FloatLayout):
    """Bugal GUI builder
    """
    def __init__(self, **kwargs):
        self.input_type = None      # the type of the csv
        self.csv_pth = None         # path to the file
        self.db_pth = None          # path to the file
        self.zip_pth = None         # path to the file
        self.toml_pth = None        # path to the file
        self.srvc_invoker = None    # Service invoker
    #     # call Widget layout constructor
        super(BugalRoot, self).__init__(**kwargs)
    # parameters from the gui
    csv_pth_input = ObjectProperty(None)
    db_pth_input = ObjectProperty(None)
    zip_pth_input = ObjectProperty(None)
    toml_pth_input = ObjectProperty(None)

    def _print_log(self, message):
        # addressing the IDs from the gui
        self.ids.gui_log.text = message

    def _create_import_csv_invoker(self):
        """creates the import csv invoker by initialising receiver instances for
        commands

        Returns:
            service.Invoker: Invoker instance which can run the configured commands
        """
        # get receivers with the parameters from the gui
        stack = model.Stack(self.input_type)
        handl = handler.CSVImporter(self.csv_pth)
        trepo = repo.TransactionsRepo(pth=self.db_pth)
        hrepo = repo.HistoryRepo(pth=self.db_pth)
        adapter = csv_adapter.ImporterAdapter(self.csv_pth)
        # create invoker
        import_invoker = service.Invoker()
        # set invoker command
        # import_invoker.set_main_command(service.CmdImportNewCsv(trepo, hrepo, stack, handl))
        import_invoker.set_main_command(service.CmdImportClassic(trepo, hrepo, adapter))
        return import_invoker

    def clear_input(self):
        """clearing the entered configuration from gui
        """
        self.ids.csv_pth_input.text = ''
        self.ids.db_pth_input.text = ''
        self.ids.zip_pth_input.text = ''
        self.ids.toml_pth_input.text = ''
        self.srvc_invoker = None
        message = 'title: the configuration is cleared'
        logger.info(message)
        Logger.info(message)        # prints message to console
        self._print_log(message)    # prints messag to gui

    def _validate_path(self, _path):
        message = ''
        if len(_path) > 0:
            if Path(_path).is_dir():
                message = message + ' - Path configured ok \n'
            elif Path(_path).is_file():
                str(Path(_path).suffix)
                message = message + ' - File configured ok \n'
            else:
                message = message + ' - Path is incorrect \n'
                return (message, '')
        else:
            message = message + ' - Path will use working directory \n'
        return (message, Path(_path))

    def configure(self):
        """taking over configuration on pressed button
        """
        message = ''
        (classic, beta) = self.get_input_type()
        if classic:
            self.input_type = cfg.TransactionListClassic
        elif beta:
            self.input_type = cfg.TransactionListBeta
        else:
            message = message + 'ERROR: Input Type configuration failed'
        message = message + f'Input type: {self.input_type} \n'
        (validation, self.csv_pth) = self._validate_path(self.ids.csv_pth_input.text)
        message = message + 'CSV' + validation
        (validation, self.db_pth) = self._validate_path(self.ids.db_pth_input.text)
        message = message + 'DB' + validation
        (validation, self.zip_pth) = self._validate_path(self.ids.zip_pth_input.text)
        message = message + 'ZIP' + validation
        (validation, self.toml_pth) = self._validate_path(self.ids.toml_pth_input.text)
        message = message + 'TOML' + validation
        if self.toml_pth.is_file():
            message = f'use configuration from TOML file: {self.toml_pth} \n'
        else:
            cfg.TYPECLASS = self.input_type     # overwriting configuration from toml
            cfg.CSVFILE = self.csv_pth          # overwriting configuration from toml
            cfg.DBFILE = self.db_pth            # overwriting configuration from toml
            cfg.ARCHIVE = self.zip_pth          # overwriting configuration from toml

        self.srvc_invoker = self._create_import_csv_invoker()
        message = message + f'Invoker result: {self.srvc_invoker}'

        print(message)
        logger.info("message")
        self._print_log(message)

    def get_input_type(self):
        """Getting status Radio box Input type

        Returns:
            tupple: (classic: bool, beta: bool)
        """
        rb_classic = self.ids.rb_classic.active
        rb_beta = self.ids.rb_beta.active
        return (rb_classic, rb_beta)

    def do_import(self):
        """Invokes the import command on pressed button
        """
        if isinstance(self.srvc_invoker, service.Invoker):
            message = "start IMPORT"
            self.srvc_invoker.run_commands()
        else:
            message = "IMPORT service not configured properly"
        self._print_log(message)


class BugalApp(App):
    """Bugal Application
    """
    def build(self):
        """ initializing and returning the root widget
        """
        # return Label(text="KIVY BUGALTERIA")
        logger.warning("Building App")
        return BugalRoot()


if __name__ == "__main__":
    logger.info("main function started")
    app = BugalApp()
    logger.warning("App was built - start to run")
    app.run()
