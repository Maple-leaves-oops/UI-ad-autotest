"""
登录页面：http://dap-staging-6.micro-stage.lilith.sh/login?from，使用账号密码进行登录
"""
from dataclasses import dataclass
from urllib.parse import urljoin
from pages.base_page import BasePage
from locators.login_page_locators import LoginPageLocators
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import pytest


@dataclass
class LoginPage(BasePage):
    """
    :param credentials 登录凭证
    """
    credentials: dict

    def login(self) -> None:
        """
        :return: None
        """
        login_url = urljoin(self.credentials["base_url"], "/login")

        try:
            self.page.goto(login_url, wait_until="networkidle")
        except PlaywrightTimeoutError:
            pytest.fail(f"跳转到登录页面失败: {login_url}")

        try:
            self.page.locator(LoginPageLocators.SWITCH_TO_UESRNAME_PASSWORD_LOGIN).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail(f"无法点击账户密码登录")

        try:
            self.page.fill(LoginPageLocators.USERNAME_INPUT, self.credentials["dap_username"], timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail("未找到用户名输入框")

        try:
            self.page.fill(LoginPageLocators.PASSWORD_INPUT, self.credentials["dap_password"], timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail("未找到密码输入框")

        try:
            self.page.click(LoginPageLocators.LOGIN_BUTTON, timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail("未找到或无法点击登录按钮")

    def is_logged_in(self) -> bool:
        try:
            self.page.wait_for_url(f"**/{LoginPageLocators.LOGIN_SUCCESS_PATH}", timeout=10000)
        except PlaywrightTimeoutError:
            # 超时了也不直接 fail，而是再检查一次当前URL
            pass
        return LoginPageLocators.LOGIN_SUCCESS_PATH in self.page.url
