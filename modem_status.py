import sys
import threading
import time
import configparser
import logging
import os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QIcon
from ping3 import ping



if not os.path.exists('log'):
    os.makedirs('log')

# Konfiguracja loggera
log_filename = os.path.join('log', 'connection.log')
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

def check_connection(tray_icon, host):
    previous_status = None

    while True:
        result = ping(host)
        if result is not None:
            if result < 1:
                status_text = "Status: Ok"
                previous_status = set_status(tray_icon, status_text, ICON_OK, previous_status)
                log_message = f"[OK] Polaczenie ok - {host}"
                logging.info(log_message)
            else:
                status_text = "Status: Błąd"
                previous_status = set_status(tray_icon, status_text, ICON_ERROR, previous_status)
                log_message = f" Blad polaczenia - {host}"
                logging.error(log_message)
        else:
            status_text = "Status: Błąd"
            previous_status = set_status(tray_icon, status_text, ICON_ERROR, previous_status)
            log_message = f" Blad polaczenia - {host}"
            logging.error(log_message)
        time.sleep(10)

def read_host_from_config():
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    host = config['Connection']['host']
    return host

def on_click():
    pass

def on_info():
    message_box = QMessageBox()
    message_box.setIcon(QMessageBox.Information)
    message_box.setWindowTitle("Informacja")
    message_box.setText("Autor: Mikołaj Kempa")
    ok_button = message_box.addButton('OK', QMessageBox.AcceptRole)
    ok_button.clicked.connect(restart_app)
    message_box.exec_()

def on_select(action):
    if action == action_exit:
        print("Wyłączono aplikację")
        sys.exit()

def set_status(tray_icon, status_text, icon_path, previous_status):
    if previous_status != status_text:
        show_notification(status_text, icon_path)
        tray_icon.setIcon(QIcon(icon_path))
        tray_icon.setToolTip("Modem ok" if status_text == "Status: Ok" else "Błąd modemu")
        return status_text
    return previous_status

def show_notification(message, icon_path):
    tray_icon.showMessage("Monitor połączenia", message, QIcon(icon_path), 5000)

def restart_app():
    # Uruchom ponownie aplikację (skrypt)
    python_script = sys.executable
    os.execl(python_script, python_script, *sys.argv)

app = QApplication(sys.argv)
tray_icon = QSystemTrayIcon(QIcon('img/green_dot.ico'), app)
tray_icon.setToolTip('Modem ok')

menu = QMenu()

action_exit = QAction('Zamknij', menu)
action_info = QAction('Info', menu)

action_exit.triggered.connect(lambda: on_select(action_exit))
action_info.triggered.connect(on_info)

menu.addSeparator()
menu.addAction(action_info)
menu.addAction(action_exit)

tray_icon.setContextMenu(menu)
tray_icon.activated.connect(on_click)
tray_icon.show()

ICON_OK = 'img/green_dot.ico'
ICON_ERROR = 'img/red_dot.ico'

connection_thread = threading.Thread(target=check_connection, args=(tray_icon, read_host_from_config()))
connection_thread.daemon = True
connection_thread.start()

sys.exit(app.exec_())
