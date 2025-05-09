from flask import Flask, request, render_template
import webbrowser
import threading
import os
import time
from dotenv import load_dotenv

load_dotenv()

def get_user_token():
    """

    Функция по получению access токена пользователя Twitch

    :return:
    """
    app = Flask(__name__)
    token_received = False

    @app.route('/')
    def index():
        """

        корневой путь с перенаправлением на сохранение токена

        :return: Шаблон страници со скриптом
        """
        return render_template('html_template.html')


    @app.route('/save')
    def save():
        """

        Сохранения токена т .txt файле

        :return:
        """
        nonlocal token_received
        token = request.args.get('token')
        with open("token.txt", "w") as f:
            f.write(token)
        token_received = True
        return ""

    # Запускаем сервер в отдельном потоке
    def run_server():
        """

        Функция запуска localhost

        :return:
        """

        app.run(port=3000)

    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Открываем браузер для авторизации
    webbrowser.open(
        f"https://id.twitch.tv/oauth2/authorize?"
        f"response_type=token&"
        f"client_id={os.getenv("CLIENT_ID_TWICH")}&"
        f"redirect_uri=http://localhost:3000&"
        f"scope=clips:edit&"
        f"force_verify=true"
    )

    # Ждем получения токена
    while not token_received:
        pass

    # Даем время на сохранение файла
    time.sleep(1)

if __name__ == '__main__':
    get_user_token()