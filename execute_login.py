from core.scraper import Scraper
from selenium.webdriver.common.by import By

def fam8_login(scraper: Scraper):
    """
    fam8にログインするための関数

    Parameter
    ----------
    scraper : DrierConfig
        現在操作しているWebページのドライバー
    """

    #ログイン情報
    ID = 'admin'
    PASSWORD = 'fhC7UPJiforgKTJ8'

    # ユーザーID入力
    element = scraper.driver.find_element(By.XPATH, '//*[@id="topmenu"]/tbody/tr[2]/td/div[1]/form/div/table/tbody/tr[1]/td/input')
    element.clear()
    element.send_keys(ID)
    
    # パスワード入力
    element = scraper.driver.find_element(By.XPATH, '//*[@id="topmenu"]/tbody/tr[2]/td/div[1]/form/div/table/tbody/tr[2]/td/input')
    element.clear()
    element.send_keys(PASSWORD)
    
    # ログインボタンをクリック
    scraper.driver.find_element(By.XPATH, '//*[@id="topmenu"]/tbody/tr[2]/td/div[1]/form/div/table/tbody/tr[3]/td/input[2]').click()