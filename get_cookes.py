import asyncio
import nodriver as uc
import time
import json
import pickle
import os

async def get_content(browser, url, searching_title, return_page=False):

    """

    Функция для ожидания смены названия страницы

    :param browser: Проинициализированый браузер
    :param url: url страницы
    :param searching_title: ожидаемое название
    :param return_page: Булевое значение для указания возврата страницы, по умолчанию False
    :return: page при указании параметра return_page

    """

    page = await browser.get(url=url, new_tab=True)
    await asyncio.sleep(7)
    content = await page.get_content()
    while f"<title>{searching_title}</title>" in content:
        await asyncio.sleep(2)
        content = await page.get_content()
    return page if return_page else None


async def get_cookes():
    """

    Функция по получение куков с помощью библиотеки NODRIVER

    :return:

    """

    # Адреса сайтов получаемых куков
    youtube_url = "https://accounts.google.com"
    twitch_url = "https://www.twitch.tv/login"
    tiktok_url = "https://www.tiktok.com/login"


    CensorTracker = os.path.abspath('PATH/censor tracker custom') # Подключение кастомного расширения

    browser = await uc.start( # Инициализация браузера
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-web-security",
            f'load-extension={CensorTracker}'
        ]
    )

    await asyncio.sleep(2)

    # Переход к кажому сайту и получение куков, и возврат страницы в конце
    await get_content(browser, youtube_url, searching_title='Вход&nbsp;– Google Аккаунты')
    await get_content(browser, twitch_url, searching_title='Войти - Twitch')
    page = await get_content(browser, tiktok_url, searching_title='Войти | TikTok', return_page=True)


    # Запись куков в переменную
    cookies = await page.send(
        uc.cdp.network.get_all_cookies()
    )

    # print("куки")
    # print(cookies)

    # Сохранение куков
    with open('cookies.pkl', 'wb') as f:
        pickle.dump(cookies, f)
    browser.stop()




async def main():

    await get_cookes()


if __name__ == '__main__':
    uc.loop().run_until_complete(main())

