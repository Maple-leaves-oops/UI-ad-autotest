@echo off
REM ================================
REM 获取标准时间戳 YYYY_MM_DD_HH_MM_SS
REM ================================
for /f %%i in ('powershell -Command "Get-Date -Format yyyy_MM_dd_HH_mm_ss"') do set TIMESTAMP=%%i

REM ================================
REM 清理 allure-results 目录
REM ================================
if exist reports\allure-results (
    del /Q reports\allure-results\*
)

REM ================================
REM 运行 pytest
REM ================================
pytest tests/test_cases/test_03_toutiao_campaign.py -s -v --alluredir=reports/allure-results

REM ================================
REM 生成 Allure 报告，带时间戳目录
REM ================================
set REPORT_DIR=reports\allure-report-%TIMESTAMP%
allure generate reports/allure-results -o %REPORT_DIR% --clean
if %errorlevel% neq 0 (
    echo allure generate 失败，请检查 allure-results 是否为空
    exit /b %errorlevel%
)
