@echo off
setlocal

REM バッチファイルが置いてあるディレクトリを取得
cd %~dp0

REM (1) execute_create_multi_adframe.py を実行（最大3回リトライ）
set RETRY_COUNT=0
set MAX_RETRY=10

:RETRY_EXECUTE_CREATE
.\python-embed\python.exe execute_create_multi_adframe.py
if %errorlevel% neq 0 (
    set /a RETRY_COUNT+=1
    echo [WARNING] execute_create_multi_adframe.py でエラー発生！（%RETRY_COUNT%/%MAX_RETRY% 回目）
    
    if %RETRY_COUNT% lss %MAX_RETRY% (
        echo [INFO] %RETRY_COUNT% 回目のリトライを 5 秒後に実行します...
        timeout /t 5 /nobreak >nul
        goto RETRY_EXECUTE_CREATE
    ) else (
        echo [ERROR] execute_create_multi_adframe.py の最大リトライ回数に達しました。次の処理を継続します。
    )
) else (
    echo [INFO] execute_create_multi_adframe.py が正常終了しました。
)

REM (2) execute_insert_id.py を実行（最大3回リトライ）
set RETRY_COUNT=0

:RETRY_EXECUTE_INSERT
.\python-embed\python.exe execute_insert_id.py
if %errorlevel% neq 0 (
    set /a RETRY_COUNT+=1
    echo [ERROR] execute_insert_id.py でエラー発生！（%RETRY_COUNT%/%MAX_RETRY% 回目）

    if %RETRY_COUNT% lss %MAX_RETRY% (
        echo [INFO] %RETRY_COUNT% 回目のリトライを 5 秒後に実行します...
        timeout /t 5 /nobreak >nul
        goto RETRY_EXECUTE_INSERT
    ) else (
        echo [FATAL] execute_insert_id.py の最大リトライ回数に達しました。処理を終了します。
    )
) else (
    echo [INFO] execute_insert_id.py が正常終了しました。
)

REM コマンドプロンプトを自動で閉じる
exit /b 0
