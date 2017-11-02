import pickle
import sys
import json

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from cryptography.fernet import Fernet

import paho.mqtt.client as mqtt

from pycrdt.crdt.crdt import CRDTDoc


class Editor(QPlainTextEdit):
    upd_text = pyqtSignal(str)  # in
    del_evt = pyqtSignal(int)  # out
    ins_evt = pyqtSignal(int, str)  # out

    def __init__(self):
        self.view = QPlainTextEdit.__init__(self)
        self.setFrameStyle(QFrame.NoFrame)

        self.font = QFont()
        self.font.setStyleHint(QFont.Monospace)
        self.font.setFixedPitch(True)
        self.setFont(self.font)

        self.upd_text.connect(self.on_upd_text)

    def keyPressEvent(self, e):
        cursor = self.textCursor()

        if e.key() == Qt.Key_Backspace:
            pos = cursor.position() - 1
            self.del_evt.emit(pos)

        elif e.text() and e.key() != Qt.Key_Backspace:
            pos = cursor.position()
            self.ins_evt.emit(pos, e.text())

        QPlainTextEdit.keyPressEvent(self, e)

    @pyqtSlot(str)
    def on_upd_text(self, text):
        cursor = self.textCursor()
        old_pos = cursor.position()
        self.setPlainText(text)
        cursor.setPosition(old_pos)
        self.setTextCursor(cursor)


class Main(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.key = b"7tLEmPE51jXJRwNUIu5zQOOsoMwjlfgydyVeI2n8guw="
        self.fernet = Fernet(self.key)

        self.site = int(input("Enter side no: "))
        self.pad_name = str(input("Enter pad name (type demo to start with some text): "))
        self.mqtt_name = f"test/pad/{self.pad_name}"

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("iot.eclipse.org", 1883, 60)

        self.window_title = f"PyCRDT Demo | Pad: {self.pad_name}"

        self.setWindowTitle(self.window_title)
        self.setGeometry(400, 400, 800, 600)

        self.editor = Editor()
        self.setCentralWidget(self.editor)

        self.doc = CRDTDoc()
        self.doc.site = self.site
        self.editor.del_evt.connect(self.on_del)
        self.editor.ins_evt.connect(self.on_ins)

        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe(self.mqtt_name)

    @pyqtSlot(int)
    def on_del(self, pos):
        patch = self.doc.delete(pos)
        self.client.publish(self.mqtt_name, "p ".encode() + self.fernet.encrypt(patch.encode()))

    @pyqtSlot(int, str)
    def on_ins(self, pos, char):
        patch = self.doc.insert(pos, char)
        self.client.publish(self.mqtt_name, "p ".encode() + self.fernet.encrypt(patch.encode()))

    def on_message(self, client, userdata, msg):
        code, payload = msg.payload.decode().split(" ")
        payload = self.fernet.decrypt(payload.encode())

        if code == "p":
            patch = json.loads(payload)
            if patch["src"] != self.site:
                self.doc.apply_patch(payload)
                self.editor.upd_text.emit(self.doc.text)
        elif code == "i":
            self.doc = pickle.loads(payload)
            self.doc.site = self.site

            self.editor.upd_text.emit(self.doc.text)


def main():
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    main = Main()
    main.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
