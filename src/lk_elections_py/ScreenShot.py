import json
import os
import tempfile
import time
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from twtr import Tweet, Twitter
from utils import Log

log = Log('ScreenShot')


@dataclass
class ScreenShot:
    text: str
    image_path: str

    URL = 'https://nuuuwan.github.io/lanka_elections/'
    T_SLEEP = 10
    WIDTH = 720
    HEIGHT = 720

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

        div_ss = driver.find_element(By.XPATH, '//div[@id="div-screenshot"]')
        div_ss.screenshot(image_path)
        log.debug(f'Screenshot saved to {image_path}')

        div_ss_text = driver.find_element(
            By.XPATH, '//div[@id="div-screenshot-text"]'
        )
        data_json = div_ss_text.text
        data = json.loads(data_json)
        log.debug(f'{data=}')

        url_current = driver.current_url
        log.debug(f'{url_current=}')
        driver.quit()

        os.startfile(image_path)
        election_year = data['electionYear']
        result = data['result']

        party_to_votes = result['partyToVotes']['partyToVotes']
        sorted_party_and_votes = sorted(
            party_to_votes.items(), key=lambda x: x[1], reverse=True
        )

        total_votes = sum(party_to_votes.values())
        result_lines = []
        p_votes_others = 0
        for party, votes in sorted_party_and_votes:
            p_votes = votes / total_votes
            if p_votes < 0.05:
                p_votes_others += p_votes
                continue
            result_lines.append(f'#{party} {p_votes:.0%}')

        if p_votes_others > 0:
            result_lines.append(f'Others {p_votes_others:.0%}')

        result_text = '\n'.join(result_lines)

        ent_pd = data['entPD']
        end_ed = data['entED']

        pd_name = ent_pd['name'].replace(' ', '')
        ed_name = end_ed['name'].replace(' ', '')

        text = f'''#PresPollSL{election_year}
#{pd_name} (#{ed_name})

{result_text}

{url_current}'''
        print(text)

        return ScreenShot(text, image_path)

    def tweet(self):
        try:
            twitter = Twitter()
            tweet = Tweet(self.text).add_image(self.image_path)
            tweet_id = twitter.send(tweet)
            log.debug(f'{tweet_id=}')
        except Exception as e:
            log.error('Could not tweet: ' + str(e))
