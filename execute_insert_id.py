import argparse
import sys
sys.path.append("./")
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from adframe import insert_id
from config.driver_config import DriverConfig
from core.scraper import Scraper
from log import app_log
import execute_login

# ✅ 「複数原稿配信タイプ」のボタンをクリックする関数
def click_multiple_adframe_type(scraper):
    """
    「複数原稿配信タイプ」のボタンをクリックする。
    """
    try:
        side_menu_button = WebDriverWait(scraper.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="sidemenu"]/div[3]/a[6]/div'))
        )
        side_menu_button.click()

        WebDriverWait(scraper.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#tbl_data"))
        )

    except TimeoutException:
        logger = app_log.get_my_logger(__name__)
        logger.error("[ERROR] 「複数原稿配信タイプ」のメニューが見つからなかった。処理を中断します。")
        raise

# ✅ 広告枠IDの挿入処理
def execute_insert(is_test: bool):
    # ✅ `logger` を関数内で取得
    logger = app_log.get_my_logger(__name__)
    logger.info("IDの挿入を開始しました。")

    with DriverConfig() as driver:
        driver.get("https://admin.fam-8.net/report/index.php")
        scraper = Scraper(driver)

        # ✅ ログイン処理
        logger.info("ログインを開始しました。")
        execute_login.fam8_login(scraper)
        logger.info("ログインに成功しました。")

        # ✅ 「複数原稿配信タイプ」ページに遷移
        click_multiple_adframe_type(scraper)

        # ✅ `#tbl_data` の取得を保証
        try:
            WebDriverWait(scraper.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#tbl_data"))
            )
        except TimeoutException:
            logger.error("[ERROR] #tbl_data のロードが確認できません。処理を中断します。")
            raise

        if not is_test:
            # ✅ ID挿入処理
            insert_id.insert_id(scraper)
    
    logger.info("IDの挿入に成功しました。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ID挿入用スクリプト")
    parser.add_argument(
        "--test", action="store_true", help="テストモードで実行する場合に指定"
    )
    args = parser.parse_args()

    execute_insert(is_test=args.test)
