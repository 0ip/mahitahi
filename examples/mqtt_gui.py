#!/usr/bin/env python3
import pickle
import sys
import json

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from cryptography.fernet import Fernet

import paho.mqtt.client as mqtt

sys.path.append("..")
from mahitahi import Doc


class Editor(QTextEdit):
    upd_text = pyqtSignal(str)  # in
    del_evt = pyqtSignal(str)  # out
    ins_evt = pyqtSignal(str)  # out

    def __init__(self, site):
        self.view = QPlainTextEdit.__init__(self)
        self.setFrameStyle(QFrame.NoFrame)

        self.font = QFont()
        self.font.setStyleHint(QFont.Monospace)
        self.font.setFixedPitch(True)
        self.font.setPointSize(16)
        self.setFont(self.font)

        self.doc = Doc()
        self.doc.site = site

        self.upd_text.connect(self.on_upd_text)

        shortcut_f3 = QShortcut(QKeySequence("F3"), self)
        shortcut_f3.activated.connect(self.debug_crdt)

        shortcut_f4 = QShortcut(QKeySequence("F4"), self)
        shortcut_f4.activated.connect(self.debug_widget)

        shortcut_f5 = QShortcut(QKeySequence("F5"), self)
        shortcut_f5.activated.connect(self.reload_from_crdt)

    def keyPressEvent(self, e):
        cursor = self.textCursor()

        if e.matches(QKeySequence.Paste) and QApplication.clipboard().text():
            pos = cursor.position()
            for i, c in enumerate(QApplication.clipboard().text()):
                patch = self.doc.insert(pos + i, c)
                self.ins_evt.emit(patch)

        elif e.key() == Qt.Key_Backspace:
            sel_start = cursor.selectionStart()
            sel_end = cursor.selectionEnd()
            if sel_start == sel_end:
                patch = self.doc.delete(cursor.position() - 1)
                self.del_evt.emit(patch)
            else:
                for pos in range(sel_end, sel_start, -1):
                    patch = self.doc.delete(pos - 1)
                    self.del_evt.emit(patch)

        elif e.key() != Qt.Key_Backspace and e.text() and e.modifiers() != Qt.ControlModifier:
            sel_start = cursor.selectionStart()
            sel_end = cursor.selectionEnd()
            if sel_start != sel_end:
                for pos in range(sel_end, sel_start, -1):
                    patch = self.doc.delete(pos - 1)
                    self.del_evt.emit(patch)

            patch = self.doc.insert(sel_start, e.text())
            self.ins_evt.emit(patch)

        QTextEdit.keyPressEvent(self, e)

    @pyqtSlot(str)
    def on_upd_text(self, patch):
        self.doc.apply_patch(patch)

        cursor = self.textCursor()
        old_pos = cursor.position()
        self.setPlainText(self.doc.text)
        cursor.setPosition(old_pos)
        self.setTextCursor(cursor)

    def debug_crdt(self):
        self.doc.debug()

    def debug_widget(self):
        print(self.toPlainText().encode())

    def reload_from_crdt(self):
        self.setPlainText(self.doc.text)


class AuthorHighlighter(QSyntaxHighlighter):

    def __init__(self, parent):
        QSyntaxHighlighter.__init__(self, parent)
        self.parent = parent

    def highlightBlock(self, text):
        curr_line = self.previousBlockState() + 1

        doc_line = 0
        block_pos = 0

        text_format = QTextCharFormat()

        for c, a in zip(self.parent.doc.text, self.parent.doc.authors[1:-1]):
            if c in ("\n", "\r"):
                doc_line += 1
                continue
            else:
                if doc_line == curr_line:
                    color = QColor(255, 255, 255)

                    if a == 1:
                        color = QColor(187, 222, 251)
                    elif a == 2:
                        color = QColor(222, 187, 251)
                    elif a == 3:
                        color = QColor(222, 251, 187)

                    text_format.setBackground(QBrush(color, Qt.SolidPattern))

                    self.setFormat(block_pos, 1, text_format)

                    block_pos += 1
                elif doc_line > curr_line:
                    break

        self.setCurrentBlockState(self.previousBlockState() + 1)


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

        self.window_title = f"MahiTahi Demo | Pad: {self.pad_name} | Site: {self.site}"

        self.setWindowTitle(self.window_title)
        self.setGeometry(400, 400, 800, 600)

        self.editor = Editor(self.site)
        self.highlighter = AuthorHighlighter(self.editor)
        self.setCentralWidget(self.editor)

        self.editor.del_evt.connect(self.on_del)
        self.editor.ins_evt.connect(self.on_ins)

        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        self.client.subscribe(self.mqtt_name, qos=2)

    @pyqtSlot(str)
    def on_del(self, patch):
        print(f"Sending patch: {patch}")
        self.client.publish(self.mqtt_name, "p ".encode() +
                            self.fernet.encrypt(patch.encode()), qos=2)

    @pyqtSlot(str)
    def on_ins(self, patch):
        print(f"Sending patch: {patch}")
        self.client.publish(self.mqtt_name, "p ".encode() +
                            self.fernet.encrypt(patch.encode()), qos=2)

    def on_message(self, client, userdata, msg):
        code, payload = msg.payload.decode().split(" ")
        payload = self.fernet.decrypt(payload.encode())

        if code == "p":
            patch = json.loads(payload)
            if patch["src"] != self.site:
                print(f"Received patch: {payload}")

                self.editor.upd_text.emit(payload.decode())
        elif code == "i":
            doc = pickle.loads(payload)
            for c in doc._doc[1:-1]:
                self.editor.upd_text.emit(doc._serialize("i", c))


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
