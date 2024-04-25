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

    URL = 'https://nuuuwan.github.io/lk_elections/'
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

        div_widget_list = driver.find_elements(
            By.XPATH, '//div[@id="lk-elections-widget"]'
        )
        n_div_widget_list = len(div_widget_list)
        log.debug(f'Found {n_div_widget_list} widgets.')
        if n_div_widget_list == 0:
            raise Exception('No widgets found')

        div_random = random.choice(div_widget_list)

        div_random.screenshot(image_path)
        log.debug(f'Screenshot saved to {image_path}')

        div_text_title = div_random.find_element(
            By.XPATH, './/div[@id="lk-elections-widget-text-title"]'
        )
        text_title = div_text_title.text
        log.debug(f'{text_title=}')
        
        div_text_body = div_random.find_element(
            By.XPATH, './/div[@id="lk-elections-widget-text-body"]'
        )
        text_body = div_text_body.text.replace('\n', '\n\n')
        log.debug(f'{text_body=}')

        text = '\n\n'.join([div_text_title.text, div_text_body.text])
        cleaned_text = clean(text)

        url_current = driver.current_url
        log.debug(f'{url_current=}')

        cleaned_text += '\n\n' + "See also " + url_current
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
