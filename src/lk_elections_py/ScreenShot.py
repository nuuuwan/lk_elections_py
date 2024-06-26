import random
import tempfile
import time
from dataclasses import dataclass
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from twtr import Tweet, Twitter
from utils import Log

log = Log('ScreenShot')


def clean(x):
    while '  ' in x:
        x = x.replace('  ', ' ')
    x = x.strip()
    if len(x) > 250:
        x = x[:250] + '...'
    return x


@dataclass
class ScreenShot:
    text: str
    image_path: str

    URL = 'https://nuuuwan.github.io/lk_elections?pageID=random'
    T_SLEEP = 20
    WIDTH = 2000
    HEIGHT = 2000

    @staticmethod
    def random():
        # headless
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')

        options.add_argument(f'--width={ScreenShot.WIDTH}')
        options.add_argument(f'--height={ScreenShot.HEIGHT}')

        driver = webdriver.Firefox(options=options)
        driver.get(ScreenShot.URL)

        log.debug(f'Opened {ScreenShot.URL}...')
        image_path = tempfile.mktemp('.png')

        log.debug(f'😴 Sleeping for {ScreenShot.T_SLEEP}s...')
        time.sleep(ScreenShot.T_SLEEP)

        elem_widget_list = driver.find_elements(
            By.XPATH, '//*[@id="lk-elections-widget"]'
        )
        n_elem_widget_list = len(elem_widget_list)
        log.debug(f'Found {n_elem_widget_list} widgets.')
        if n_elem_widget_list == 0:
            raise Exception('No widgets found')

        elem_random = random.choice(elem_widget_list)

        elem_random.screenshot(image_path)
        log.debug(f'Screenshot saved to {image_path}')

        elem_text_title = elem_random.find_element(
            By.XPATH, './/*[@id="lk-elections-widget-text-title"]'
        )
        text_title = elem_text_title.text
        log.debug(f'{text_title=}')
        
        elem_text_body = elem_random.find_element(
            By.XPATH, './/*[@id="lk-elections-widget-text-body"]'
        )
        text_body = elem_text_body.text.replace('\n', '\n\n')
        log.debug(f'{text_body=}')

        text = '\n\n'.join([elem_text_title.text, elem_text_body.text])
        cleaned_text = clean(text)

        url_current = driver.current_url
        log.debug(f'{url_current=}')

        cleaned_text += '\n\n' + url_current
        print(cleaned_text)
        log.debug(f'len(cleaned_text) = {len(cleaned_text)}')

        driver.quit()

        return ScreenShot(cleaned_text, image_path)

    def tweet(self):
        try:
            twitter = Twitter()
            tweet = Tweet(self.text).add_image(self.image_path)
            tweet_id = twitter.send(tweet)
            log.debug(f'{tweet_id=}')
        except Exception as e:
            log.error('Could not tweet: ' + str(e))
