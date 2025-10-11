import pytest
from dotenv import find_dotenv, load_dotenv
import os
from pathlib import Path
from playwright.sync_api import BrowserContext, Browser
from datetime import datetime
import allure
from utils.utils import load_yaml


@pytest.fixture(scope="session")
def credentials() -> dict:
    """
    加载系统环境变量配置：基础路径、用户名、密码等敏感信息

    说明：
    - load_dotenv(): 会从当前工作目录开始，逐级向上查找 `.env` 文件。
    - 本 Fixture 会加载 `.env` 文件，并提取以下字段：
      BASE_URL, DAP_USERNAME, DAP_PASSWORD
    - 返回时会统一转成小写 key，例如：
      {
        "base_url": "http://xxx",
        "dap_username": "test_user",
        "dap_password": "123456"
      }

    异常：
    - 找不到 .env 文件时，pytest.fail()
    - 缺少必要字段时，pytest.fail()

    :return: dict
        含登录所需的基础配置（base_url, dap_username, dap_password）
    """
    try:
        env_path = find_dotenv(usecwd=True)
        if not env_path:
            pytest.fail(f".env文件未找到")
        load_dotenv(env_path, override=False)
    except Exception as e:
        pytest.fail(f"加载.env文件失败: {e}")

    required_keys = ["BASE_URL", "DAP_USERNAME", "DAP_PASSWORD"]
    creds = {k.lower(): os.getenv(k) for k in required_keys}

    missing = [k for k, v in creds.items() if v is None]
    if missing:
        pytest.fail(f".env文件缺少必要字段: {', '.join(missing)}")

    return creds


@pytest.fixture(scope="session")
def browser_config() -> dict:
    """
    加载浏览器配置文件 `configs/browser.yaml`

    配置文件结构示例：
    browser:
      launch_args:
        headless: false
        channel: chrome
        slow_mo: 2000
        args: ["--start-maximized"]
      context_args:
        no_viewport: true
        ignore_https_errors: true

    :return: dict
        {
          "launch_args": {...},   # 启动参数
          "context_args": {...}   # 上下文参数
        }
    """
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "configs" / "browser.yaml"
    return load_yaml(config_path)["browser"]


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict, browser_config: dict) -> dict:
    """
    合并 pytest-playwright 默认浏览器启动参数和自定义配置文件参数

    :param browser_type_launch_args: pytest-playwright 内置默认参数
    :param browser_config: configs/browser.yaml 中的 launch_args 节点
    :return: dict
    """
    return {**browser_type_launch_args, **browser_config.get("launch_args", {})}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, browser_config: dict) -> dict:
    """
    合并 pytest-playwright 默认浏览器上下文参数和自定义配置文件参数

    :param browser_context_args: pytest-playwright 内置默认参数
    :param browser_config: configs/browser.yaml 中的 context_args 节点
    :return: dict
    """
    return {**browser_context_args, **browser_config.get("context_args", {})}


@pytest.fixture(scope="session")
def authenticated_context(browser: Browser, browser_context_args: dict) -> BrowserContext:
    """
    浏览器上下文，全局共享（session 级别）

    Playwright 三层架构：
    - Browser：浏览器进程（管理多个 Context）
    - BrowserContext：独立会话（隔离 cookie/localStorage/session）
    - Page：具体标签页（页面操作单元）

    功能：
    - 基于 pytest-playwright 提供的 browser fixture 创建 Context
    - 启用 trace 追踪（包含截图/DOM快照/源码）
    - trace 文件按天命名保存，例如 trace_2025_09_21.zip

    查看 trace：
    npx playwright show-trace trace_2025_09_21.zip

    :param browser: Browser 实例
    :param browser_context_args: dict，上下文参数
    :return: BrowserContext，全局复用
    """
    context = browser.new_context(**browser_context_args)
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    trace_dir = Path("trace")
    trace_dir.mkdir(parents=True, exist_ok=True)

    # 时间戳（到秒）
    date_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    trace_file = trace_dir / f"trace_{date_str}.zip"

    # 停止 tracing 并保存
    context.tracing.stop(path=str(trace_file))
    context.close()


# ======================================
# function 级别 HTTP 错误收集
# ======================================
@pytest.fixture(autouse=True)
def capture_http_errors(authenticated_context: BrowserContext, request):
    """
    每个测试用例独立捕获 HTTP 错误状态码
    """
    error_messages = []

    # 日志目录
    log_dir = Path("errors")
    log_dir.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime("%Y_%m_%d")
    log_file = log_dir / f"error_responses_{date_str}.log"

    # 事件监听函数
    def handle_response(response):
        if response.status >= 400:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_line = (
                f"[{timestamp}] [错误捕获] {response.status} {response.url}\n"
            )

            # 控制台输出
            print(log_line.strip())

            # 写入日志
            with log_file.open("a", encoding="utf-8") as f:
                f.write(log_line)

            # 收集到本用例列表
            error_messages.append(log_line.strip())

    # 给 session 级 context 注册监听
    authenticated_context.on("response", handle_response)

    # 测试用例执行
    yield

    # 测试结束时 fail（挂到本用例）
    if error_messages:
        # Allure attach
        allure.attach(
            "\n".join(error_messages),
            name="HTTP 错误状态码",
            attachment_type=allure.attachment_type.TEXT
        )

        # 让用例失败
        pytest.fail("HTTP 错误发生在本用例:\n" + "\n".join(error_messages), pytrace=False)


