from flask import Flask
import threading

app = Flask('')


@app.route('/')
def home():
    return "Бот работает!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    server = threading.Thread(target=run)
    server.start()
