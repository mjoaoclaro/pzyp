"""
Common utilities, most of them useful for a Qt related project.
"""

import os
import pathlib
import sys
import json 
from importlib import reload as reload_module, import_module, invalidate_caches
from subprocess import run as run_proc

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import QStandardPaths

all = [
    'msg_box', 'show_info', 'show_error',
    'add_table_widget_row', 'add_table_widget_rows',
    'load_qt_ui',
    'get_standard_location',
    'connectev',
    'dump_objs',
    'gen_unique_path_from',
    'overwrite_if_needed_or_exit',
    'exists_or_exit',
]

################################################################################
##
##      QT
##
################################################################################

UIC_COMPILER = 'pyside6-uic'

def msg_box(msg, icon_type):
    mbox = QMessageBox()
    mbox.setText(msg)
    mbox.setIcon(icon_type)
    mbox.exec()
#:

def show_info(msg):
    msg_box(msg, icon_type=QMessageBox.Information)
#:

def show_error(msg):
    msg_box(msg, icon_type=QMessageBox.Critical)
#:

def compile_ui_if_needed(ui_file_path: str, ignore_mtime: bool=False):
    """
    The following will dynamically compile the Qt Designer '.ui' file
    given by C{ui_file_path}, and import and load the generated Python
    module. The generated module will have the name: 
        
        C{ui_file_path} + '_ui.py'

    The '.ui' file will only be compiled if it's more recent that a
    previous instance of the generated module, or if this generated
    module doesn't exist at all (perhaps it's the first compilation).

    @param ui_file_path: The file path for the Qt Designer 'ui' file.
    @param ignore_mtime: If True, modification times for the ui file
    and the corresponding generated modules will be ignored and the
    ui file will ALWAYS be COMPILED.
    @returns The imported and reloaded C{module} object.
    """
    if not os.path.exists(ui_file_path):
        raise ValueError(f"Can't find UI file {ui_file_path}")
    #:
    if not ui_file_path.endswith('.ui'):
        raise ValueError(f"UI file path ('{ui_file_path}') must end in '.ui'!")
    #:
    gen_module_name = ui_file_path.strip('.ui') + '_ui'
    gen_module_path = gen_module_name + '.py'

    ui_mtime = os.path.getmtime(ui_file_path)
    gen_mod_mtime = os.path.getmtime(gen_module_path)

    if (
            not os.path.exists(gen_module_path) or 
            (not ignore_mtime and ui_mtime > gen_mod_mtime)
        ):
        print(f"Compiling '{ui_file_path}' to '{gen_module_path}'.", file=sys.stderr)
        run_proc(['pyside6-uic', '-o', gen_module_path, ui_file_path])
        print(f"Loading '{gen_module_name}' module", file=sys.stderr)
    #:

    # We want to make sure that the module is up to date, whether it 
    # was imported before or not. import_module won't really import the 
    # module if the module was imported before (it just returns the module
    # object). OTOH, reload won't reload if the module wasn't imported 
    # before. That's why wee need to import and then do a reload.
    invalidate_caches()
    return reload_module(import_module(gen_module_name))
#:

def add_table_widget_row(
    table, 
    row_num, 
    row_obj, 
    editable=False, 
    extract_col_values=None,
):
    if not row_obj:
        raise ValueError("No row object (with column values) was given.")

    col_values = extract_col_values(row_obj) if extract_col_values else row_obj

    for col, col_val in enumerate(col_values):
        cell = QTableWidgetItem()
        cell.setText(col_val)
        flags = cell.flags()
        if editable:
            flags |= Qt.ItemFlags.ItemIsEditable
        cell.setFlags(flags)
        table.setItem(row_num, col, cell)
#:

def add_table_widget_rows(
    table, 
    row_objs, 
    editable=False,
    extract_col_values=None,
):
    """
    Add a row to `table` for each object in `row_objs`. Rows will be 
    numbered from 1.
    """
    table.clearContents()
    table.setRowCount(len(row_objs))
    sorting_enabled = table.isSortingEnabled()
    table.setSortingEnabled(False)
    for row_num, row_obj in enumerate(row_objs):
        add_table_widget_row(
            table, 
            row_num,
            row_obj=row_obj,
            editable=editable,
            extract_col_values=extract_col_values,
        )
    table.setSortingEnabled(sorting_enabled)
#:

