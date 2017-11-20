#!/usr/bin/env python3
import sys
import json
import uuid
import base64
import random

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from cryptography.fernet import Fernet

import paho.mqtt.client as mqtt

sys.path.append("..")
from mahitahi import Doc


class Main(QMainWindow):

    HOST = "iot.eclipse.org"

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.patch_stack = []
        self.author = False

        resp, ok = QInputDialog.getText(
            self, "Portal Setup", "Paste a Portal ID or click cancel to create a new ID:"
        )

        if not ok:
            self.portal_id, self.pad_name, self.fernet_key = self.generate_portal_tuple()
            self.author = True
            print(f"Share this portal ID:\n\n  {self.portal_id}")
        else:
            self.pad_name, self.fernet_key = self.parse_portal_id(resp)

        self.fernet = Fernet(self.fernet_key)
        self.site = int(random.getrandbits(32))
        self.mqtt_name = f"mahitahi/pad/{self.pad_name}"
        self.subs = {
            self.mqtt_name + "/aloha": self.on_topic_aloha,
            self.mqtt_name + "/patch": self.on_topic_patch
        }

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.HOST, 1883, 60)

        self.window_title = f"MahiTahi Demo | Pad: {self.pad_name} | Site: {self.site} | Author: {self.author}"

        self.setWindowTitle(self.window_title)
        self.setGeometry(400, 400, 800, 600)

        self.editor = Editor(self.site)
        self.highlighter = AuthorHighlighter(self.editor)
        self.setCentralWidget(self.editor)

        self.editor.change_evt.connect(self.on_change)

        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        for topic in self.subs.keys():
            self.client.subscribe(topic, qos=2)

        if not self.author:
            self.client.publish(self.mqtt_name + "/aloha", "a")

    def generate_portal_tuple(self, include_server=False):
        pad = uuid.uuid4().hex
        key = Fernet.generate_key().decode()

        temp_str = ""
        if include_server:
            temp_str += f"{self.HOST}:"

        temp_str += f"{pad}:{key}"

        return base64.b64encode(temp_str.encode()).decode(), pad, key.encode()

    def parse_portal_id(self, portal_id):
        tup = base64.b64decode(portal_id.encode()).decode().split(":")

        if len(tup) == 2:
            pad, key = tup
            return pad, key.encode()
        elif len(tup) == 3:
            server, pad, key = tup
            return server, pad, key.encode()

    @pyqtSlot(str)
    def on_change(self, patch):
        print(f"Sending patch: {patch}")
        payload = self.fernet.encrypt(patch.encode())
        self.patch_stack.append(payload)
        self.client.publish(self.mqtt_name + "/patch", payload, qos=2)

    def on_message(self, client, userdata, msg):
        self.subs[msg.topic](msg.payload)

    def on_topic_aloha(self, payload):
        if self.author:
            for patch in self.patch_stack:
                self.client.publish(self.mqtt_name + "/patch", patch, qos=2)

    def on_topic_patch(self, payload):
        if payload not in self.patch_stack:
            payload_decrypted = self.fernet.decrypt(payload)
            patch = json.loads(payload_decrypted)
            if patch["src"] != self.site:
                print(f"Received patch: {payload_decrypted.decode()}")
                self.patch_stack.append(payload)
                self.editor.upd_text.emit(payload_decrypted.decode())


class Editor(QTextEdit):
    upd_text = pyqtSignal(str)  # in
    change_evt = pyqtSignal(str)  # out

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
                self.change_evt.emit(patch)

        elif e.key() == Qt.Key_Backspace:
            if not self.toPlainText():
                return

            sel_start = cursor.selectionStart()
            sel_end = cursor.selectionEnd()
            if sel_start == sel_end:
                patch = self.doc.delete(cursor.position() - 1)
                self.change_evt.emit(patch)
            else:
                for pos in range(sel_end, sel_start, -1):
                    patch = self.doc.delete(pos - 1)
                    self.change_evt.emit(patch)

        elif e.key() != Qt.Key_Backspace and e.text() and e.modifiers() != Qt.ControlModifier:
            sel_start = cursor.selectionStart()
            sel_end = cursor.selectionEnd()
            if sel_start != sel_end:
                for pos in range(sel_end, sel_start, -1):
                    patch = self.doc.delete(pos - 1)
                    self.change_evt.emit(patch)

            patch = self.doc.insert(sel_start, e.text())
            self.change_evt.emit(patch)

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

    COLORS = (
        (251, 222, 187),
        (187, 251, 222),
        (222, 251, 187),
        (222, 187, 251),
        (187, 222, 251)
    )

    NUM_COLORS = len(COLORS)

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
                    text_format.setBackground(QBrush(self.get_author_color(a), Qt.SolidPattern))

                    self.setFormat(block_pos, 1, text_format)

                    block_pos += 1
                elif doc_line > curr_line:
                    break

        self.setCurrentBlockState(self.previousBlockState() + 1)

    def get_author_color(self, author_site):
        return QColor(*self.COLORS[author_site % self.NUM_COLORS])


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
