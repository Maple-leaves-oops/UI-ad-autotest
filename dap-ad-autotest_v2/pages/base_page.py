"""
Page Object 基类
作用：
(1) POM（Page Object Model）模式的基类，统一保存 Playwright 的 Page 实例。
(2) 子类页面对象（如 LoginPage、HomePage）继承它后，可以直接使用 self.page 进行页面操作。
(3) 方便扩展通用方法（如截图、等待加载、通用断言等），减少重复代码。

注：
(1)@dataclass:
@dataclass 用来自动生成类的样板代码，比如 __init__、__repr__、__eq__ 等
"""
from dataclasses import dataclass
from playwright.sync_api import Page
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
import pytest


@dataclass
class BasePage:
    page: Page

    def refresh_page(self):
        """刷新页面并等待加载完成"""
        self.page.reload()
        self.page.wait_for_load_state("networkidle")

    def wait_and_click(self, selector: str, timeout: int = 5000) -> None:
        """
        等待元素可点击并执行点击操作
        :param selector: 元素定位符
        :param timeout: 超时时间（毫秒）
        """
        try:
            self.page.locator(selector).click(timeout=timeout)
        except PlaywrightTimeoutError:
            pytest.fail(f"元素 {selector} 未找到或无法点击（超时 {timeout} ms）")

    def wait_and_fill(self, selector: str, value: str, timeout: int = 5000) -> None:
        """
        等待输入框出现并填充值
        :param selector: 输入框定位符
        :param value: 输入的值
        :param timeout: 超时时间（毫秒）
        """
        try:
            self.page.locator(selector).fill(value, timeout=timeout)
        except PlaywrightTimeoutError:
            pytest.fail(f"输入框 {selector} 未找到，无法输入 '{value}' （超时 {timeout} ms）")