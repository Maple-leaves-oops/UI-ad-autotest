@echo off
REM ================================
REM 清理 allure-results 目录
REM ================================
if exist reports\allure-results (
    del /Q reports\allure-results\*
)

REM ================================
REM 运行 pytest
REM ================================
pytest tests/test_cases//test_03_toutiao_campaign.py -s -v --alluredir=reports/allure-results
if %errorlevel% neq 0 (
    echo  pytest 执行失败
    exit /b %errorlevel%
)

REM ================================
REM 生成 Allure 报告
REM ================================
allure generate reports/allure-results -o reports/allure-report --clean
if %errorlevel% neq 0 (
    echo allure generate 失败
    exit /b %errorlevel%
)

REM ================================
REM 打开 Allure 报告
REM ================================
allure open reports/allure-report
