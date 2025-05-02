import argparse
import sys
sys.path.append("./")

from config.driver_config import DriverConfig
from core.scraper import Scraper
from config.settings import Scrayping_Setting
from adframe import child_frame_multi, insert_id, parents_frame
from log import app_log
import execute_login

# ハイブリット枠作成
def main(is_test):
    logger = app_log.get_my_logger(__name__)
    logger.info("ハイブリット枠の作成を開始しました。")

    setting = Scrayping_Setting(file_type="multi", is_test=is_test)
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
        child_frame_multi.create_new_adframe(scraper, "メディア", df)
        logger.info("子枠の作成に成功しました。")

        # 親枠作成
        logger.info("親枠の作成を開始しました。")
        parents_frame.apply_new_adframe(scraper, "複数原稿配信タイプ", df)
        logger.info("親枠の作成に成功しました。")

        # クリアボタンを押す
        try:
            scraper.click_element_by_css("#main_area > form > div.where > input:nth-child(1)")
        except Exception:
            pass

        # IDを記入
        logger.info("IDの挿入を開始しました。")
        insert_id.insert_id(scraper)
        logger.info("IDの挿入に成功しました。")

        logger = app_log.get_my_logger(__name__)
        logger.info("ハイブリット枠の作成に成功しました。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ハイブリット枠作成スクリプト")
    parser.add_argument("--test", action="store_true", help="テストモードで実行する場合に指定")
    args = parser.parse_args()

    main(is_test=args.test)