def get_standard_location(name, first_location_only=True):
    """
    A wrapper for C{QStandardPaths.standardLocations} with predefined 
    keys:
        'home'    -> C{QStandardPaths.HomeLocation}
        'desktop' -> C{QStandardPaths.DesktopLocation}
        'docs'    -> C{QStandardPaths.DocumentsLocation}
        ... look at variable C{locs} to know the rest of the keys 

    This wrapper function returns a string with the first path found
    for the given C{name} if C{first_location_only} is C{True}, 
    otherwise all paths are returned. In some platforms it's possible
    to get several paths for the same key.
    """
    locs = {
        'home': QStandardPaths.HomeLocation,
        'desktop': QStandardPaths.DesktopLocation,
        'docs': QStandardPaths.DocumentsLocation,
        'apps_location': QStandardPaths.ApplicationsLocation,
        'music': QStandardPaths.MusicLocation,
        'movies': QStandardPaths.MoviesLocation,
        'pictures': QStandardPaths.PicturesLocation,
        'config': QStandardPaths.ConfigLocation,
    }
    paths = QStandardPaths.standardLocations(locs[name]) 
    return paths[0] if first_location_only else paths
#:

def connectev(
        widget, 
        event_name, 
        event_handler, 
        parent=None, 
        call_base_after=False,
        call_base_before=False
):
    """
    Connect C{event_handler} to the event given C{event_name}.
    C{event_name} must be a valid event for C{widget}. An optional
    C{parent} (eg, a window or dialog) can be passed and will
    be included in the call to C{event_handler} as the 1st argument.

    Example: 
    C{connectev(self.line_edit, 'keyPressEvent', self.method)}

    @param widget: The widget that responds to the event.
    @param event_name: A string with the event name (eg,
    C{'focusInEvent'})
    @param event_handler: A function to handle the event. It should
    have one or two parameters: the event object (not the name) and,
    if C{parent} is passed, this parent object. The event object is
    the last argument.
    @param parent: A parent widget. This can be useful if one wants
    to use an outside function as the event handler and still pass
    the parent widget for context.
    @param call_base_aftter: Whether to call the base event handler 
    after the new {event_handler}.
    @return: Nothing.
    """
    def call_event_handler(event):
        if call_base_before:
            base_method(event)
        event_handler(event, *event_handler_args)
        if call_base_after:
            base_method(event)
    #:

    event_handler_args = (widget, parent) if parent else (widget,)
    base_method = getattr(widget, event_name)
    setattr(
        widget, 
        event_name,
        call_event_handler
    )
    setattr(
        widget, 
        f'__{event_name}_old_handler__',
        base_method
    )
#:

def disconnectev(
        widget, 
        event_name,
):
    base_method_name =  f'__{event_name}_old_handler__'
    if not (base_method := getattr(widget, base_method_name)):
        raise AttributeError(f'Reference to event {event_name} not found')
    #:
    setattr(
        widget,
        event_name,
        base_method
    )
    delattr(widget, base_method_name)
#:

#######################################################################
##
##   OTHER STUFF
##
#######################################################################


def dump_objs(objs_iter, dump_fn=json.dumps):
    """
    'Dumpa' um iterável de objectos do mesmo tipo para um array de 
    objectos de JSON. Recebe uma função para 'dumpar' os objectos 
    individuais. Atenção que em JSON só existe uma forma de representar 
    conjuntos de elementos: o array, que equivale a uma C{list}a em 
    Python. Assim sendo, esta função devolve um JSON-array que, à 
    semelhança de uma lista de Python, é delimitado por '[' e ']'.
    """
    return '[%s]' % ','.join((dump_fn(obj) for obj in objs_iter))


def gen_unique_path_from(path_: str) -> str:
    """
    Generates a unique file path from C{path_} if the given 
    {path_} exists. Otherwise, just returns that path.
    Returns a C{str} with the new unique path.
    """
    if not path_:
        raise ValueError('Empty path')
    path_ext = pathlib.Path(path_).suffix
    path_and_name = path_.partition(path_ext)[0] if path_ext else path_
    i = 2
    while os.path.exists(path_):
        path_ = f'{path_and_name}_{i}{path_ext}'
        i += 1
    return path_
#:

def overwrite_if_needed_or_exit(dest_file_path: str, error_code=3):
    if os.path.exists(dest_file_path):
        answer = input(f"File {dest_file_path} exists. Overwrite (y or n)? ")
        if answer.strip().lower() != 'y':
            print("File will not be overwritten")
            sys.exit(error_code)
    #:
#:

def exists_or_exit(file_path, error_code=3):
    if not os.path.exists(file_path):
        print(f"File {file_path} doesn't exist", file=sys.stderr)
        sys.exit(error_code)
    #:
#:

# def recuren(old, new):
#     """
#     RECUrsively REName files with pattern `old` to
#     replacing that pattern with `new`.
#     """
#     for p, _, filenames in os.walk('.'):
#         for old_name in filenames:
#             new_name = new.join(old_name.split(old))
#             os.rename(p + os.sep + old_name, p + os.sep + new_name)
