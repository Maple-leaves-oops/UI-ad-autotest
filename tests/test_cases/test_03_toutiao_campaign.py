import pytest
import allure
from utils.utils import load_yaml, generate_test_combinations


# 加载数据
base_data = load_yaml("tests/test_data/base_data.yaml")
scenarios = load_yaml("tests/test_data/scenarios.yaml")
all_scenarios = scenarios["short_video_scenarios"] + scenarios["live_scenarios"]


@allure.epic("创编UI自动化")
@allure.feature("头条广告创编测试")
class TestCampaignCreate:
    """
    参数化用例 @pytest.mark.parametrize 的作用：
    - 根据场景数据（scenarios.yaml）动态生成多组测试用例
    - 每个场景作为一条独立用例运行，Allure 报告里会展示为多条 case
    - 通过 ids 参数给每个用例命名，便于在报告中区分具体场景
    - 实现数据驱动测试：测试逻辑保持不变，输入数据不同即可覆盖多种业务情况
    """
    @allure.story("批量创建测试-新版")
    @pytest.mark.parametrize(
        "scenario",
        all_scenarios,
        ids=lambda s: s["name"]
    )
    def test_create_campaign(self, campaign_page_toutiao, scenario):
        """创建广告,只取每个场景的第一个组合"""
        index = all_scenarios.index(scenario)
        if index < 0:
            pytest.skip(f"调试阶段，跳过第{index + 1}个用例")
        # 注：next() 每个场景只取第一个组合进行测试，否则组合数过多执行时间过长
        test_data = next(generate_test_combinations(scenario, base_data))
        case_id = f"{test_data['scenario_name']}"
        # 开始执行用例测试
        with allure.step(f"执行组合测试: {case_id}"):
            allure.dynamic.title(case_id)
            allure.dynamic.description(f"测试组合: {test_data}")
            # create_result = campaign_page_toutiao.create_campaign(test_data)
            # refresh_page刷新页面，防止由于过往用例执行失败（比如找不到数据无法点击确定按钮）导致卡死，无法执行后面的用例
            # 但是我好像记得dap_ad_autotest中新版广告创建时也会存在没数据导致卡死的问题
            # campaign_page_toutiao.refresh_page()
            # # 验证结果
            # assert create_result, f"广告{case_id}创建流程失败，无法进入预览页面"
            """
            注意：在 pytest + Playwright 这种结构里，一旦 create_campaign(test_data) 内部抛了异常（比如定位不到元素、点击超时），
            pytest 会立即认为这个测试步骤失败，然后：不会执行后续代码（包括 refresh_page()）。
            pytest 直接进入 teardown 阶段，标记用例失败。写的刷新页面逻辑根本没有机会运行。
            """
            # 修改刷新逻辑
            try:
                create_result = campaign_page_toutiao.create_campaign(test_data)
                assert create_result, f"广告{case_id}创建流程失败，无法进入预览页面"
            finally:
                # 无论成功/失败，都执行刷新，避免卡死
                campaign_page_toutiao.refresh_page()
