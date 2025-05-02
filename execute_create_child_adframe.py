import argparse
import sys
sys.path.append("./")

from adframe import child_frame
from config.driver_config import DriverConfig
from core.scraper import Scraper
from config.settings import Scrayping_Setting
from log import app_log
import execute_login


# 子枠作成
def main(is_test):
    logger = app_log.get_my_logger(__name__)
    logger.info("子枠の作成を開始しました。")

    setting = Scrayping_Setting(file_type="child", is_test=is_test)
    df = setting.df

    with DriverConfig() as driver:
        driver.get("https://admin.fam-8.net/report/index.php")
        scraper = Scraper(driver)

        # ログイン
        logger.info("ログインを開始しました。")
        execute_login.fam8_login(scraper)
        logger.info("ログインに成功しました。")

        # 子枠作成
        logger.info("子枠の作成を開始しました。")
        child_frame.create_new_adframe(scraper, "メディア", df)
        logger.info("子枠の作成に成功しました。")

        
    logger.info("子枠の作成を終了しました。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="子枠作成スクリプト")
    parser.add_argument(
        "--test", action="store_true", help="テストモードで実行する場合に指定"
    )
    args = parser.parse_args()

    main(is_test=args.test)
