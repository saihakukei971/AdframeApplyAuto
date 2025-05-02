from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class DriverConfig(webdriver.Chrome):
    def __init__(
        self,
        default_dl_path: str = "",
        headless: bool = False,
    ):
        self.default_dl_path = default_dl_path
        self.options = self._setup_options(headless)

        super().__init__(
            options=self.options,
        )
        self.implicitly_wait(5)
        self.set_script_timeout(5)

    def _setup_options(self, headless: bool):
        options = Options()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("-incognito")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        if headless:
            options.add_argument("--headless")
        options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
        if self.default_dl_path != "":
            options.add_experimental_option(
                "prefs", {"download.default_directory": self.default_dl_path}
            )
        return options

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()
