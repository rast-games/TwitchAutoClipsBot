import os
import time
from dotenv import load_dotenv
import nodriver as uc
from get_cookes import get_cookes
from load_cookies import load_cookies
from get_user_token import get_user_token
import requests
import configparser
from shorts_maker import convert_to_tiktok_and_YtShorts
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains


def wait_and_click(driver, wait_for_xpath, timeout=20):

    """

    Функция ожидающая элемент и кликающая на него впоследствии

    :param driver: драйвер который будет нажимать
    :param wait_for_xpath: XPATH до элемента
    :param timeout: таймаут ожидания
    :return:

    """

    element_locator = EC.presence_of_element_located((By.XPATH, wait_for_xpath))
    WebDriverWait(driver, timeout).until(element_locator)
    driver.find_element(By.XPATH, wait_for_xpath).click()


def reload_driver(driver):
    """

    Функция для переинициализации драйвера вручную пользователем

    :param driver: драйвер
    :return: переинициализирований драйвер

    """
    if os.path.exists("cookies.pkl"): # Удаление текущих куков если они существуют
        os.remove("cookies.pkl")
    driver.quit() # Отключение текущего драйвера
    time.sleep(1)
    uc.loop().run_until_complete(get_cookes()) # Получение новых куков
    time.sleep(1)
    driver = load_cookies() # Инициализация нового драйвера
    return driver

# def text_in_element(locator: tuple, texts: tuple):
#     def wrap(driver):
#         elem = driver.find_element(*locator)  # Поиск актуального элемента
#         return any(text in elem.text for text in texts)
#     return wrap

def upload_to_tiktok(driver, title, video_path, username):
    """

        Функция по автоматической публикации кливов в ТТ

        :param driver: Проинициализирований драйвер
        :param title: Название видео
        :param video_path: Путь к видео
        :param username: Ник стримера
        :return:

        """

    try:
        wait = WebDriverWait(driver, 3)

        print("[1] Начало загрузки видео в тт")

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Файл {video_path} не найден")
        print("[2] Файл видео существует")

        print("[3] Открываю TikTok Studio")

        driver.get("https://www.tiktok.com/creator-center/upload")


        # Загрузка файла
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        ).send_keys(os.path.abspath(video_path))

        # Ожидание инициализации редактора
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class, 'public-DraftStyleDefault-block')]"))
        )

        desc_editor = driver.find_element(
            By.XPATH,
            "//div[contains(@class, 'DraftEditor-editorContainer')]"
        )

        desc_editor.click()

        ActionChains(driver).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE).pause(1).perform()

        ActionChains(driver).send_keys(f"Стрим LIVE! Твич: {username}").perform()


        # Работа с Shadow DOM
        try:
            # 1. Дождаться появления хоста
            host = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.TAG_NAME, "tiktok-cookie-banner"))
            )

            # 2. Получить доступ к Shadow DOM
            shadow_root = driver.execute_script("return arguments[0].shadowRoot", host)

            # 3. Найти кнопку через CSS-селектор (второй button в контейнере)
            accept_button = WebDriverWait(shadow_root, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div.button-wrapper > button:last-child")
                )
            )

            # 4. Кликнуть
            accept_button.click()
            print("✅ Куки приняты!")

        except TimeoutException:
            print(f"❌Куки либо уже приняты, либо произошла какая либо ошибка")

        progress_bar = driver.find_element(
            By.CSS_SELECTOR,
            "div.jsx-1979214919:nth-child(3)"
        )

        style = progress_bar.get_attribute("style")
        width = style.split("width:")[1].split("%")[0].strip()

        while width != '100':
            style = progress_bar.get_attribute("style")
            width = style.split("width:")[1].split("%")[0].strip()

        print("[4] Загрузка видео в тт выполнена")





        # Дополнительные действия для сохранения
        driver.find_element(By.CSS_SELECTOR, '.button-group > button:nth-child(1)').click()
        print("[5] Публикация успешно завершена!")

    except Exception as e:
        print(f"Ошибка: {str(e)}")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)




