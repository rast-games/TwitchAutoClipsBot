import os.path
import time
from selenium import webdriver
import pickle
from http.cookiejar import Cookie
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class NetError(WebDriverException):
    pass


def refresh_cookies(driver, url):

    wait = WebDriverWait(driver, 3)


    try:
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'neterror')))
        raise NetError
    except TimeoutException:
        pass
    except WebDriverException:
        raise NetError


    time.sleep(2)
    try:
        with open('cookies.pkl', 'rb') as f:
            cookies = pickle.load(f)
        for cookie in cookies:
            # Конвертируем объект Cookie в словарь
            cookie_dict = {
                'name': cookie.name,
                'value': cookie.value,
                'domain': cookie.domain,
                'path': cookie.path,
                'secure': cookie.secure
            }

            # Добавляем expiry если есть
            if cookie.expires:
                cookie_dict['expiry'] = int(cookie.expires)

            # Удаляем лишние поля
            for field in ['httpOnly', 'sameSite', 'rest']:
                cookie_dict.pop(field, None)

            try:
                driver.add_cookie(cookie_dict)
            except Exception as e:
                print(f"Ошибка добавления cookie {cookie.name}: {str(e)}")
        driver.refresh()
        time.sleep(1)
    except Exception as e:
        print("ошибка работы с cookie ", str(e))


def load_cookies():

    have_error = True # Переменная отвечающая за ожиданиеинициализации без ошибок

    while have_error:
        options = webdriver.ChromeOptions()
        CensorTracker = os.path.abspath('PATH/censor tracker custom')
        options.add_argument(f'load-extension={CensorTracker}')
        options.add_argument("--mute-audio")
        # options.add_argument('--headless') # безголовый режим пока в разработке

        # Запускаем драйвер
        driver = webdriver.Chrome(options=options)
        time.sleep(2)

        time.sleep(2)  # Даем время на инициализацию

        lag_urls = ["https://www.tiktok.com/login"] # urls с которыми могут возникнуть сетевые ошибки

        urls = ["https://www.youtube.com/", 'https://www.twitch.tv'] # стабильные urls


        try:
            for url in lag_urls + urls:
                refresh_cookies(driver, url)
            have_error = False
        except NetError:
            print("ошибка сети")
            driver.quit()
            continue
        except Exception as e:
            print("Ошибка: ", str(e))
            return str(e)


    print("куки успешно подгружены")
    return driver



if __name__ == '__main__':
    load_cookies()


