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
from datetime import datetime, date
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
        self.xlsx_pth = None        # path to the file
        self.import_invoker = None    # Service invoker
        self.export_invoker = None    # Service invoker
    #   # call Widget layout constructor
        super(BugalRoot, self).__init__(**kwargs)
    # parameters from the gui
    csv_pth_input = ObjectProperty(None)
    db_pth_input = ObjectProperty(None)
    zip_pth_input = ObjectProperty(None)
    toml_pth_input = ObjectProperty(None)
    xlsx_pth_input = ObjectProperty(None)

    start_year = ObjectProperty(None)
    start_month = ObjectProperty(None)
    start_day = ObjectProperty(None)
    end_year = ObjectProperty(None)
    end_month = ObjectProperty(None)
    end_day = ObjectProperty(None)

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
        # create invoker
        import_invoker = service.Invoker()
        # set invoker command
        import_invoker.set_main_command(service.CmdImportNewCsv(trepo, hrepo, stack, handl))

        return import_invoker

    def _create_export_invoker(self):
        """creates the export invoker by initialising receiver instances for
        commands

        Returns:
            service.Invoker: Invoker instance which can run the configured commands
        """
        trepo = repo.TransactionsRepo(pth=self.db_pth, db_type='sqlite')
        handl = handler.ExcelWriter(self.xlsx_pth)
        # calculate input data
        year1 = self.ids.start_year.text
        month1 = self.ids.start_month.text
        day1 = self.ids.start_day.text

        year2 = self.ids.end_year.text
        month2 = self.ids.end_month.text
        day2 = self.ids.end_day.text

        # startdate = datetime.strptime(str(datum), '%d.%m.%Y').date()
        startdate = date(int(year1), int(month1), int(day1))
        # enddate = datetime.strptime(str(datum), '%d.%m.%Y').date()
        enddate = date(int(year2), int(month2), int(day2))
        print(f'filter create: {startdate} - {enddate}')
        # create command
        cmd = service.CmdExportExcel(trepo, handl)
        cmd.set_filter(startdate, enddate, datum_range=True)
        # create invoker
        export_invoker = service.Invoker()
        # set invoker command
        export_invoker.set_main_command(cmd)

        return export_invoker

    # def _create_transaction_read_invoker(self) -> service.Invoker:
    #     year1 = self.ids.start_year.text
    #     month1 = self.ids.start_month.text
    #     day1 = self.ids.start_day.text

    #     year2 = self.ids.end_year.text
    #     month2 = self.ids.end_month.text
    #     day2 = self.ids.end_day.text

    #     datum = day1 + '.' + month1 + '.' + year1
    #     print(datum)
    #     startdate = datetime.strptime(datum, '%d.%m.%y').date()
    #     datum = day2 + '.' + month2 + '.' + year2
    #     print(datum)
    #     enddate = datetime.strptime(datum, '%d.%m.%y').date()
    #     read_invoker = service.CmdReadTransactions()
    #     read_invoker.set_filter([startdate, enddate], datum_range=True)
    #     return read_invoker

    def clear_input(self):
        """clearing the entered configuration from gui
        """
        self.ids.csv_pth_input.text = ''
        self.ids.db_pth_input.text = ''
        self.ids.zip_pth_input.text = ''
        self.ids.toml_pth_input.text = ''
        self.ids.xlsx_pth_input.text = ''

        message = 'title: the configuration is cleared'
        logger.info(message)
        Logger.info(message)        # prints message to console
        self._print_log(message)    # prints messag to gui

    def _validate_path(self, _path):
        message = ''
        if _path is None:
            message = "Path not configured"
            return (message, Path(_path))
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
        (validation, self.xlsx_pth) = self._validate_path(self.ids.xlsx_pth_input.text)
        message = message + 'Excel' + validation
        (validation, self.toml_pth) = self._validate_path(self.ids.toml_pth_input.text)
        message = message + 'TOML' + validation
        if self.toml_pth.is_file():
            message = f'use configuration from TOML file: {self.toml_pth} \n'
        else:
            cfg.TYPECLASS = self.input_type     # overwriting configuration from toml
            cfg.CSVFILE = self.csv_pth          # overwriting configuration from toml
            cfg.DBFILE = self.db_pth            # overwriting configuration from toml
            cfg.ARCHIVE = self.zip_pth          # overwriting configuration from toml
            cfg.EXCEL = self.xlsx_pth           # overwriting configuration from toml
        self.import_invoker = self._create_import_csv_invoker()
        message = message + f'Invoker result: {self.import_invoker}'

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
        if isinstance(self.import_invoker, service.Invoker):
            message = "start IMPORT"
            self.import_invoker.run_commands()
        else:
            message = "IMPORT service not configured properly"
        self._print_log(message)

    def do_export_cfg(self):
        """taking over configuration on pressed button
        """
        message = ''
        (validation, self.db_pth) = self._validate_path(self.ids.db_pth_input.text)
        message = message + 'DB' + validation
        (validation, self.xlsx_pth) = self._validate_path(self.ids.xlsx_pth_input.text)
        message = message + 'Excel' + validation
        # read_invoker = self._create_transaction_read_invoker()
        self.export_invoker = self._create_export_invoker()
        # self.export_invoker.set_on_start(read_invoker)
        message = message + f'Invoker result: {self.export_invoker}'

        print(message)
        logger.info("message")
        self._print_log(message)

    def do_export(self):
        """Invokes the export command on pressed button
        """
        if isinstance(self.export_invoker, service.Invoker):
            message = "start EXPORT"
            self.export_invoker.run_commands()
        else:
            message = "EXPORT service not configured properly"
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
