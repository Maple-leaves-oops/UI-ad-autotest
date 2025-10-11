import allure


@allure.epic("创编UI自动化")
@allure.feature("头条广告创编测试")
@allure.story("点击头条广告创建按钮后能否正常跳转到批量创建页面测试")
def test_login_success(home_page):
    """测试：用户点击头条广告创建按钮后能否正常跳转到批量创建页面"""
    assert home_page.is_created_toutiao_campaign(), "点击头条的去创建按钮，未成功跳转到广告创建页面"
