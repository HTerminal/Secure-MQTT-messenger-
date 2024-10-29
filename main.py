import sys
import paho.mqtt.client as mqtt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QTextEdit, QPushButton
from PyQt5.QtCore import Qt, QDateTime


class MessengerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.send_topic = ""
        self.receive_topic = ""
        self.encryption_key = b"ThisIsASecretKey123ThisIsASecret"
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        self.setWindowTitle("Messenger")
        self.setGeometry(100, 100, 400, 300)

        self.send_topic_label = QLabel("Send Topic:", self)
        self.send_topic_label.setGeometry(20, 20, 80, 20)

        self.send_topic_input = QLineEdit(self)
        self.send_topic_input.setGeometry(110, 20, 200, 20)

        self.receive_topic_label = QLabel("Receive Topic:", self)
        self.receive_topic_label.setGeometry(20, 60, 80, 20)

        self.receive_topic_input = QLineEdit(self)
        self.receive_topic_input.setGeometry(110, 60, 200, 20)

        self.connect_button = QPushButton("Connect", self)
        self.connect_button.setGeometry(320, 20, 60, 60)
        self.connect_button.clicked.connect(self.connect_mqtt)

        self.message_label = QLabel("Message:", self)
        self.message_label.setGeometry(20, 100, 60, 20)

        self.message_input = QLineEdit(self)
        self.message_input.setGeometry(80, 100, 200, 20)

        self.send_button = QPushButton("Send", self)
        self.send_button.setGeometry(300, 100, 80, 20)
        self.send_button.clicked.connect(self.send_message)

        self.chat_log = QTextEdit(self)
        self.chat_log.setGeometry(20, 140, 360, 120)
        self.chat_log.setReadOnly(True)

    def connect_mqtt(self):
        self.send_topic = self.send_topic_input.text()
        self.receive_topic = self.receive_topic_input.text()
        self.mqtt_client.connect("broker.hivemq.com", 1883, 60)
        self.mqtt_client.loop_start()
        self.mqtt_client.subscribe(self.receive_topic)
        self.send_topic_input.setEnabled(False)
        self.receive_topic_input.setEnabled(False)
        self.connect_button.setEnabled(False)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT broker")
        else:
            print("Failed to connect to MQTT broker")

    def on_message(self, client, userdata, msg):
        ciphertext = msg.payload
        try:
            plaintext = self.decrypt_message(ciphertext, self.encryption_key)
            timestamp = QDateTime.currentDateTime().toString(Qt.ISODate)
            message = f"[{timestamp}] {plaintext}"
            self.chat_log.append(message)
        except ValueError:
            timestamp = QDateTime.currentDateTime().toString(Qt.ISODate)
            error_message = f"[{timestamp}] Error: Unsupported message received"
            self.chat_log.append(error_message)

    def encrypt_message(self, message, key):
        cipher = AES.new(key, AES.MODE_ECB)
        padded_message = pad(message.encode(), AES.block_size)
        encrypted_message = cipher.encrypt(padded_message)
        return encrypted_message

    def decrypt_message(self, ciphertext, key):
        cipher = AES.new(key, AES.MODE_ECB)
        padded_plaintext = cipher.decrypt(ciphertext)
        plaintext = unpad(padded_plaintext, AES.block_size)
        return plaintext.decode()

    def send_message(self):
        message = self.message_input.text()
        encrypted_message = self.encrypt_message(message, self.encryption_key)
        self.mqtt_client.publish(self.send_topic, encrypted_message)
        self.message_input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MessengerWindow()
    window.show()
    sys.exit(app.exec_())
