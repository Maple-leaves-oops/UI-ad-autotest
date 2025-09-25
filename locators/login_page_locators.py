"""
登录页面元素定位符
说明：集中管理登录页中所有控件的XPATH定位，方便维护和修改。
"""
from dataclasses import dataclass


@dataclass
class LoginPageLocators:
    SWITCH_TO_UESRNAME_PASSWORD_LOGIN = "//p[contains(text(),'账户密码登录')]"
    USERNAME_INPUT = "//input[@placeholder='用户名']"
    PASSWORD_INPUT = "//input[@placeholder='密码']"
    LOGIN_BUTTON = "//button[normalize-space(text())='登录']"
    LOGIN_SUCCESS_PATH = "advertise-2/home"
