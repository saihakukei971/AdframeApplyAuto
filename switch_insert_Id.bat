@echo off
REM リトライ回数の設定
set RETRY_COUNT=0
set MAX_RETRY=3

:RETRY_EXECUTE_INSERT
echo [INFO] execute_insert_id.py を実行します。（リトライ %RETRY_COUNT%/%MAX_RETRY%）

REM **Pythonスクリプトの実行**
.\python-embed\python execute_insert_id.py

REM **実行結果の確認**
if %errorlevel% neq 0 (
    set /a RETRY_COUNT+=1
    echo [ERROR] execute_insert_id.py でエラー発生！（%RETRY_COUNT%/%MAX_RETRY% 回目）

    REM **リトライ回数チェック**
    if %RETRY_COUNT% lss %MAX_RETRY% (
        echo [INFO] %RETRY_COUNT% 回目のリトライを 5 秒後に実行します...
        timeout /t 5 /nobreak >nul
        goto RETRY_EXECUTE_INSERT
    ) else (
        echo [FATAL] execute_insert_id.py の最大リトライ回数に達しました。処理を終了します。
        exit /b 1
    )
) else (
    echo [INFO] execute_insert_id.py が正常終了しました。
)

REM **正常終了時にブラウザを閉じる**
taskkill /IM chrome.exe /F >nul 2>&1

exit /b 0