def upload_youtube(driver, title, video_path, username):
    """

    Функция по автоматической публикации кливов в ЮТ

    :param driver: Проинициализирований драйвер
    :param title: Название видео
    :param video_path: Путь к видео
    :param username: Ник стримера
    :return:

    """



    try:
        print("[1] Начало загрузки видео в ют")



        if not os.path.exists(video_path): # Проверка существования файла
            raise FileNotFoundError(f"Файл {video_path} не найден")

        print("[2] Файл видео существует")

        # Конвертируем видео (если нужно)
        new_path = convert_to_tiktok_and_YtShorts(video_path)  # Путь к адаптированому видео
        os.remove(video_path)  # Удаление старого видео
        video_path = new_path  # Присваивание нового пути в качестве стандартного




        wait = WebDriverWait(driver, 3)
        print("[3] Открываю YouTube Studio")


        # Открываем студию YouTube
        driver.get("https://studio.youtube.com")

        source = driver.page_source # Получение HTML кода страници при переходе в студию
        while "Вход" in source: # Проверка на предмет детекта бота гуглом, и переинициализация драйвера в противном случае
            driver = reload_driver(driver)
            driver.get("https://studio.youtube.com")
            wait = WebDriverWait(driver, 3)
            source = driver.page_source

        print("[4] Авторизация...")

        # Кликаем кнопку загрузки
        # Проверка на наличие кнопки загрузки в главном меню, и использование отдельных кнопок в противном случае
        try:
            wait_and_click(driver, '//*[@id="upload-button"]', 3)
        except:
            wait_and_click(driver, '/html/body/ytcp-app/ytcp-entity-page/div/ytcp-header/header/div/div/ytcp-button/ytcp-button-shape/button/yt-touch-feedback-shape/div', 5)
            wait_and_click(driver, '/html/body/ytcp-text-menu/tp-yt-paper-dialog/div/tp-yt-paper-listbox/tp-yt-paper-item[1]/ytcp-ve/tp-yt-paper-item-body/div/div/div/yt-formatted-string', 5)

        print("[5] Авторизация успешна")


        # Загружаем файл
        print("[6] Ищу кнопку загрузки")



        file_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type=file]")) # Передача файла ЮТ
        )

        try: # Проверка на обнаружение автоманизации гуглом, и переинициализация дравера и рекурсивный вызов функции в противном случае
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#dialog-title")))
            driver = reload_driver(driver)
            upload_youtube(driver, title, video_path, username)
            return None

        except TimeoutException:
            pass


        print("[7] Кнопка загрузки найдена")
        file_input.send_keys(os.path.abspath(video_path))
        print("[8] Загружаю файл")
        print("[9] Файл отправлен")


        try:  # Ожидание ошибки превышения лимита загрузки в день, и продолжение в противном случае

            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.error-short')))
            print("[10] Ошибока, вам не доступна возможность выкладывать видео")

            try:
                now_max = config.get("Settings", "max_iterations")

                now_it = config.get("Settings", "iteration")

                config.set("Settings", "max_iterations", now_max if now_max > now_it else now_it)

            except:
                config.set("Settings", "max_iterations", config.get("Settings", "iteration"))

            finally:
                global flag

                flag = False
                # print(flag)
                global additionally_loop
                additionally_loop = True
                # print(additionally_loop)

                with open("config.ini", "w") as configfile:
                    config.write(configfile)

                return None
        except TimeoutException:
            print("[10] Ошибок загрузки не обнаружено")

        print("[11] Заполнение описания, названия и т.д")


        # Заполняем название
        title_field = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@id="textbox"]'))
        )

        title_field.clear()
        title_field.send_keys(title)

        # Заполняем описание
        desc_field = driver.find_element(
            By.XPATH, '//div[@id="textbox"][contains(@aria-label, "Расскажите, о чем ваше видео.")]'
        )
        desc_field.clear()
        desc_field.send_keys(f"Стрим LIVE! Твич: {username}")


        # Кнопки необходимые для публикации видео
        buttons = ['//*[contains(text(), "Нет, это видео не для детей")]',
                   *['//*[@id="next-button"]/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]' for _ in range(3)],
                   '//div[contains(text(), "Открытый доступ")]',
                   '//*[@id="done-button"]/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]'
                   ]

        # Их нажатие
        [wait_and_click(driver, buttons[i]) for i in range(len(buttons))]


        # while not set(indicator.text.split()) & set(("Обработка в HD…","Загрузка видео завершена.")):
        #     time.sleep(1)
            # print(page_source_yt)

        page_source_yt = driver.page_source # Получение HTML кода страници

        # Ожидание появление какой либо надписи гарантирующей загрузку видео
        while not ("Обработка в HD…" in page_source_yt or "Загрузка видео завершена." in page_source_yt):
            # Проверка наличия одной из фраз
            page_source_yt = driver.page_source


            # try:
            #     # Ожидаем появление любой из двух фраз
            #     wait.until(text_in_element((By.CLASS_NAME, 'progress-label'), ("Обработка в HD…", "Загрузка видео завершена.")))
            #     wait_for_load = False
            # except TimeoutException:
            #     pass


        print("Загрузка начата успешно!")

    except Exception as e:
        print(f"Ошибка загрузки: {str(e)}")
        # driver.save_screenshot('error.png')

    finally:
        os.remove(video_path) if os.path.exists(video_path) else None
        if config.read('config.ini') == []:
            config.add_section('Settings')
            config.set('Settings', 'iteration', '1')

        elif config.get('Settings', 'iteration') == '0':
            config.set('Settings', 'iteration', '1')

        else:
            iter = setting = config.get('Settings', 'iteration')
            config.set('Settings', 'iteration', f'{int(iter) + 1}')
        with open('config.ini', 'w') as config_file:
            config.write(config_file)




def save_clips(link):
    """

    Функция сохранения клипа по прямой ссылке

    :param link: Прямая ссылка на видео
    :return: Путь к сохраненому видео

    """
    filename = link.split('/')[-1]
    response = requests.get(link)
    print("создание файла")
    with open(f"cache/{filename}", 'wb') as f:
        f.write(response.content)
    return f"cache/{filename}"


