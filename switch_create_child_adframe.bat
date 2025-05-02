@echo off
setlocal

REM バッチファイルが置いてあるディレクトリを取得
cd %~dp0

REM (1) execute_create_child_adframe.py を実行（最大3回リトライ）
set RETRY_COUNT=0
set MAX_RETRY=10

:RETRY_EXECUTE_CHILD_CREATE
echo [INFO] execute_create_child_adframe.py を実行します...
.\python-embed\python.exe execute_create_child_adframe.py

if %errorlevel% neq 0 (
    set /a RETRY_COUNT+=1
    echo [WARNING] execute_create_child_adframe.py でエラー発生！（%RETRY_COUNT%/%MAX_RETRY% 回目）

    if %RETRY_COUNT% lss %MAX_RETRY% (
        echo [INFO] %RETRY_COUNT% 回目のリトライを 5 秒後に実行します...
        timeout /t 5 /nobreak >nul
        goto RETRY_EXECUTE_CHILD_CREATE
    ) else (
        echo [ERROR] execute_create_child_adframe.py の最大リトライ回数に達しました。処理を終了します。
    )
) else (
    echo [INFO] execute_create_child_adframe.py が正常終了しました。
)

REM コマンドプロンプトを自動で閉じる
exit /b 0
