import allure


@allure.epic("创编UI自动化")
@allure.feature("用户登录页面")
@allure.story("正确登录后能否跳转到广告创建页面测试")
def test_login_success(login_page):
    """测试：用户用正确账号密码登录后是否能进入成功跳转"""
    assert login_page.is_logged_in(), "登录后未成功跳转"
