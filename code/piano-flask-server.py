from flask import Flask
import threading

host_name = None
port = 8080
app = Flask(__name__)

@app.route('/')
def main():
    return 'Hello from Piano server'

if __name__ == '__main__':
    flask_thread = threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False))
    flask_thread.start()
    flask_thread.join()