def get_clips_wrap(driver, username, count=20):
    '''
        Оберточная функция, по получению клипов

        :param driver проинициализированый драйвер
        :param username никнейм стримера
        :param count кол во клипов

        '''

    url = "https://api.twitch.tv/helix/clips" # API Twitch по получению ссылки на созданный клип
    if not os.path.isfile("token.txt"): # Проверка на существование access токена, и его получение в противном случае
        get_user_token()
    with (open("token.txt", "r") as f): # Чтение access токена
        token = f.read()
        headers = { # Заполнение заголовков будующих запросов
            'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {token}'
        }

        response = requests.get(f'https://api.twitch.tv/helix/users?login={username}', headers=headers) # Получение ID стримера с помощью API

        data = response.json()
        if len(data['data']) < 1:
            print('Канал не существует, либо нет воэможности получить id')
            return None


        # ID стримера

        broadcaster_id = data['data'][0]['id'] # ID стримера

        params = {"broadcaster_id": broadcaster_id} # Параметры будующих запросов

    for _ in range(count): # Создание цикла, который будет повтораться count раз

        rand_word = requests.get('https://random-word-api.herokuapp.com/word') # Получение случайного слова для заголовка клипа
        title = rand_word.json()[0]
        # print(rand_word.json()[0])

        response = requests.post(url, headers=headers, params=params) # Обращение к API Twitch для получения ссылки на созданный клип
        data_response = response.json()
        # print(data_response)
        if "message" in data_response: # Проверка на наличие сообщения об ошибке в ответе, в противном случае прекращение работы
            print(data_response['message'])
            break
        try:
            wait = WebDriverWait(driver, 10)
            url_clip = response.json()["data"][0]["edit_url"] # Извлечение ссылки на сам клип
            driver.get(url_clip) # Переход по ссылке
            title_form = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#cmgr-title-input')) # Ожидание поля для заголовка
            )
            title_form.send_keys(title) # Ввод заголовка

            wait_and_click(driver,'//*[@id="root"]/div/div[1]/div/div[3]/div/div/main/div/div[3]/div/div[2]/div[2]/div/div[2]/div[2]/div/div/div/button') # Ожидание и клик по кнопке "Опубликовать"

            video = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, 'video')) # Ожидание прямой ссылки на клип
            )
            link = video.get_attribute('src') # Извлечение прямой ссылки на клип
            # print(link)

            if os.path.exists("config.ini"):
                config.read('config.ini')
                iter_yt = int(config.get("Settings", "iteration"))
                try:
                    max_iterations = int(config.get("Settings", "max_iterations"))
                except configparser.NoOptionError:
                    max_iterations = "unknown"
            else:
                iter_yt = 0
                max_iterations = "unknown"

            if (max_iterations == "unknown" or iter_yt <= max_iterations) and flag:
                upload_youtube(driver, title, save_clips(link), username=username)
            else:
                upload_to_tiktok(driver, title, save_clips(link), username=username)




        except Exception as e:
            print(f'ошибка: {str(e)}')



def get_clips(driver, username, count=20):
    '''
    Основная функция, по получению клипов

    :param driver проинициализированый драйвер
    :param username никнейм стримера
    :param count кол во клипов

    '''
    # Вызов внутренней функции для того чтобы иметь возможность пройти доп. круг при возникновении ошибки
    get_clips_wrap(driver, username, count)

    if additionally_loop: # Дополнительный круг при необходимости
        get_clips_wrap(driver, username, 1)






def main():

    '''Входная функция'''

    # Инициализация

    load_dotenv()
    global CLIENT_ID
    global flag
    global additionally_loop
    global config

    CLIENT_ID = os.getenv("CLIENT_ID_TWICH")
    config = configparser.ConfigParser()
    if os.path.exists("config.ini"):
        config.read('config.ini')
    flag = True
    additionally_loop = False

    print("V 1.0")

    # Получение задания от пользователя

    try:
        user_streemer = input("Введите ник стримера: ") # Получаем от пользователя ник стримера
        count = input("Введите количество клипов:") # Получаем от пользователя понимание того, сколько клипов надо сделать

        while not count.isdigit(): # Проверка на целочисленность
            print("количество клипов должно быть целочисленным числом")
            count = input("Введите количество клипов:")


        if not os.path.isfile("cookies.pkl"): # Проверка на предмет существования сохраненных куков, и их получение в противном случае
            uc.loop().run_until_complete(get_cookes())
        driver = load_cookies() # Инициализация драйвера внутри функции load_cookies
        if driver is None:
            print("Cookies не загружены")
            return None
        get_clips(driver, count=int(count), username=user_streemer)

        try: # Система сохранения номера итерации в файле config.ini
            config.add_section('Settings')
        except configparser.DuplicateSectionError:
            pass
        finally:
            config.set('Settings', 'iteration', '0')
        with open('config.ini', 'w') as config_file:
            config.write(config_file)
    except KeyboardInterrupt:
        print("Программа завершена принудительно")





if __name__ == "__main__":
    main()

