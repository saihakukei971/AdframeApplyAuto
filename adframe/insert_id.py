import time
import pandas as pd
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from io import StringIO

from core.scraper import Scraper
from log import app_log
from core import micro_func


def insert_id(scraper: Scraper):
    """親枠と子枠に親枠IDを挿入する関数"""
    logger = app_log.get_my_logger(__name__)

    try:
        # ✅ `#tbl_data` の要素が表示されるまで最大 15 秒待つ
        WebDriverWait(scraper.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#tbl_data"))
        )

        # ✅ `#tbl_data` のHTMLを取得しログ出力
        table = scraper.find_element_by_css("#tbl_data")
        table_html = table.get_attribute("outerHTML")

        # ✅ `FutureWarning` 回避のため `StringIO` を使用
        time.sleep(0.5)
        df_multi_table = pd.read_html(StringIO(table_html), header=0)[0]

        # ✅ `広告枠名` のカラムがあるか確認
        if "広告枠名" not in df_multi_table.columns:
            logger.error("[ERROR] `広告枠名` カラムが見つかりません。処理を中断します。")
            raise Exception("Missing column: 広告枠名")

        # ✅ 広告枠名のフィルタリング
        target_pattern = r"^【F_】\S*"
        df_multi_table_trans = df_multi_table[
            df_multi_table["広告枠名"].str.match(target_pattern)
        ]
        logger.info(f"IDを挿入すべき広告枠を抽出: {len(df_multi_table_trans)}個")

        # df を繰り返して ID を挿入
        for index, row in df_multi_table_trans.iterrows():
            time.sleep(0.5)
            inputbox = scraper.find_element_by_css(
                "#main_area > form > div.where > input.txBox"
            )
            inputbox.clear()
            inputbox.send_keys(row["広告枠名"])

            scraper.find_element_by_css(
                "#main_area > form > div.where > input.btn"
            ).click()

            # ✅ 検索結果が表示されるまで待機
            WebDriverWait(scraper.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "table#tbl_data.tbl tr:nth-child(2) td:nth-child(3)")
                )
            )
            time.sleep(0.5)
            scraper.find_element_by_css(
                "table#tbl_data.tbl tr:nth-child(2) td:nth-child(3)"
            ).click()
            time.sleep(0.5)

            # ✅ 親枠名の再設定
            insert_frameid = str(row["広告枠ID"])
            parent_adframe_txbox = scraper.find_element_by_css(
                "table.tbl_input input.txBox"
            )
            insert_txbox(parent_adframe_txbox, insert_frameid)
            insert_id_in_child(scraper, insert_frameid)

            for i in range(3):
                try:
                    micro_func.button_click(
                        scraper, "div#input_area input[type='submit']", "value", "登録"
                    )
                    break
                except Exception:
                    logger.warning(f"ボタンのクリックに失敗しました。{i + 1}回目")
                    time.sleep(0.5)
                

            # ✅ アラート処理
            micro_func.alert_click(scraper, 0.5, "OK")
            micro_func.alert_click(scraper, 0.5, "OK")

            # ✅ クリアボタンを押す
            scraper.click_element_by_css("#main_area > form > div.where > input:nth-child(1)")

            # ✅ `#tbl_data` の再取得（ページリロード後の安定性向上）
            WebDriverWait(scraper.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#tbl_data"))
            )

    except TimeoutException as e:
        logger.error("[ERROR] `#tbl_data` のロードが確認できません。処理を中断します。")
        logger.exception("Timeout Exception:", exc_info=e)
        raise

    except NoSuchElementException as e:
        logger.error("[ERROR] 指定された要素が存在しません。")
        logger.exception("NoSuchElementException:", exc_info=e)
        raise


def insert_txbox(txbox, insert_item):
    """指定のテキストボックスの値を空にして、ID を入れた広告枠名を代入する関数"""
    logger = app_log.get_my_logger(__name__)

    val: str = txbox.get_attribute("value")
    txbox.clear()
    txbox.send_keys(val.replace("【F_】", f"【F_{insert_item}】").replace("【f_】", f"【f_{insert_item}】"))
    logger.info(f'テキストボックスに「{val.replace("【F_】", f"【F_{insert_item}】").replace("【f_】", f"【f_{insert_item}】")}」を入力。')


def insert_id_in_child(scraper: Scraper, insert_frameid):
    """子枠のID挿入処理"""
    logger = app_log.get_my_logger(__name__)
    try:
        child_table_rows_css = "#input_area > table > tbody > tr:nth-child(2) > td > form > table > tbody > tr:nth-child(4) > td > table > tbody > tr"
        WebDriverWait(scraper.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, child_table_rows_css))
        )
        child_table_rows = scraper.find_elements_by_css(child_table_rows_css)
        child_count = len(child_table_rows)

        for r in range(1, child_count):
            # 画面遷移のたびに要素がリセットされるため、再取得する
            child_table_rows = scraper.find_elements_by_css(child_table_rows_css)

            # 子枠編集ボタンをクリック
            for i in range(3):
                try:
                    scraper.find_element_by_css_in_element(
                        child_table_rows[r], "input[type='button']"
                    ).click()
                    break
                except Exception:
                    logger.warning(f"ボタンのクリックに失敗しました。{1 + i}回目")
                    time.sleep(0.5)

            scraper.driver.switch_to.window(scraper.driver.window_handles[-1])

            # `#main_area` のフォームが読み込まれるのを待つ
            WebDriverWait(scraper.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#main_area > div > form > table:nth-child(45) > tbody > tr")
                )
            )

            edit_rows = scraper.find_elements_by_css(
                "#main_area > div > form > table:nth-child(45) > tbody > tr"
            )

            for edit_row in edit_rows:
                if "広告枠名" in scraper.find_element_by_css_in_element(edit_row, "th").text:
                    edit_row_txbox = scraper.find_element_by_css_in_element(
                        edit_row, "input[type='text']"
                    )

                    insert_txbox(edit_row_txbox, insert_frameid)
                    micro_func.button_click(
                        scraper, "form p input.btn.btn_red", "value", "登録"
                    )

                    # ✅ アラート処理
                    micro_func.alert_click(scraper, 0.5, "OK")
                    time.sleep(0.5)

                    # ✅ 子ウィンドウを閉じる
                    scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
                    break

    except TimeoutException as e:
        logger.error("`insert_id_in_child` の処理中にタイムアウトが発生しました。")
        logger.exception("Timeout Exception:", exc_info=e)
        raise

    except NoSuchElementException as e:
        logger.error("指定された要素が見つかりませんでした。")
        logger.exception("NoSuchElementException:", exc_info=e)
        raise
