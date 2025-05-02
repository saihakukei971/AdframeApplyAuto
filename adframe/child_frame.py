import re
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchWindowException

from core import micro_func
from core.scraper import Scraper
from log import app_log
from created_frames import created_frames

# 新規一般子枠用
def create_new_adframe(scraper: Scraper, side_menu, df):
    logger = app_log.get_my_logger(__name__)
    previous = ""
    for cnt_row in range(len(df)):
        if (created_frames.check_created_frames([df.at[cnt_row, "登録広告枠名"]], "child")):
            logger.info(f"既に子枠が作成された記録があるためスキップしました。: {df.at[cnt_row, '登録対象メディアID']}")
            continue

        logger.info(f"「{df.at[cnt_row, '登録広告枠名']}」の登録を開始します。")

        # CSVデータの最初の行の実行時、または前の行と今の行で参照先メディアIDが違う場合、以下を実行する
        csv_row = df.loc[cnt_row]
        if cnt_row != 0:
            prev_csv_row = df.loc[cnt_row - 1]
        else:
            prev_csv_row = 0

        if cnt_row == 0 or csv_row["参照メディアID"] != prev_csv_row["参照メディアID"] or previous == "":
            micro_func.click_sidemenu(scraper, side_menu)

            micro_func.search_format_create(
                scraper, "メディアID", "1", str(csv_row["参照メディアID"])
            )

            micro_func.click_media_link(scraper)
            micro_func.status_select_on(scraper)

        # 広告枠コピーの対象にする広告枠をチェックする
        # 該当広告枠をチェック
        pattern = csv_row["正規表現"]
        check_table_row_to_copy(scraper, pattern, True)

        # 広告枠コピーから対象広告枠を作成
        scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
        micro_func.button_click(
            scraper, "div#table_area input.btn.btn_wider", "value", "広告枠コピー"
        )

        scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
        micro_func.button_click(
            scraper, "table.tbl_input td > input.btn", "value", "選択"
        )

        scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
        micro_func.search_format_create(
            scraper, "メディアID", "1", str(csv_row["登録対象メディアID"])
        )
        micro_func.button_click(
            scraper, "table#tbl_data.tbl input.btn.btn_red", "value", "選択"
        )

        scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
        set_new_adframe_name(scraper, csv_row["登録広告枠名"], csv_row["正規表現"])

        micro_func.button_click(
            scraper, "form > p > input.btn.btn_wider_red", "value", "コピー"
        )
        micro_func.alert_click(scraper, 0.5, "OK")

        created_frames.add_created_frames([df.at[cnt_row, "登録広告枠名"]], "child")
        previous = csv_row["参照メディアID"]
        logger.info(f"「{df.at[cnt_row, '登録広告枠名']}」の登録を完了しました。")

        for i in range(3):
            try:
                scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
                break
            except Exception:
                logger.warning(f"ウィンドウの切り替えに失敗しました。{i + 1}回目")
                time.sleep(0.5)

        # 該当広告枠をチェックを外す
        check_table_row_to_copy(scraper, csv_row["正規表現"], False)


def check_table_row_to_copy(scraper: Scraper, pattern, checked: bool):
    logger = app_log.get_my_logger(__name__)
    table_row_css = "#tbl_data > tbody > tr"
    try:
        WebDriverWait(scraper.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#tbl_data > tbody > tr")))
    except TimeoutError:
        pass
    except NoSuchWindowException:
        scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
        logger.warning("ウィンドウに関してのエラーが発生しました")
    
    for i in range(3):
        try:
            time.sleep(0.5)
            i = 0
            for tr in scraper.find_elements_by_css(table_row_css):
                # 開始行はヘッダーのため含めない
                if i == 0:
                    i += 1
                    continue

                if re.fullmatch(pattern, scraper.find_element_by_css_in_element(tr, "a.a_list").text):
                    checkbox = scraper.find_element_by_css_in_element(tr, 'input[name="sel"]')
                    scraper.driver.execute_script(f"arguments[0].checked = {'true' if checked else 'false'};", checkbox)
                    logger.info(f"「{re.fullmatch(pattern, scraper.find_element_by_css_in_element(tr, 'a.a_list').text)[0]}」のチェックボックスを{'オン' if checked else 'オフ'}にしました。")
            break
        except Exception:
            logger.warning(f"チェックボックスのチェックに失敗しました。{i + 1}回目")
            time.sleep(0.5)


def set_new_adframe_name(scraper: Scraper, frame_name, pattern):
    logger = app_log.get_my_logger(__name__)
    for i in range(3):
        try:
            css_selection_adframe_list = (
                "#main_area > div > form > table:nth-child(41) > tbody > tr"
            )
            time.sleep(0.5)
            cnt_check = scraper.find_elements_by_css(css_selection_adframe_list)

            for c in range(len(cnt_check) - 1):
                time.sleep(0.5)
                check = scraper.find_element_by_css(f"#is_any_name{c}1")
                scraper.click_element_by_element(check)

            for tr in scraper.find_elements_by_css(css_selection_adframe_list):
                # 捜査中のcsvデータの行の正規表現に当てはまる文字列は存在するtrなら処理する
                if re.search(pattern, tr.text):
                    txbox = scraper.find_element_by_css_in_element(tr, 'input[type="text"]')
                    txbox.send_keys(frame_name)
                    break
            break
        except Exception:
            logger.warning(f"名前の入力に失敗しました。{i + 1}回目")
            time.sleep(0.5)