"""
主页面元素定位符
"""
from dataclasses import dataclass


@dataclass
class HomePageLocators:
    CREATE_TOUTIAO_CAMPAIGN_BUTTON = ("//div[contains(@class,'spreader-content')][.//div[contains(text(),'巨量引擎')]]//"
                                      "div[contains(@class,'spreader-btn') and normalize-space(text())='去创建']")
    # 判断：点击去创建后，是否跳转到相应页面
    CREATE_TOUTIAO_CAMPAIGN_SUCCESSS_PATH = "promotion/toutiao/batch-create/form-info"
