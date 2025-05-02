import time

from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.scraper import Scraper


def click_sidemenu(scraper: Scraper, SEARCH_SIDEMENU4_STRING: str):
    side_menu = scraper.find_elements_by_css(
        "div.tbl > a.a_noline > div.sidemenu4.sidemenu4_off"
    )
    for link in side_menu:
        if link.text == SEARCH_SIDEMENU4_STRING:
            link.click()
            break
    time.sleep(0.5)


def click_sidemenu_for_js(scraper: Scraper, SEARCH_SIDEMENU4_STRING):
    side_menu = scraper.find_elements_by_css(
        "div.tbl > a.a_noline > div.sidemenu4.sidemenu4_off"
    )
    for link in side_menu:
        if link.text == SEARCH_SIDEMENU4_STRING:
            scraper.driver.execute_script("arguments[0].click();", link)
            break
    time.sleep(0.5)


def search_format_create(
    scraper: Scraper, item_option: str, type_option: str, search_word: str
):
    """
    検索項目、検索方法、入力値を設定し検索ボタンを押す関数

    Parameter
    ----------
    scraper : object
        現在操作しているWebページのドライバー

    item_option : string
        メディアIDや広告枠名

    type_option : string
        検索方法("が次に等しい"→"1" "が次をすべて含む"→"2" "が次のどれかを含む"→"3" "が次を含まない"→"5")

    search_word : string
        検索ボックスの値
    """

    scraper.select_by_visible_text("select[name='search_col0']", item_option)
    scraper.select_by_value("select[name='search_type0']", type_option)

    search_text = scraper.find_element_by_css("input[name='search_text0']")

    if search_text.get_attribute("value") == "":
        search_text.send_keys(search_word)
    else:
        search_text.clear()
        search_text.send_keys(search_word)

    time.sleep(0.5)

    scraper.click_element_by_css("div.where > input.btn")


def status_select_on(scraper: Scraper):
    """広告枠ページ内でステータスをオンにする関数"""
    scraper.select_by_visible_text(
        "#main_area > form > div.where > table:nth-child(16) > tbody > tr:nth-child(1) > td > select:nth-child(2)",
        "オン",
    )


def button_click(scraper: Scraper, css: str, attribute: str, find_value: str):
    """Valueの値から判断してボタンをクリックする関数
    css : css_selector
    attribute : get_attributeの属性
    find_value : 検索したいワード
    """
    time.sleep(0.5)
    for btn in scraper.find_elements_by_css(css):
        if btn.get_attribute(attribute) == find_value:
            btn.click()
            break
    time.sleep(0.5)


def alert_click(scraper: Scraper, sleep_time, ok_or_cancel, count=0):
    """アラートをクリックする関数"""
    time.sleep(sleep_time)
    try:
        if count == 5:
            raise Exception

        wait = WebDriverWait(scraper.driver, 30)
        wait.until(EC.alert_is_present())

        if ok_or_cancel == "OK":
            scraper.alert_click_to_accept()
        else:
            scraper.alert_click_to_dismiss()

    except UnexpectedAlertPresentException:
        alert_click(scraper, sleep_time, ok_or_cancel, count + 1)

    except TimeoutException:
        pass

    time.sleep(sleep_time)


def choice_btn_click(scraper: Scraper, find_text: str):
    """テーブル内に複数同名ボタンがあるとき、trの文字列から判断したボタンを押す関数"""
    for tr in scraper.find_elements_by_css("table.tbl_input tr"):
        th = scraper.find_element_by_css_in_element(tr, "th")
        if th.text == find_text:
            btn = scraper.find_element_by_css_in_element(tr, "input.btn")
            btn.click()
            break
    time.sleep(0.5)


def click_media_link(scraper: Scraper):
    """メディア選択をして、メディア名をクリックする関数"""
    media_name_link = scraper.find_element_by_css("a.a_list")
    scraper.click_element_by_element(media_name_link)
    time.sleep(0.5)
