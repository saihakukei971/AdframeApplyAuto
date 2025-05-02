import time

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By

from core.scraper import Scraper
from log import app_log
from core import micro_func
from created_frames import created_frames


def apply_new_adframe(scraper: Scraper, side_menu, df):
    logger = app_log.get_my_logger(__name__)

    try:
        micro_func.click_sidemenu(scraper, side_menu)

        for row in range(len(df)):
            if (created_frames.check_created_frames([df.at[row, "親枠"]], "parent")):
                logger.info(f"既に親枠が作成された記録があるためスキップしました。メディアID: {df.at[row, 'メディアID']}")
                continue
            logger.info(f"親枠の作成を開始、メディアID: {df.at[row, 'メディアID']}")

            # 新規作成ボタンを押す
            micro_func.button_click(
                scraper, "div#table_area input.btn.btn_red", "value", "新規"
            )

            # 申請フロー
            parent_adframe_txbox = scraper.find_element_by_css(
                "table.tbl_input input.txBox"
            )
            parent_adframe_id = str(df.at[row, "親枠"]).strip()
            parent_adframe_txbox.send_keys(parent_adframe_id)
            logger.info(f"親枠の名称に「{parent_adframe_id}」を入力。")

            micro_func.choice_btn_click(scraper, "メディア")

            # メディア選択画面を開き、メディアを検索
            scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
            # ✅ 検索時に **完全一致検索** に変更
            search_value = f'{df.at[row, "メディアID"].item()}'  
            micro_func.search_format_create(scraper, "メディアID", "1", search_value)

            micro_func.button_click(
                scraper, "table#tbl_data.tbl input.btn.btn_red", "value", "選択"
            )

            # 広告枠選択画面を開き、広告枠を検索
            scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
            for i in range(3):
                try:
                    micro_func.choice_btn_click(scraper, "広告枠")
                    break
                except Exception:
                    logger.warning(f"ボタンのクリックに失敗しました。{i + 1}回目")
                    time.sleep(0.5)

            # 広告枠ポップアップ
            scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
            search_word_ary = [df.at[row, "レクタングル用"], df.at[row, "インフィード小"]]
            micro_func.search_format_create(
                scraper, "広告枠名", "3", " ".join(search_word_ary)
            )

            # テーブルの広告枠名が正しい場合、チェックボックスをクリック
            for attempt in range(3):  # 最大3回リトライ
                try:
                    for word in search_word_ary:
                        try:
                            checkbox = scraper.driver.find_element(By.XPATH, f"//*[@id='tbl_data']/tbody/tr/td[contains(text(), '{word}')]/following-sibling::td[11]/input")
                        except NoSuchElementException:
                            logger.info(f"「{word}」のチェックボックスは存在しません。")
                            continue
                        
                        scraper.driver.execute_script("arguments[0].checked = true;", checkbox)
                        logger.info(f"「{word}」にチェックを付けました。")
                    
                    break  # 成功したらループを抜ける

                except StaleElementReferenceException:
                    time.sleep(1)  # 再試行前に待機

            micro_func.button_click(
                scraper, "div#table_area input.btn.btn_wider_red", "value", "決定"
            )

            scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
            insert_ratio(scraper, df, row)
            logger.info("比率の入力完了。")

            micro_func.button_click(
                scraper, "div#input_area input[type='submit']", "value", "登録"
            )

            # 登録しますか？のアラートを押す
            micro_func.alert_click(scraper, 0.5, "OK")

            # 登録しましたのアラートを押す
            micro_func.alert_click(scraper, 0.5, "OK")

            logger.info(f"親枠の作成に成功、メディアID: {df.at[row, 'メディアID']}")
            created_frames.add_created_frames([df.at[row, "親枠"]], "parent")

    except NoSuchElementException as e:
        logger = app_log.get_my_logger(__name__)
        logger.info("The specified element may not exist.")
        logger.exception("The detailed error message -", exc_info=e)
        raise


def insert_ratio(scraper: Scraper, df, row):
    """比率を記入する関数"""
    try:
        i = 0
        for tr in scraper.find_elements_by_css("table.tbl_input tr"):
            # レクタングル・インフィード小どちらも比率を記入出来たら、繰り返しをやめる
            if i > 1:
                break

            if "広告枠ID" in tr.text:
                for tr_in_table in scraper.find_elements_by_css_in_element(
                    tr, "td table tr"
                ):
                    if (
                        "【f_" in tr_in_table.text
                        and "レクタングル" in tr_in_table.text
                    ):

                        for input in scraper.find_elements_by_css_in_element(
                            tr_in_table, 'input[type="text"]'
                        ):
                            input.send_keys(df.at[row, "レクタングル比率"].item())
                            i += 1

                    elif (
                        "【f_" in tr_in_table.text
                        and "インフィード用" in tr_in_table.text
                    ):
                        for input in scraper.find_elements_by_css_in_element(
                            tr_in_table, 'input[type="text"]'
                        ):
                            input.send_keys(df.at[row, "インフィード小比率"].item())
                            i += 1

                    else:
                        continue

    except NoSuchElementException as e:
        logger = app_log.get_my_logger(__name__)
        logger.info("The specified element may not exist.")
        logger.exception("The detailed error message -", exc_info=e)
        raise
