from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from config.driver_config import DriverConfig


class Scraper:
    def __init__(self, driver: DriverConfig):
        self.driver = driver

    def get_page(self, url: str):
        self.driver.get(url)

    def find_element_by_css(self, css: str) -> WebElement:
        return self.driver.find_element(By.CSS_SELECTOR, css)

    def find_elements_by_css(
        self, css: str, allow_empty_list: bool = False
    ) -> list[WebElement]:
        elm_lists = self.driver.find_elements(By.CSS_SELECTOR, css)
        if len(elm_lists) > 0:
            return elm_lists
        else:
            if allow_empty_list:
                return elm_lists
            else:
                raise NoSuchElementException("要素が見つかりませんでした")

    def find_element_by_css_in_element(
        self, element: WebElement, css: str
    ) -> WebElement:
        return element.find_element(By.CSS_SELECTOR, css)

    def find_elements_by_css_in_element(
        self, element: WebElement, css: str
    ) -> list[WebElement]:
        return element.find_elements(By.CSS_SELECTOR, css)

    def find_element_by_css_wait_until(self, css: str, timeout: int = 30) -> WebElement:
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, css))
        )

    def click_element_by_element(self, element: WebElement):
        element.click()

    def click_element_by_css(self, css: str):
        self.find_element_by_css(css).click()

    def click_element_to_css_by_js(self, css: str):
        """JavaScriptで要素をクリックする"""
        element = self.find_element_by_css(css)
        self.driver.execute_script("arguments[0].click();", element)

    def send_keys_by_css(self, css, value: str):
        self.find_element_by_css(css).send_keys(value)

    def get_page_source(self) -> str:
        return self.driver.page_source

    def save_screenshot(self, file_name: str):
        self.driver.save_screenshot(file_name)

    def execute_script_by_css(self, css: str, script: str):
        element = self.find_element_by_css(css)
        self.driver.execute_script(script, element)

    def page_reload(self):
        self.driver.refresh()

    def get_log(self, log_type: str):
        return self.driver.get_log(log_type)

    def exists_element(self, css: str) -> bool:
        try:
            self.find_element_by_css(css)
            return True

        except NoSuchElementException:
            return False

    def select_by_visible_text(self, css: str, text: str):
        """指定されたテキストに一致するオプションを選択する"""
        element = self.find_element_by_css(css)
        select = Select(element)
        select.select_by_visible_text(text)

    def select_by_value(self, css: str, val: str):
        """指定されたvalueに一致するオプションを選択する"""
        element = self.find_element_by_css(css)
        select = Select(element)
        select.select_by_value(val)

    def alert_click_to_accept(self):
        alert = self.driver.switch_to.alert
        alert.accept()

    def alert_click_to_dismiss(self):
        alert = self.driver.switch_to.alert
        alert.dismiss()
