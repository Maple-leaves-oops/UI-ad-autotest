"""
主页面：在进行登录后到达的页面：http://dap-staging-6.micro-stage.lilith.sh/advertise-2/home
"""
from dataclasses import dataclass
import pytest
from pages.base_page import BasePage
from locators.home_page_locators import HomePageLocators
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import allure


@dataclass
class HomePage(BasePage):
    def create_toutiao_campaign(self):
        """
        点击去创建按钮并返回新打开的页面对象

        :return: 新的 Page 实例
        """
        max_retries = 2
        for attempt in range(1, max_retries + 1):
            try:
                with self.page.expect_popup() as popup_info:
                    self.page.locator(
                        HomePageLocators.CREATE_TOUTIAO_CAMPAIGN_BUTTON
                    ).click(timeout=10000)
                new_page = popup_info.value
                return HomePage(new_page)

            except PlaywrightTimeoutError:
                if attempt < max_retries:
                    # TODO print的内容可以考虑到写在logging中
                    print(f"第 {attempt} 次进入主页面失败，刷新页面后重试...")
                    with allure.step(f"第 {attempt} 次进入主页面失败，刷新页面后重试..."):
                        self.page.reload()
                else:
                    pytest.fail("无法点击头条的去创建按钮，或未触发新页面")

    def is_created_toutiao_campaign(self) -> bool:
        """
        判断是否成功跳转到了创建头条广告的页面

        :return:
        """
        try:
            self.page.wait_for_url(f"**/{HomePageLocators.CREATE_TOUTIAO_CAMPAIGN_SUCCESSS_PATH}", timeout=10000)
        except PlaywrightTimeoutError:
            pass
        return HomePageLocators.CREATE_TOUTIAO_CAMPAIGN_SUCCESSS_PATH in self.page.url
