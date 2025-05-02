import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

from core import micro_func
from core.scraper import Scraper
from log import app_log
from created_frames import created_frames

def create_new_adframe(scraper: Scraper, side_menu, df):
    logger = app_log.get_my_logger(__name__)
    previous_id = ""
    for cnt_row in range(len(df)):
        if (created_frames.check_created_frames([df.at[cnt_row, "レクタングル用"], df.at[cnt_row, "インフィード小"]], "child_multi")):
            logger.info(f"既に子枠が作成された記録があるためスキップしました。メディアID: {df.at[cnt_row, 'メディアID']}")
            continue
        logger.info(f"子枠の作成を開始、メディアID: {df.at[cnt_row, 'メディアID']}")

        if (cnt_row == 0 or df.at[cnt_row, "参照メディアID"].item() != df.at[cnt_row - 1, "参照メディアID"].item() or df.at[cnt_row, "参照メディアID"].item() != previous_id):
            micro_func.click_sidemenu(scraper, side_menu)
            micro_func.search_format_create(
                scraper, "メディアID", "1", df.at[cnt_row, "参照メディアID"].item()
            )
            click_media_link(scraper)
            micro_func.status_select_on(scraper)
            check_table_row_to_copy(scraper)

        scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
        for i in range(3):
            try:
                micro_func.button_click(
                    scraper, "div#table_area input.btn.btn_wider", "value", "広告枠コピー"
                )
                break
            except Exception:
                logger.warning(f"ボタンのクリックに失敗しました。{i + 1}回目")
                time.sleep(0.5)
        scraper.driver.switch_to.window(scraper.driver.window_handles[-1])

        for i in range(3):
            try:
                micro_func.button_click(
                    scraper, "table.tbl_input td > input.btn", "value", "選択"
                )
                break
            except Exception:
                logger.warning(f"ボタンのクリックに失敗しました。{i + 1}回目")
                time.sleep(0.5)

        scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
        micro_func.search_format_create(
            scraper, "メディアID", "1", df.at[cnt_row, "メディアID"].item()
        )

        for i in range(3):
            try:
                micro_func.button_click(
                    scraper, "table#tbl_data.tbl input.btn.btn_red", "value", "選択"
                )
                break
            except Exception:
                logger.warning(f"ボタンのクリックに失敗しました。{i + 1}回目")
                time.sleep(0.5)
        scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
        set_new_adframe_name(scraper, df, cnt_row)

        logger.info(f"子枠の作成に成功、メディアID: {df.at[cnt_row, 'メディアID']}")
        previous_id = df.at[cnt_row, "参照メディアID"].item()
        created_frames.add_created_frames([df.at[cnt_row, "レクタングル用"], df.at[cnt_row, "インフィード小"]], "child_multi")




def click_media_link(scraper: Scraper):
    media_name_link = scraper.find_element_by_css(".a_list")
    scraper.click_element_by_element(media_name_link)
    WebDriverWait(scraper.driver, 2).until(EC.staleness_of(media_name_link))

def check_table_row_to_copy(scraper: Scraper):
    check_map = {"24 ﾚｸﾀﾝｸﾞﾙ　全体紐づけ": False, "3 ｲﾝﾌｨｰﾄﾞ_小": False}

    for key in check_map.keys():
        try:
            checkbox = WebDriverWait(scraper.driver, 2).until(
                EC.presence_of_element_located((By.XPATH, f"//td[contains(text(), '{key}')]/following-sibling::td[10]/input"))
            )
            scraper.driver.execute_script("arguments[0].checked = true;", checkbox)
            check_map[key] = True
            if all(check_map.values()):
                break
        except TimeoutException:
            continue