@pytest.fixture(scope="session")
def login_page(authenticated_context: BrowserContext, credentials: dict):
    """
    登录页面 Fixture（session 级别）

    流程：
    1. 基于 authenticated_context 创建新 Page
    2. 实例化 LoginPage（POM）
    3. 执行登录操作
    4. 返回已登录的 LoginPage 实例

    依赖链：
    authenticated_context → login_page

    :param authenticated_context: 已认证的 BrowserContext
    :param credentials: dict, 登录凭证
    :return: LoginPage 已登录页面对象
    """
    page = authenticated_context.new_page()
    from pages.login_page import LoginPage
    login_pom = LoginPage(page, credentials)
    login_pom.login()
    yield login_pom


@pytest.fixture(scope="session")
def home_page(login_page):
    """
    主页面 Fixture（session 级别）

    流程：
    1. 基于已登录的 login_page.page
    2. 实例化 HomePage（POM）
    3. 点击“去创建”，捕获新窗口
    4. 返回新窗口的 HomePage 实例

    依赖链：
    authenticated_context → login_page → home_page

    注意：
    - 必须重新赋值，否则仍然停留在旧页面

    :param login_page: 已登录的 LoginPage
    :return: HomePage，已进入新窗口
    """
    from pages.home_page import HomePage
    home_pom = HomePage(login_page.page)
    home_pom = home_pom.create_toutiao_campaign()
    yield home_pom


@pytest.fixture(scope="class")
def campaign_page_toutiao(home_page):
    """
    头条广告创建页面 Fixture（class 级别）

    流程：
    1. 基于 home_page.page
    2. 实例化 CampaignPageToutiao（POM）
    3. 返回该实例，供用例调用

    依赖链：
    authenticated_context → login_page → home_page → campaign_page_toutiao

    :param home_page: 已进入新广告页面的 HomePage
    :return: CampaignPageToutiao
    """
    from pages.campaign_page_toutiao import CampaignPageToutiao
    campaign_toutiao_pom = CampaignPageToutiao(home_page.page)
    yield campaign_toutiao_pom


# @pytest.fixture(scope="session")
# def screenshot_config() -> dict:
#     """
#     截图配置（session 级别）
#
#     配置文件结构：configs/screenshot.yaml
#     path:
#       dir: screenshots     # 截图根目录
#       file: failures       # 子目录
#
#     :return: dict
#         {"dir": Path(...), "file": Path(...)}
#     """
#     base_dir = Path(__file__).resolve().parent
#     config_path = base_dir / "configs" / "screenshot.yaml"
#     cfg = load_yaml(config_path)["path"]
#
#     return {
#         "dir": Path(cfg["dir"]),
#         "file": Path(cfg["file"])
#     }
#
#
# @pytest.fixture(scope="function", autouse=True)
# def capture_screenshot_on_failure(request, authenticated_context: BrowserContext, screenshot_config: dict):
#     """
#     全局自动截图 Fixture（function 级别，autouse=True）
#
#     功能：
#     - 每个用例执行后，若 call 阶段失败，自动截取当前页面
#     - 截图文件命名：<用例名>_<时间戳>.png
#     - 截图关联到 Allure 报告，方便快速定位失败原因
#
#     关键点：
#     - request.node.rep_call: 来自 pytest_runtest_make_report 钩子，表示用例执行结果
#     - authenticated_context.pages[-1]: 获取最后一个活跃页面，避免多标签页误截
#     - full_page=True: 截取完整页面（含滚动区域）
#     """
#     yield
#
#     if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
#         case_name = request.node.name.replace("[", "_").replace("]", "_").replace("/", "_")
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         screenshot_path = screenshot_config['dir'] / screenshot_config['file'] / f"{case_name}_{timestamp}.png"
#
#         page = authenticated_context.pages[-1] if authenticated_context.pages else None
#         if not page:
#             allure.attach("截图失败：无活跃页面", name="截图异常", attachment_type=allure.attachment_type.TEXT)
#             return
#
#         try:
#             page.screenshot(path=str(screenshot_path), full_page=True, timeout=10000)
#         except Exception as e:
#             allure.attach(f"截图执行失败：{str(e)}", name="截图异常", attachment_type=allure.attachment_type.TEXT)
#             return
#
#         allure.attach.file(str(screenshot_path),
#                            name=f"用例失败截图_{timestamp}",
#                            attachment_type=allure.attachment_type.PNG,
#                            extension="png")
#
#
# @pytest.hookimpl(tryfirst=True, hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     """
#     Pytest 钩子：生成测试报告结果
#
#     功能：
#     - 在 setup/call/teardown 阶段执行后，记录执行结果
#     - 将结果对象挂载到 item 上，供 fixture 访问
#
#     例如：
#     - item.rep_setup
#     - item.rep_call
#     - item.rep_teardown
#
#     capture_screenshot_on_failure 就是通过 item.rep_call 判断用例是否失败
#     """
#     outcome = yield
#     rep = outcome.get_result()
#     setattr(item, f"rep_{rep.when}", rep)


# def pytest_collection_modifyitems(items):
#     """
#     测试用例收集完成时，将收集到的item的name和nodeid的中文显示在控制台上
#     """
#     for item in items:
#         item.name = item.name.encode("utf-8").decode("unicode_escape")
#         item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")