#追加20250304# ✅ 追加: 20250304
def set_new_adframe_name(scraper: Scraper, df, cnt_row):
    logger = app_log.get_my_logger(__name__)

    # ✅ 1. ポップアップウィンドウに確実に切り替える
    WebDriverWait(scraper.driver, 5).until(lambda d: len(d.window_handles) >= 1)
    scraper.driver.switch_to.window(scraper.driver.window_handles[-1])

    # ✅ 2. ページの完全な読み込みを待機（最大15秒）
    WebDriverWait(scraper.driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # ✅ 3. `tr` 要素を確実に取得（最大15秒待機）
    for attempt in range(3):  # 最大3回リトライ
        try:
            WebDriverWait(scraper.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#main_area form table:last-of-type tbody tr"))
            )

            #任意名称にラジオボタンを変更
            scraper.driver.execute_script("arguments[0].click();", scraper.driver.find_element(By.CSS_SELECTOR, 'input#is_any_name01'))
            WebDriverWait(scraper.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#main_area form table:last-of-type tbody tr"))
            )
            scraper.driver.execute_script("arguments[0].click();", scraper.driver.find_element(By.CSS_SELECTOR, 'input#is_any_name11'))

            WebDriverWait(scraper.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#main_area form table:last-of-type tbody tr"))
            )

            rows = scraper.driver.find_elements(By.CSS_SELECTOR, "#main_area form table:last-of-type tbody tr")
            if not rows:
                raise StaleElementReferenceException
            break  # 成功したらループを抜ける
        except StaleElementReferenceException:
            time.sleep(1)  # 再試行前に待機

    # ✅ `tr` が取得できた場合のみ処理を実行
    任意名称1_入力完了 = False
    任意名称2_入力完了 = False

    for attempt in range(3):  # 最大3回リトライ
        try:
            for tr in rows:
                #print(f"🛠 Debug: Processing tr element - {tr.text}")  # デバッグ用
                if tr.text == "選択広告枠一覧":
                    continue

                # ✅ `input[type="text"]` を取得（リトライ付き）
                for retry in range(3):
                    try:
                        txbox = WebDriverWait(tr, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'td input[type="text"]'))
                        )
                        break  # 成功したらループを抜ける
                    except StaleElementReferenceException:
                        time.sleep(1)  # 再試行前に待機
                else:
                    continue  # `txbox` の取得に3回失敗したら次の `tr` へ

                # ✅ `txbox` が画面に表示されるまで待機
                WebDriverWait(scraper.driver, 5).until(EC.visibility_of(txbox))

                # ✅ 既存の値を削除し、確実に入力
                txbox.clear()

                # ✅ 正しい値を取得
                input_text = ""
                if "レクタングル用" in tr.text:
                    input_text = str(df.iloc[cnt_row]["レクタングル用"]).strip()
                    任意名称1_入力完了 = True
                elif "インフィード用" in tr.text:
                    input_text = str(df.iloc[cnt_row]["インフィード小"]).strip()
                    任意名称2_入力完了 = True

                if not input_text:
                    input_text = "デフォルト名称"

                # ✅ `send_keys()` で値を入力
                txbox.send_keys(input_text)
                logger.info(f"任意名称に「{input_text}」を入力。")

                # ✅ 入力値が正しくセットされたか確認
                entered_value = txbox.get_attribute("value")
                if entered_value.strip() != input_text.strip():
                    continue  # もう一度試す

            # ✅ 両方の入力が完了したかチェック
            if not (任意名称1_入力完了 and 任意名称2_入力完了):
                raise Exception("⚠️ Error: 任意名称1 または 任意名称2 のどちらかが入力されていません")

            logger.info("任意名称の設定に成功。")
            break  # 成功したらループを抜ける

        except StaleElementReferenceException:
            time.sleep(1)  # 再試行前に待機
            rows = scraper.driver.find_elements(By.CSS_SELECTOR, "#main_area form table:last-of-type tbody tr")  # ✅ `tr` を再取得
            continue  # 再試行

        except TimeoutException:
            time.sleep(1)
            continue  # 再試行

    # ✅ **コピー処理を確実に実行**
    for attempt in range(3):  # 最大3回リトライ
        try:
            copy_button = WebDriverWait(scraper.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'form > p > input.btn.btn_wider_red'))
            )
            scraper.driver.execute_script("arguments[0].click();", copy_button)  # **JSでクリック**
            break  # 成功したらループを抜ける
        except (StaleElementReferenceException, TimeoutException):
            time.sleep(1)  # 再試行前に待機
    
    micro_func.alert_click(scraper, 0.5, "OK")

    # ✅ 6. クリック後にポップアップが閉じる可能性があるので、ウィンドウを再取得
    if len(scraper.driver.window_handles) > 1:
        scraper.driver.switch_to.window(scraper.driver.window_handles[-1])
    else:
        scraper.driver.switch_to.window(scraper.driver.window_handles[0])