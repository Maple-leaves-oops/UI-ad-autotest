"""
头条广告创建计划页面：在首页点击头条广告的去创建按钮后到达的页面：http://dap-staging-6.micro-stage.lilith.sh/promotion/toutiao/batch-create/form-info
批量创建页面[新版]
包含页面具体操作方法、验证元素存在方法、页面加载状态。。。
"""
import pytest
from pages.base_page import BasePage
from locators.campaign_page_toutiao_locators import CampaignPageToutiaoLocators
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import re
import warnings
import allure


class CampaignPageToutiao(BasePage):
    """新版巨量引擎-批量创建页面操作类"""
    def is_loaded(self):
        """验证页面是否加载完成"""
        return self.page.is_visible(CampaignPageToutiaoLocators.PAGE_TITLE)

    def get_current_page_url(self):
        """获取当前页面 URL，用于判断跳转"""
        return self.page.url

    def create_campaign(self, test_data):
        """根据测试数据创建广告"""

        # #调换1、2两个部分字段的操作顺序，解决切换【推广目的】【营销场景】字段值导致账户清空的问题，避免导致后续数据为空
        # #顺序为：先【关联游戏】、再【营销目标与场景】、最后【投放账户】
        # 1.1关联游戏
        self.set_game(test_data["game"])

        # 2. 营销目标与场景【推广目标、投放类型、营销场景、广告类型、投放模式、】
        self.set_purpose_and_scene(
            test_data["purpose"],
            test_data.get("sub_purpose"),
            test_data["scene"],
            test_data["ad_type"],
            test_data["delivery_mode"],
            test_data["game"]
        )

        # 1.2 投放账户
        self.set_account(test_data["account"])

        # 3. 投放内容与目标【星广联投任务、应用类型、推广应用、转化目标】
        if "star_task" in test_data:
            star_task = test_data["star_task"]
        else:
            star_task = None
        self.set_content_and_target(test_data["app_type"], test_data["ad_type"], test_data["delivery_mode"], star_task)

        # 4. 投放版位【投放位置、媒体选择】
        # 只有通投-手动时，需要手动选择投放版位，其他情景下只有一个选项，默认选择。
        if test_data["ad_type"] == "通投广告" and test_data["delivery_mode"] == "手动投放":
            self.set_placement(
                test_data["placement"],
            )

        # 5.用户定向【定向盒子、过滤已转化、过滤时间、】
        # todo 若固定过滤转化和过滤时间的话，这里可以直接不进行区分
        if test_data["filter_type"] == "公司账户" or test_data["filter_type"] == "APP":
            self.set_targeting(
            )
        else:
            self.set_targeting(
            )

        # 6. 广告设置【原生广告投放、创意盒子/素材组、产品名称、产品主图、产品卖点、行动号召】
        if "native_ad" in test_data:
            native_ad = test_data["native_ad"]
        else:
            native_ad = None
        if "material_type" in test_data:
            material_type = test_data["material_type"]
        else:
            material_type = None
        if test_data["app_type"] == "安卓应用":
            land_page = test_data["app_type"]
        else:
            land_page = None
        if "star_task" in test_data:
            star_task = test_data["star_task"]
        else:
            star_task = None
        if "dy_material" in test_data:
            dy_material = test_data["dy_material"]
        else:
            dy_material = None
        # 搜索-极速智投、搜索-常规投放，需要文本摘要
        if test_data["ad_type"] == "搜索广告":
            text_summary = "文本摘要"
        else:
            text_summary = None
        self.set_creative(native_ad=native_ad, game=test_data['game'], land_page=land_page,
                          material_type=material_type, text_summary=text_summary, star_task=star_task,
                          dy_material=dy_material)

        # 7. 排期与预算【投放时间、投放时段、竞价策略、项目预算、付费方式 / 竞价策略、广告预算、广告出价】
        if test_data["ad_type"] == "通投广告" and test_data["delivery_mode"] == "自动投放":  # 没有项目预算选项、竞价策略新增最大转化
            # 竞价策略【选择原则：通投-自动，传入“最大转化”值进行选择；其他默认不操作】
            budget_type = None
            daily_budget = None
            bidding_strategy = test_data["bidding_strategy"]
        else:
            bidding_strategy = None
            budget_type = test_data["budget_type"]
            if test_data["budget_type"] == "不限":  # 没有日预算
                daily_budget = None
            else:
                daily_budget = test_data["daily_budget"]
        self.set_budget(
            time=test_data["time"],
            time_period=test_data["time_period"],
            bidding_strategy=bidding_strategy,  # 竞价策略【选择原则：通投-自动，传入“最大转化”值进行选择；其他默认不操作】
            daily_budget=daily_budget,
            ad_budget=test_data["ad_budget"],
            ad_bid=test_data["ad_bid"],
            budget_type=budget_type
        )

        # 8.设置搜索快投/搜索广告：【只考虑通投广告-手动投放即可】
        # 搜索快投：仅通投广告-手动投放需要：【(出价系数、定向拓展)】
        # 搜索广告-常规投放：智能拓流、动态创意【只有开启选项，无需设置】
        if test_data["ad_type"] == "通投广告" and test_data["delivery_mode"] == "手动投放":
            self.set_search_express(
                test_data["bid_factor"],
                test_data["expansion"]
            )

        # 9. 项目生成方式与标签【项目生成方式、投放类型、/+（项目启停设置、广告启停设置）】
        # 直播-直播素材，项目生成方式 只有“按受众”选项可以选择【存在默认选择，就可以不进行操作】
        self.set_generation(
            test_data["generation_type"],
            test_data["campaign_type"],
            test_data["campaign_status"],
            test_data["ad_status"]
        )

        # 验证创建成功
        return self._verify_creation_success()

    def set_game(self, game):
        """1.1选择关联游戏"""
        try:
            # 点击下拉框
            self.page.locator(CampaignPageToutiaoLocators.GAME_SELECTOR_NEW).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail("选择游戏失败：未找到或无法点击下拉框")
        except Exception as e:
            pytest.fail(f"选择游戏失败：发生未知错误 {e}")

        try:
            # 点击具体游戏选项（模板传参）
            self.page.locator(CampaignPageToutiaoLocators.GAME_SELECTED.format(game=game)).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail(f"选择游戏失败：未找到或无法点击选项 '{game}'")
        except Exception as e:
            pytest.fail(f"选择游戏失败：发生未知错误 {e}")

    def set_purpose_and_scene(self, purpose, sub_purpose, scene, ad_type, delivery_mode, game):
        """2.选择营销目标与场景【(推广目标、投放类型/投放内容)、营销场景、广告类型、投放模式】"""
        # 点击左侧侧边栏，定位到营销目标与场景
        try:
            self.page.locator(CampaignPageToutiaoLocators.LIST_PURPOSE_SCENE).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail("选择营销目标与场景失败：未找到或无法点击")
        except Exception as e:
            pytest.fail(f"选择营销目标与场景失败：发生未知错误 {e}")

        # 推广目标：应用推广/小程序
        try:
            self.page.locator(
                CampaignPageToutiaoLocators.PURPOSE_SCENE_SELECTOR_NEW.format(purpose=purpose)
            ).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail(f"选择推广目标失败：未找到或无法点击选项 '{purpose}'")
        except Exception as e:
            pytest.fail(f"选择推广目标失败：发生未知错误 {e}")

        # 子目标：投放类型/投放内容
        if sub_purpose:
            try:
                self.page.locator(
                    CampaignPageToutiaoLocators.SUB_PURPOSE_LABEL_LOCATOR.format(sub_purpose=sub_purpose)
                ).click(timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail(f"选择子目标失败：未找到或无法点击选项 '{sub_purpose}'")
            except Exception as e:
                pytest.fail(f"选择子目标失败：发生未知错误 {e}")

        # 营销场景
        try:
            self.page.locator(
                CampaignPageToutiaoLocators.PURPOSE_SCENE_LABEL_NEW.format(scene_ad_type_delivery_mode=scene)
            ).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail(f"选择营销场景失败：未找到或无法点击选项 '{scene}'")
        except Exception as e:
            pytest.fail(f"选择营销场景失败：发生未知错误 {e}")

        # 广告类型
        try:
            self.page.locator(
                CampaignPageToutiaoLocators.PURPOSE_SCENE_LABEL_NEW.format(scene_ad_type_delivery_mode=ad_type)
            ).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail(f"选择广告类型失败：未找到或无法点击选项 '{ad_type}'")
        except Exception as e:
            pytest.fail(f"选择广告类型失败：发生未知错误 {e}")

        # 投放模式
        try:
            self.page.locator(
                CampaignPageToutiaoLocators.PURPOSE_SCENE_LABEL_NEW.format(scene_ad_type_delivery_mode=delivery_mode)
            ).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail(f"选择投放模式失败：未找到或无法点击选项 '{delivery_mode}'")
        except Exception as e:
            pytest.fail(f"选择投放模式失败：发生未知错误 {e}")

        # 搜索广告-极速智投，新增蓝海关键词选项、自定义关键词（非必选）
        lanhai_key = self.page.locator(CampaignPageToutiaoLocators.LANHAI_KEY)
        if lanhai_key.is_visible():
            try:
                lanhai_key.click(timeout=5000)  # 点击 添加蓝海关键词 按钮
            except PlaywrightTimeoutError:
                pytest.fail("蓝海关键词按钮点击失败：未找到或无法点击")
            except Exception as e:
                pytest.fail(f"蓝海关键词按钮点击失败：发生未知错误 {e}")

            try:
                self.page.locator(
                    CampaignPageToutiaoLocators.LANHAI_KEYWORD_TITLE.format(game=game)
                ).wait_for(state="visible", timeout=10000)
            except PlaywrightTimeoutError:
                pytest.fail(f"蓝海关键词分组标题未出现：'{game}'")
            except Exception as e:
                pytest.fail(f"蓝海关键词分组标题等待失败：发生未知错误 {e}")

            try:
                (self.page.locator(CampaignPageToutiaoLocators.GAME_GROUP_SELECTOR.format(game=game))
                 .wait_for(state="visible", timeout=5000))
            except PlaywrightTimeoutError:
                pytest.fail(f"未找到游戏分组: {game}，请检查游戏名称或页面加载！")
            except Exception as e:
                pytest.fail(f"蓝海关键词游戏分组查找失败：发生未知错误 {e}")

            try:
                first_keyword_checkbox = self.page.locator(
                    CampaignPageToutiaoLocators.LANHAI_FIRST_KEYWORD.format(game=game)
                ).first
                first_keyword_checkbox.check(timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail(f"选择蓝海关键词失败：游戏 '{game}' 分组内未找到或无法点击第一个复选框")
            except Exception as e:
                pytest.fail(f"选择蓝海关键词失败：发生未知错误 {e}")

            try:
                self.page.get_by_role("button", name="确定").click()
            except PlaywrightTimeoutError:
                pytest.fail("蓝海关键词选择失败：未找到或无法点击『确定』按钮")
            except Exception as e:
                pytest.fail(f"蓝海关键词选择失败：发生未知错误 {e}")

        # 自定义关键词
        auto_key = self.page.locator(CampaignPageToutiaoLocators.CUSTOM_KEY)
        if auto_key.is_visible():
            try:
                auto_key.click(timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail("自定义关键词选择失败：未找到或无法点击『选择』按钮")
            except Exception as e:
                pytest.fail(f"自定义关键词选择失败：发生未知错误 {e}")

            try:
                self.page.locator(CampaignPageToutiaoLocators.CUSTOM_KEYWORD_TITLE).wait_for(
                    state="visible", timeout=5000
                )
            except PlaywrightTimeoutError:
                pytest.fail("自定义关键词抽屉未出现：请检查页面加载")
            except Exception as e:
                pytest.fail(f"自定义关键词抽屉等待失败：发生未知错误 {e}")

            try:
                keyword_input = self.page.locator(CampaignPageToutiaoLocators.CUSTOM_KEYWORD_INPUT)
                keyword_input.fill("测试")
            except PlaywrightTimeoutError:
                pytest.fail("自定义关键词输入失败：未找到输入框")
            except Exception as e:
                pytest.fail(f"自定义关键词输入失败：发生未知错误 {e}")

            try:
                self.page.locator(CampaignPageToutiaoLocators.CUSTOM_KEYWORD_QUERY).click(timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail("自定义关键词查询失败：未找到或无法点击查询按钮")
            except Exception as e:
                pytest.fail(f"自定义关键词查询失败：发生未知错误 {e}")

            try:
                self.page.locator(CampaignPageToutiaoLocators.CUSTOM_KEYWORD_ADD).first.click(timeout=10000)
            except PlaywrightTimeoutError:
                pytest.fail("自定义关键词添加失败：未找到或无法点击添加按钮")
            except Exception as e:
                pytest.fail(f"自定义关键词添加失败：发生未知错误 {e}")

            try:
                self.page.get_by_role("button", name="确定").click()
            except PlaywrightTimeoutError:
                pytest.fail("自定义关键词确认失败：未找到或无法点击确定按钮")
            except Exception as e:
                pytest.fail(f"自定义关键词确认失败：发生未知错误 {e}")

        # 蓝海流量包
        lanhai_bag_button = self.page.locator(CampaignPageToutiaoLocators.LANHAI_BAG)
        if lanhai_bag_button.is_visible():
            try:
                lanhai_bag_button.click(timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail("蓝海流量包入口点击失败：未找到或无法点击『选择』按钮")
            except Exception as e:
                pytest.fail(f"蓝海流量包入口点击失败：发生未知错误 {e}")

            try:
                self.page.locator(CampaignPageToutiaoLocators.LANHAI_BAG_TITLE).wait_for(
                    state="visible", timeout=5000
                )
            except PlaywrightTimeoutError:
                pytest.fail("蓝海流量包抽屉未出现：请检查页面加载")
            except Exception as e:
                pytest.fail(f"蓝海流量包抽屉等待失败：发生未知错误 {e}")

            try:
                # 填写输入框并回车
                input_locator = self.page.locator(
                    "//div[@class='search-input']//input[@placeholder='请输入']"
                )
                input_locator.fill(game)
                input_locator.press("Enter")
            except PlaywrightTimeoutError:
                pytest.fail("蓝海流量包搜索输入框操作超时：未找到或无法操作输入框")
            except Exception as e:
                pytest.fail(f"蓝海流量包搜索输入框操作失败：发生未知错误 {e}")

            try:
                self.page.locator(
                    CampaignPageToutiaoLocators.LANHAI_BAG_ROW_RADIO.format(game=game)
                ).first.click(timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail(f"蓝海流量包选择失败：未找到游戏『{game}』的单选框")
            except Exception as e:
                pytest.fail(f"蓝海流量包选择失败：发生未知错误 {e}")

            try:
                self.page.get_by_role("button", name="确定").click()
            except PlaywrightTimeoutError:
                pytest.fail("蓝海流量包确认失败：未找到或无法点击『确定』按钮")
            except Exception as e:
                pytest.fail(f"蓝海流量包确认失败：发生未知错误 {e}")

    def set_account(self, account):
        """1.2 选择投放账户"""
        # 点击“添加账户”按钮
        try:
            self.page.locator(CampaignPageToutiaoLocators.ACCOUNT_ADD).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail("投放账户选择失败：未找到或无法点击『添加账户』按钮")
        except Exception as e:
            pytest.fail(f"投放账户选择失败：发生未知错误 {e}")

        # 输入账户
        try:
            self.page.locator(CampaignPageToutiaoLocators.ACCOUNT_FILL_NEW).fill(account, timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail(f"投放账户输入失败：未找到输入框或无法输入账户 '{account}'")
        except Exception as e:
            pytest.fail(f"投放账户输入失败：发生未知错误 {e}")

        # 按 Enter 搜索账户
        try:
            # TODO 这里搜索完有时候会回退，导致搜索不成功，有点奇怪，为什么会瞬间回退到搜索前的状态呢？
            self.page.locator(CampaignPageToutiaoLocators.ACCOUNT_FILL_NEW).press("Enter")
        except PlaywrightTimeoutError:
            pytest.fail(f"投放账户输入后按 Enter 失败：未找到输入框或无法操作账户 '{account}'")
        except Exception as e:
            pytest.fail(f"投放账户输入后按 Enter 失败：发生未知错误 {e}")

        # 等待账号 ID 出现
        try:
            self.page.locator(CampaignPageToutiaoLocators.ACCOUNT_ID.format(account=account)).wait_for(
                state="visible", timeout=10000
            )
        except PlaywrightTimeoutError:
            pytest.fail(f"账号ID {account} 在表格中未出现")
        except Exception as e:
            pytest.fail(f"等待账号ID {account} 出现失败：发生未知错误 {e}")

        # 勾选搜索结果中的第一个账号
        try:
            self.page.locator(CampaignPageToutiaoLocators.ACCOUNT_ID_SELECTED.format(account=account)).click(
                timeout=5000
            )
        except PlaywrightTimeoutError:
            pytest.fail(f"无法选择账号ID {account} 的复选按钮")
        except Exception as e:
            pytest.fail(f"选择账号ID {account} 复选按钮失败：发生未知错误 {e}")

        # 点击确认 -> 确定
        try:
            self.page.get_by_role("button", name="确定").click()
        except PlaywrightTimeoutError:
            pytest.fail("添加投放账户失败：未找到或无法点击『确定』按钮")
        except Exception as e:
            pytest.fail(f"添加投放账户失败：发生未知错误 {e}")

    def set_content_and_target(self, app_type, ad_type, delivery_mode, star_task=None):
        """3.投放内容与目标【应用类型、推广应用、转化目标】"""
        try:
            self.page.locator(CampaignPageToutiaoLocators.LIST_CONTENT_TARGET).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail("投放内容与目标选择失败：未找到或无法点击『投放内容与目标』按钮")
        except Exception as e:
            pytest.fail(f"投放内容与目标选择失败：发生未知错误 {e}")

        # 选择关联星广联投任务 【选择原则：固定选择一个任务】
        # [营销场景十一 选择该字段，会影响后续广告/创意设置]
        if star_task:
            # 点击关联星广联投任务选择按钮
            try:
                self.page.locator(CampaignPageToutiaoLocators.STAR_TASK_SELECTOR).click(timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail("星广联投任务选择失败：未找到或无法点击『关联星广联投任务』按钮")
            except Exception as e:
                pytest.fail(f"星广联投任务选择失败：发生未知错误 {e}")

            try:
                self.page.locator(
                    CampaignPageToutiaoLocators.STAR_TASK_INPUT
                ).fill("战火勋章", timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail("星广联投任务输入失败：未找到输入框或无法输入任务名称")
            except Exception as e:
                pytest.fail(f"星广联投任务输入失败：发生未知错误 {e}")

            try:
                self.page.locator(
                    CampaignPageToutiaoLocators.STAR_TASK_INPUT
                ).press("Enter", timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail("星广联投任务输入失败：无法在输入框内按下 Enter")
            except Exception as e:
                pytest.fail(f"星广联投任务输入失败：发生未知错误 {e}")

            # Element Plus（ep 前缀）这种 UI 框架的“假输入控件”机制:
            # ep-radio__original → 真实的 input，隐藏，不可点
            # ep-radio__inner → UI 展示层，可见，可点（推荐）
            try:
                # 星广联投任务选择匹配战火勋章的第一个
                self.page.locator(CampaignPageToutiaoLocators.STAR_TASK_CHECKBOX).first.click(timeout=10000)
            except PlaywrightTimeoutError:
                pytest.fail(f"星广联投任务选择失败：未找到或无法点击{CampaignPageToutiaoLocators.STAR_TASK_CHECKBOX}复选框")
            except Exception as e:
                pytest.fail(f"星广联投任务选择失败：发生未知错误 {e}")

            try:
                self.page.get_by_role("button", name="确定").click(timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail("星广联投任务确认失败：未找到或无法点击『确定』按钮")
            except Exception as e:
                pytest.fail(f"星广联投任务确认失败：发生未知错误 {e}")

        # 选择应用类型
        try:
            self.page.locator(CampaignPageToutiaoLocators.APP_TYPE_SELECTED.format(app_type=app_type)).click(
                timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail(f"应用类型选择失败：未找到或无法点击应用类型 '{app_type}'")
        except Exception as e:
            pytest.fail(f"应用类型选择失败：发生未知错误 {e}")

        # 选择推广应用【todo优化：这里会有默认值，也可以不进行操作】
        try:
            self.page.locator(CampaignPageToutiaoLocators.APP_SELECTOR_BOX_NEW).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail("推广应用选择失败：未找到或无法点击推广应用选择框")
        except Exception as e:
            pytest.fail(f"推广应用选择失败：发生未知错误 {e}")

        # 【选择原则：优先选择中国-安卓（不含同名包）的第一个；若无，则选择带有“中国-安卓”的第一个】
        # 这里这样定位比较方便，就不修改了。时间有限，后面的逻辑也不动了，仅加了异常处理和解决了一些定位问题 2025.09.24 by lucien
        if app_type == "安卓应用":
            try:
                # 先定位所有包含 "中国-安卓" 文本的元素，然后过滤掉包含 "同名包" 文本的元素，取第一个进行点击
                target_elements = self.page.get_by_text("中国-安卓", exact=False).filter(has_not_text="同名包")
                if target_elements.count() > 0:
                    target_elements.first.click()
                else:
                    # 如果过滤后没有符合条件的元素，就选第一个包含 "中国-安卓" 文本的元素（即便包含同名包，保证有选项可点）
                    self.page.get_by_text("中国-安卓", exact=False).first.click()
            except PlaywrightTimeoutError:
                pytest.fail("推广应用选择失败：未找到或无法点击『中国-安卓』选项")
            except Exception as e:
                pytest.fail(f"推广应用选择失败：发生未知错误 {e}")
        elif app_type == "苹果应用":
            try:
                # 匹配所有可能的 iOS/苹果 选项
                self.page.get_by_role("option", name=re.compile(r".*中国-(ios|苹果|iOS|IOS).*")).first.click(
                    timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail("推广应用选择失败：未找到或无法点击『中国-iOS/苹果』选项")
            except Exception as e:
                pytest.fail(f"推广应用选择失败：发生未知错误 {e}")

        # 选择转化目标 【选择原则：在创建广告的几个账号的不同场景下都新建test转化目标，激活：test_zst(sdk)/test_i(api)；付费-7日roi：test_zst_roi】
        try:
            conversion_aim = self.page.get_by_label("转化目标").locator("div").filter(
                has_text="未选择转化目标 选择"
            ).nth(1)
        except Exception as e:
            pytest.fail(f"转化目标定位失败：发生未知错误 {e}")
        # 转化目标区域
        if conversion_aim.is_visible():
            try:
                conversion_aim_selector = self.page.get_by_label("转化目标").get_by_text("选择", exact=True)
                conversion_aim_selector.click(timeout=5000)
                self.page.wait_for_load_state("networkidle", timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail("转化目标选择失败：未找到或无法点击")
            except Exception as e:
                pytest.fail(f"转化目标选择失败：发生未知错误 {e}")

            # 特定营销场景，需要先更改选择弹窗中的筛选器再选择转化目标
            if ad_type == "通投广告" and delivery_mode == "自动投放":
                # 更改筛选器内容为：转化目标：付费、深度转化目标：付费ROI-7日
                try:
                    self.page.get_by_text("转化目标:", exact=True).click(timeout=5000)
                    self.page.get_by_role("option", name="付费").click(timeout=5000)
                except PlaywrightTimeoutError:
                    pytest.fail("转化目标筛选失败：未找到转化目标筛选器或无法点击付费选项")
                except Exception as e:
                    pytest.fail(f"转化目标筛选失败：发生未知错误 {e}")

                try:
                    self.page.get_by_text("深度转化目标:").click(timeout=5000)
                    self.page.get_by_role("option", name="付费ROI-7日").click(timeout=5000)
                except PlaywrightTimeoutError:
                    pytest.fail("转化目标筛选失败：未找到深度转化目标筛选器或无法点击付费ROI-7日选项")
                except Exception as e:
                    pytest.fail(f"转化目标筛选失败：发生未知错误 {e}")

                # 选择转化目标：包含test_zst_roi
                try:
                    self.page.get_by_role("row", name=re.compile(r".*test_zst_roi.*", re.IGNORECASE)).locator(
                        "label").click(timeout=5000)
                except PlaywrightTimeoutError:
                    pytest.fail("转化目标选择失败：未找到或无法选择 test_zst_roi")
                except Exception as e:
                    pytest.fail(f"转化目标选择失败：发生未知错误 {e}")

                try:
                    self.page.get_by_role("button", name="确定").click(timeout=5000)
                except PlaywrightTimeoutError:
                    pytest.fail("转化目标确认失败：未找到或无法点击『确定』按钮")
                except Exception as e:
                    pytest.fail(f"转化目标确认失败：发生未知错误 {e}")

                # 选择新出现的字段：深度转化方式：每次付费+7日roi【选择该值，后续竞价策略选择新增值：最大转化】
                # 判断深度转化方式字段是否存在
                if self.page.locator(CampaignPageToutiaoLocators.DEEP_CONVERSION_LABEL).is_visible():
                    # 选择深度转化方式：每次付费+7日roi
                    try:
                        self.page.locator(CampaignPageToutiaoLocators.DEEP_CONVERSION_WAY).click(timeout=5000)
                    except PlaywrightTimeoutError:
                        pytest.fail("深度转化方式选择失败：未找到或无法点击『每次付费+7日roi』选项")
                    except Exception as e:
                        pytest.fail(f"深度转化方式选择失败：发生未知错误 {e}")
            else:
                # 如果在搜索前可见“test_zst”，则直接点击；否则再进行搜索选择
                if self.page.get_by_text("test_zst").is_visible():
                    try:
                        self.page.get_by_text("test_zst").click(timeout=5000)
                    except PlaywrightTimeoutError:
                        pytest.fail("转化目标中点击文本『test_zst』失败：未找到或无法点击")
                    except Exception as e:
                        pytest.fail(f"转化目标中点击文本『test_zst』失败：发生未知错误 {e}")

                    try:
                        self.page.get_by_role("row", name=re.compile(r"^test_zst.*")).locator("label").click(
                            timeout=5000)
                    except PlaywrightTimeoutError:
                        pytest.fail("转化目标中点击行内『test_zst』对应的 圆圈选择按钮 失败：未找到或无法点击")
                    except Exception as e:
                        pytest.fail(f"转化目标中点击行内『test_zst』对应的 圆圈选择按钮 失败：发生未知错误 {e}")

                else:
                    try:
                        self.page.locator(CampaignPageToutiaoLocators.CONVERSION_SEARCH_INPUT_NEW).fill("test_zst",
                                                                                                        timeout=5000)
                    except PlaywrightTimeoutError:
                        pytest.fail("在转化目标搜索输入框中填充 'test_zst' 失败：未找到或无法输入")
                    except Exception as e:
                        pytest.fail(f"在转化目标搜索输入框中填充 'test_zst' 失败：发生未知错误 {e}")

                    try:
                        self.page.locator(CampaignPageToutiaoLocators.CONVERSION_SEARCH_INPUT_NEW).press("Enter",
                                                                                                         timeout=5000)
                    except PlaywrightTimeoutError:
                        pytest.fail("在转化目标搜索输入框按 Enter 键失败：未找到或无法操作")
                    except Exception as e:
                        pytest.fail(f"在转化目标搜索输入框按 Enter 键失败：发生未知错误 {e}")

                    try:
                        self.page.get_by_role("dialog").locator("tbody").get_by_role("cell").filter(
                            has_text=re.compile(r"^$")
                        ).locator("span").click(timeout=5000)
                    except PlaywrightTimeoutError:
                        pytest.fail("点击转化目标搜索结果中第一个 span选择按钮 失败：未找到或无法点击")
                    except Exception as e:
                        pytest.fail(f"点击转化目标搜索结果中第一个 span选择按钮 失败：发生未知错误 {e}")

                try:
                    self.page.get_by_role("button", name="确定").click(timeout=5000)
                except PlaywrightTimeoutError:
                    pytest.fail("点击转化目标确认按钮失败：未找到或无法点击『确定』按钮")
                except Exception as e:
                    pytest.fail(f"点击转化目标确认按钮失败：发生未知错误 {e}")

    def set_placement(self, position):
        """4. 投放版位【投放位置、媒体选择】"""
        # 点击版位列表
        try:
            self.page.locator(CampaignPageToutiaoLocators.LIST_PLACEMENT).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail("投放版位选择失败：未找到或无法点击版位列表")
        except Exception as e:
            pytest.fail(f"投放版位选择失败：发生未知错误 {e}")

        # 选择投放位置
        try:
            self.page.locator(CampaignPageToutiaoLocators.LIST_PLACEMENT_SELECTED.format(position=position)).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail(f"投放位置选择失败：未找到或无法点击指定投放位置{position}")
        except Exception as e:
            pytest.fail(f"投放位置选择失败：发生未知错误 {e}")
        # 【注】首选媒体，默认全选，不需要操作；若需要指定版位，在操作时需要先去掉默认勾选，再勾选指定版位

    def set_targeting(self):
        """5.用户定向【定向盒子、过滤已转化、过滤时间】"""
        try:
            self.page.locator(CampaignPageToutiaoLocators.LIST_USER_TARGETING).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail("用户定向包列表点击失败：未找到或无法点击『用户定向包』")
        except Exception as e:
            pytest.fail(f"用户定向包列表点击失败：发生未知错误 {e}")

        try:
            self.page.locator(CampaignPageToutiaoLocators.TARGETING_PACK_BUTTON).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail("添加定向包按钮点击失败：未找到或无法点击『添加定向包』按钮")
        except Exception as e:
            pytest.fail(f"添加定向包按钮点击失败：发生未知错误 {e}")

        try:
            # 选择用户定向包【选择原则：在关联游戏下创建定向包，命名为test_zst】
            # 如果在搜索前可见“test_zst”，则直接选择；否则再进行搜索选择
            user_target_selector = self.page.get_by_role("cell", name=re.compile(r".*test_zst.*", re.IGNORECASE))
        except PlaywrightTimeoutError:
            pytest.fail("用户定向包选择失败：未找到或无法定位包含 'test_zst' 的单元格")
        except Exception as e:
            pytest.fail(f"用户定向包选择失败：发生未知错误 {e}")

        if user_target_selector.is_visible():
            user_target_selector.first.click()
        else:
            try:
                self.page.get_by_role("textbox", name="请输入", exact=True).click()
            except PlaywrightTimeoutError:
                pytest.fail("用户定向包输入框点击失败：未找到或无法点击输入框")
            except Exception as e:
                pytest.fail(f"用户定向包输入框点击失败：发生未知错误 {e}")

            try:
                self.page.get_by_role("textbox", name="请输入", exact=True).fill("test_zst")
            except PlaywrightTimeoutError:
                pytest.fail("用户定向包输入框填充失败：未找到输入框或无法输入 'test_zst'")
            except Exception as e:
                pytest.fail(f"用户定向包输入框填充失败：发生未知错误 {e}")

            try:
                self.page.get_by_role("textbox", name="请输入", exact=True).press("Enter")
            except PlaywrightTimeoutError:
                pytest.fail("用户定向包输入框按下 Enter 失败：未找到输入框或无法按下 Enter")
            except Exception as e:
                pytest.fail(f"用户定向包输入框按下 Enter 失败：发生未知错误 {e}")

            try:
                self.page.get_by_role("row", name=re.compile("test")).locator("div").first.click()  # 选择匹配到的第一个
            except PlaywrightTimeoutError:
                pytest.fail("用户定向包选择失败：未找到匹配行或无法点击第一个选项")
            except Exception as e:
                pytest.fail(f"用户定向包选择失败：发生未知错误 {e}")

        try:
            self.page.get_by_role("button", name="确定").click()
        except PlaywrightTimeoutError:
            pytest.fail("用户定向包确认失败：未找到或无法点击『确定』按钮")
        except Exception as e:
            pytest.fail(f"用户定向包确认失败：发生未知错误 {e}")

        try:
            self.page.mouse.wheel(0, 200)
        except Exception as e:
            pytest.fail(f"页面滚动失败：发生未知错误 {e}")

        try:
            # 【注】过滤已转化、过滤时间可以设置为默认值、固定、不进行操作【不影响主流程】
            self.page.get_by_label("过滤已转化").get_by_text("不限").click()  # 固定选择过滤已转化：不限
        except PlaywrightTimeoutError:
            pytest.fail("过滤已转化选择失败：未找到或无法点击『不限』选项")
        except Exception as e:
            pytest.fail(f"过滤已转化选择失败：发生未知错误 {e}")

    # select_douyin_account方法供set_creative（6.广告创意/广告设置）使用
    def select_douyin_account(self, game, material_type=None):
        douyin_selector_button = self.page.locator("//span[text()='未选择抖音号']//..//..//..//button")
        if douyin_selector_button.is_visible():
            try:
                douyin_selector_button.click(timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail("抖音号选择失败：无法点击『未选择抖音号』按钮")
            except Exception as e:
                pytest.fail(f"抖音号选择失败：发生未知错误 {e}")

            try:
                self.page.wait_for_load_state("networkidle")
            except PlaywrightTimeoutError:
                pytest.fail("等待页面加载完成失败")
            except Exception as e:
                pytest.fail(f"等待页面加载完成失败：发生未知错误 {e}")

            name = "剑与远征" if game == "剑与远征：启程" else game

            game_douyin_account = self.page.get_by_role("cell", name=name).first
            if game_douyin_account.is_visible():
                try:
                    game_douyin_account.click(timeout=5000)
                except PlaywrightTimeoutError:
                    pytest.fail(f"选择抖音号失败：未找到游戏 '{name}' 的抖音号")
                except Exception as e:
                    pytest.fail(f"选择抖音号失败：发生未知错误 {e}")

                try:
                    if material_type == "直播素材":
                        self.page.get_by_role("button", name="确定").click(timeout=5000)
                    else:
                        self.page.get_by_role("button", name="确定").nth(1).click(timeout=5000)
                except PlaywrightTimeoutError:
                    pytest.fail("抖音号确认失败：未找到或无法点击『确定』按钮")
                except Exception as e:
                    pytest.fail(f"抖音号确认失败：发生未知错误 {e}")
            else:
                try:
                    self.page.locator(CampaignPageToutiaoLocators.DOUYIN_SEARCH_INPUT_NEW).fill(name)
                except PlaywrightTimeoutError:
                    pytest.fail(f"抖音号搜索输入失败：未找到搜索输入框")
                except Exception as e:
                    pytest.fail(f"抖音号搜索输入失败：发生未知错误 {e}")

                try:
                    self.page.locator(CampaignPageToutiaoLocators.DOUYIN_SEARCH_INPUT_NEW).press("Enter")
                except PlaywrightTimeoutError:
                    pytest.fail("抖音号搜索回车失败：无法触发搜索")
                except Exception as e:
                    pytest.fail(f"抖音号搜索回车失败：发生未知错误 {e}")

                try:
                    self.page.get_by_role("cell", name=re.compile(r".*" + name + ".*")).first.click()
                except PlaywrightTimeoutError:
                    pytest.fail(f"选择搜索结果失败：未找到游戏 '{name}' 的抖音号")
                except Exception as e:
                    pytest.fail(f"选择搜索结果失败：发生未知错误 {e}")

                try:
                    if material_type == "直播素材":
                        self.page.get_by_role("button", name="确定").click()
                    else:
                        self.page.get_by_role("button", name="确定").nth(1).click()
                except PlaywrightTimeoutError:
                    pytest.fail("抖音号搜索确认失败：未找到或无法点击『确定』按钮")
                except Exception as e:
                    pytest.fail(f"抖音号搜索确认失败：发生未知错误 {e}")

    # select_material方法供set_creative（6.广告创意/广告设置）使用
    def select_material(self, count: int):
        # 定位所有包含素材复选框的容器/视觉元素
        try:
            first_grid_checkbox = self.page.locator("div.grid > div.cursor-pointer:has(label.ep-checkbox)").first
        except PlaywrightTimeoutError:
            pytest.fail("定位素材复选框容器失败：未找到div.grid > div.cursor-pointer")
        except Exception as e:
            pytest.fail(f"定位素材复选框容器失败：发生未知错误 {e}")

        try:
            if first_grid_checkbox.is_visible():
                checkboxes = self.page.locator("div.grid > div.cursor-pointer:has(label.ep-checkbox)")
            else:
                checkboxes = self.page.locator("table.ep-table__body > tbody > tr.ep-table__row:has(label.ep-checkbox)")
        except PlaywrightTimeoutError:
            pytest.fail("获取素材复选框集合失败：未找到匹配元素")
        except Exception as e:
            pytest.fail(f"获取素材复选框集合失败：发生未知错误 {e}")

        # 验证数量并选择
        try:
            total_count = checkboxes.count()
        except Exception as e:
            pytest.fail(f"获取素材数量失败：发生未知错误 {e}")

        if total_count < count:
            print(f"素材不足，需{count}个，实际{total_count}个")
            count = total_count
            print(f"实际选择{count}个素材")

        if total_count > 1:  # 页面有一个选择全部的固定checkbox
            for i in range(count):
                try:
                    # 定位第i个复选框的label/span,触发勾选
                    checkbox_label = checkboxes.nth(i + 1).locator("span.ep-checkbox__input")
                    checkbox_label.click(timeout=10000)
                except PlaywrightTimeoutError:
                    pytest.fail(f"第{i + 1}个素材勾选失败：未找到或无法点击复选框")
                except Exception as e:
                    pytest.fail(f"第{i + 1}个素材勾选失败：发生未知错误 {e}")
        else:
            pass  # 直接跳过

    # set_material_count供set_creative（6.广告创意/广告设置）使用
    def set_material_count(self, materials):
        """
        设置素材数量

        :param materials: 列表，每个元素为 (locator, count)
            locator: 素材类型按钮的定位器
            count: 对应素材类型的数量
        """
        for material in materials:
            locator, count = material
            try:
                # 定位素材类型按钮（取第2个匹配的元素，nth从0开始计数）
                span_locator = self.page.locator(locator).nth(1)
                try:
                    span_locator.click(timeout=10000)  # 点击素材类型按钮
                except PlaywrightTimeoutError:
                    pytest.fail(f"素材类型按钮 '{locator}' 未找到或无法点击")
                except Exception as e:
                    pytest.fail(f"点击素材类型按钮 '{locator}' 失败：{e}")

                # 定位输入框（素材数量输入框在按钮的兄弟节点input）
                try:
                    input_locator = span_locator.locator("../following-sibling::input")
                    input_locator.fill(str(count))  # 填写数量
                except PlaywrightTimeoutError:
                    pytest.fail(f"素材数量输入框未找到或无法输入数量 '{count}'")
                except Exception as e:
                    pytest.fail(f"填写素材数量失败：{e}")

            except Exception as e:
                pytest.fail(f"设置素材数量流程失败：{e}")

    # select_materials供set_creative（6.广告创意/广告设置）使用
    # 这里删除了dap-ad-autotest中的select_materials用到的fill_search函数，该函数仅select_materials用了一次，没有复用性
    def select_materials(self, materials):
        """
        选择素材

        :param materials: 列表，每个元素为 (button, search_keyword, count)
            button: 点击素材类型按钮的定位器
            search_keyword: 搜索关键词（为空则不搜索）
            count: 选择素材的数量
        """
        for material in materials:
            button, search_keyword, count = material
            try:
                # 点击素材类型按钮，打开素材选择面板
                try:
                    self.page.locator(button).nth(0).click(timeout=10000)
                except PlaywrightTimeoutError:
                    pytest.fail(f"素材类型按钮 '{button}' 未找到或无法点击")
                except Exception as e:
                    pytest.fail(f"点击素材类型按钮 '{button}' 失败：{e}")

                # 等待素材面板加载完成
                try:
                    loading = self.page.locator(".ep-loading-spinner")
                    loading.wait_for(state="detached", timeout=10000)
                except PlaywrightTimeoutError:
                    pytest.fail("素材加载超时，loading spinner未消失")
                except Exception as e:
                    pytest.fail(f"等待素材加载完成失败：{e}")

                # 如果指定了搜索关键词，则在搜索框输入并回车
                if search_keyword != "":
                    try:
                        search_box = self.page.get_by_role(
                            "textbox",
                            name=re.compile(
                                r"请输入搜索内容|请输入音乐名称进行搜索|请输入文案进行搜索|请输入标题关键词搜索")
                        )  # 获取搜索框
                        try:
                            search_box.click(timeout=10000)  # 点击搜索框
                            search_box.fill(search_keyword)  # 填写搜索内容
                            search_box.press("Enter")  # 按下 Enter 键
                        except PlaywrightTimeoutError:
                            pytest.fail(f"搜索框操作失败：无法输入关键词 '{search_keyword}'")
                        except Exception as e:
                            pytest.fail(f"搜索框输入关键词 '{search_keyword}' 失败：{e}")
                    except Exception as e:
                        pytest.fail(f"定位搜索框失败：{e}")

                # 调用 select_material 方法选择素材
                try:
                    self.select_material(count)
                except Exception as e:
                    pytest.fail(f"选择素材数量 '{count}' 失败：{e}")

            except Exception as e:
                pytest.fail(f"select_materials流程失败：{e}")

    def set_creative(self, native_ad=None, game=None, material_type=None, land_page=None,
                     text_summary=None, star_task=None, dy_material=None):
        """6.广告创意/广告设置（根据场景选择原生广告或素材类型）【原生广告投放、创意盒子/素材组、产品名称、产品主图、产品卖点、行动号召】"""
        try:
            self.page.locator(CampaignPageToutiaoLocators.LIST_AD_SET_NEW).click(timeout=5000)
        except PlaywrightTimeoutError:
            pytest.fail("侧边栏广告设置点击失败：未找到或无法点击广告设置")
        except Exception as e:
            pytest.fail(f"侧边栏广告设置点击失败：发生未知错误 {e}")

        # 【注】：短视频+图文场景有原生广告开关；直播场景有素材类型选择
        # 直播-直播素材：在外面选择抖音号；直播-广告素材/其他：在素材组中选择抖音号

        # 选择原生广告投放
        if native_ad:
            try:
                self.page.locator(CampaignPageToutiaoLocators.AD_MATERIAL_LABEL_SELECTOR_NEW).filter(
                    has_text=native_ad
                ).click(timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail(f"选择原生广告投放选择失败：未找到或无法点击包含文原生广告投放选项")
            except Exception as e:
                pytest.fail(f"选择原生广告投放选择失败：发生未知错误 {e}")

        if material_type:
            # 选择素材类型（直播场景下，素材形式中有直播素材和广告素材两种选择）
            try:
                self.page.locator(CampaignPageToutiaoLocators.MATERIAL_TYPE_SELECTED.
                                  format(material_type=material_type)).click(timeout=5000)  # 选择素材类型下拉框
            except PlaywrightTimeoutError:
                pytest.fail("素材类型选择失败：未找到或无法点击素材类型下拉框")
            except Exception as e:
                pytest.fail(f"素材类型选择失败：发生未知错误 {e}")

            # 场景七&九：直播-直播素材  不需要选择素材组,在外部选择抖音号
            if material_type == "直播素材":
                try:
                    self.select_douyin_account(game, material_type)  # 调用选择抖音号
                except Exception as e:
                    pytest.fail(f"抖音号选择失败：发生未知错误 {e}")

            # 素材组外选择蓝海关键词【直播-搜索-常规 可见】
            # 【注】如果是搜索广告-常规投放，则需要选择蓝海关键词【直播的蓝海关键词在外面,短视频+图文的在素材组内】
            lanhai_key_selector_set = self.page.locator(
                CampaignPageToutiaoLocators.LANHAI_KEY_SELECTOR_SET)  # 定位蓝海关键词选择器

            if lanhai_key_selector_set.is_visible():  # 判断蓝海关键词是否可见
                try:
                    lanhai_key_selector_set.click(timeout=5000)  # 点击蓝海关键词选择器
                except PlaywrightTimeoutError:
                    pytest.fail("蓝海关键词选择入口点击失败：无法点击")
                except Exception as e:
                    pytest.fail(f"蓝海关键词选择入口点击失败：发生未知错误 {e}")

                try:
                    self.page.get_by_text("预估消耗（元）").nth(0).click()  # 选择第一个蓝海关键词
                except PlaywrightTimeoutError:
                    pytest.fail("蓝海关键词第一个选项点击失败：未找到或无法点击")
                except Exception as e:
                    pytest.fail(f"蓝海关键词第一个选项点击失败：发生未知错误 {e}")

        material_button = self.page.locator(CampaignPageToutiaoLocators.MATERIAL_SELECT_BUTTON)  # 定位素材选择按钮

        # 场景七&九：直播-直播素材时，该按钮不可见，不需要选择素材组
        if material_button.is_visible():
            # 点击 批量选择素材 按钮
            try:
                material_button.click(timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail("无法点击批量选择素材按钮")
            except Exception as e:
                pytest.fail(f"点击 批量选择素材 按钮出错{e}")

            # 1.如果开启原生广告或选择广告素材，则可以选dap+抖音素材（copy场景数据，如果设置了ad_material的值就选择抖音素材，未设置则选择dap素材）；
            # 2.如果选择了星广联投，则只能选择抖音素材（抖音视频）；
            # 3.否则，只能选择dap素材
            # 只可选择抖音素材(抖音视频)
            if star_task:
                # 1.素材组设置
                try:
                    materials_to_set = [
                        (CampaignPageToutiaoLocators.DOUYIN_VIDEO, 5),  # 抖音视频
                    ]
                    self.set_material_count(materials_to_set)
                except Exception as e:
                    pytest.fail(f"设置素材组失败：{e}")

                # 2.选择投放抖音号[可以不选择指定抖音号，默认选择全部抖音号]
                # self.select_douyin_account(game,material_type)

                # 3.选择素材
                try:
                    materials_to_select = [
                        (CampaignPageToutiaoLocators.DOUYIN_VIDEO_BUTTON, "", 1),  # 抖音视频
                    ]
                    self.select_materials(materials_to_select)
                except Exception as e:
                    pytest.fail(f"选择素材失败：{e}")

                try:
                    self.page.get_by_role("button", name="确定").click(timeout=5000)  # 点击 确定 按钮
                except PlaywrightTimeoutError:
                    pytest.fail("点击‘确定’按钮失败：未找到或无法点击")
                except Exception as e:
                    pytest.fail(f"点击‘确定’按钮失败：{e}")

                # 注：星广联投：先选择素材、再选择文案
                # # 4.选择文案
                # self.page.locator("button:has-text('文案库')").click()  #点击文案库 按钮
                # self.page.get_by_role("row", name=re.compile("^测试")).first.locator("span").nth(1).click()
                # # self.page.locator("table.ep-table__body tbody tr.ep-table__row:has-text('测试数据勿用821')")  #固定选择一条文案内容
                # self.page.get_by_role("button", name="确定").click()

            # if native_ad=="开启" or material_type=="广告素材": # 可以选择dap/抖音素材
            # 选择抖音素材（抖音视频+抖音图文）
            elif dy_material:
                # 1.素材组设置
                # materials_to_set = [
                #     (CampaignPageToutiaoLocators.TEXT, 2),  # 文案
                #     (CampaignPageToutiaoLocators.DOUYIN_VIDEO, 5),  # 抖音视频
                #     (CampaignPageToutiaoLocators.DOUYIN_IMG, 5),    #抖音图文
                # ]
                try:
                    materials_to_set = [
                        (CampaignPageToutiaoLocators.DOUYIN_VIDEO, 5),  # 抖音视频
                        (CampaignPageToutiaoLocators.DOUYIN_IMG, 5),  # 抖音图文
                    ]
                    self.set_material_count(materials_to_set)
                except Exception as e:
                    pytest.fail(f"设置素材组失败：{e}")

                # 2.选择投放抖音号
                try:
                    self.select_douyin_account(game, material_type)
                except Exception as e:
                    pytest.fail(f"选择投放抖音号失败：{e}")

                # 3.选择素材
                # materials_to_select = [
                #     (CampaignPageToutiaoLocators.TEXTBUTTON, "", 2),  # 文案库
                #     (CampaignPageToutiaoLocators.DOUYIN_VIDEO_BUTTON, "", 1),  # 抖音视频[提供账号下没有抖音视频的素材]
                #     (CampaignPageToutiaoLocators.DOUYIN_IMG_BUTTON, "", 1),  # 抖音图文[提供账号下没有抖音图文的素材]
                #
                # ]
                try:
                    materials_to_select = [
                        (CampaignPageToutiaoLocators.DOUYIN_VIDEO_BUTTON, "", 1),  # 抖音视频[提供账号下没有抖音视频的素材]
                        (CampaignPageToutiaoLocators.DOUYIN_IMG_BUTTON, "", 1),  # 抖音图文[提供账号下没有抖音图文的素材]
                    ]
                    self.select_materials(materials_to_select)
                except Exception as e:
                    pytest.fail(f"选择素材失败：{e}")

                try:
                    confirm_button = self.page.get_by_role("button", name="确定")
                    if confirm_button.count() == 0:
                        self.page.reload()
                        pytest.fail("页面上没有‘确定’按钮 → 该场景失败")
                    else:
                        try:
                            confirm_button.click(timeout=5000)
                        except TimeoutError:
                            self.page.reload()
                            pytest.fail("‘确定’按钮存在，但无法点击 → 该场景失败")
                        except Exception as e:
                            self.page.reload()
                            pytest.fail(f"点击‘确定’按钮失败：{e}")
                except Exception as e:
                    pytest.fail(f"查找‘确定’按钮失败：{e}")

            # 选择dap素材/只可选择dap素材
            else:
                # 1.素材组设置【视频：5，图片：5，图文：2，文案：2】
                try:
                    materials_to_set = [
                        (CampaignPageToutiaoLocators.VIDEO, 5),  # 视频
                        (CampaignPageToutiaoLocators.IMG, 5),  # 图片
                        (CampaignPageToutiaoLocators.GROUPIMG, 2),  # 图文
                        (CampaignPageToutiaoLocators.TEXT, 2)  # 文案
                    ]
                    self.set_material_count(materials_to_set)
                except Exception as e:
                    pytest.fail(f"设置素材组失败：{e}")

                # 补充：如果选择投放抖音号可见，则选择抖音号；即在select_douyin_account种，只有选择投放抖音号可见时，才会进入该函数对应的判断逻辑，否则该函数什么也不会执行
                try:
                    self.select_douyin_account(game, material_type)
                except Exception as e:
                    pytest.fail(f"选择投放抖音号失败：{e}")

                # 2.选择素材【视频：1，图片：3，组图：4，音乐库：2，文案库：2】
                try:
                    materials_to_select = [
                        (CampaignPageToutiaoLocators.VIDEOBUTTON, "测试", 2),  # 视频
                        (CampaignPageToutiaoLocators.IMGBUTTON, "测试", 2),  # 图片
                        (CampaignPageToutiaoLocators.GROUPIMGBUTTON, "测试", 2),  # 组图
                        (CampaignPageToutiaoLocators.MUSICBUTTON, "", 1),  # 音乐库
                        (CampaignPageToutiaoLocators.TEXTBUTTON, "", 1)  # 文案库
                    ]
                    self.select_materials(materials_to_select)
                except Exception as e:
                    pytest.fail(f"选择素材失败：{e}")

                try:
                    self.page.get_by_role("button", name="确定").click()  # 点击 确定 按钮
                except TimeoutError:
                    self.page.reload()
                    pytest.fail("点击‘确定’按钮失败：未找到或无法点击")
                except Exception as e:
                    pytest.fail(f"点击‘确定’按钮失败：{e}")

            # 素材组内选择蓝海关键词【任意选择一个】
            if self.page.locator(CampaignPageToutiaoLocators.LANHAI_KEY_SELECTOR_SET).is_visible():
                try:
                    self.page.locator(CampaignPageToutiaoLocators.LANHAI_KEY_SELECTOR_SET).click(timeout=5000)
                except Exception as e:
                    pytest.fail(f"点击蓝海关键词选择器失败：{e}")

                try:
                    self.page.get_by_text("预估消耗（元）").nth(0).click(timeout=5000)
                except Exception as e:
                    pytest.fail(f"点击‘预估消耗（元）’选项失败：{e}")

        # 营销场景：搜索-极速智投、搜索-常规投放 需要填写文本摘要【选择原则：在摘要库中选择第一条】
        if text_summary:
            try:
                self.page.locator(CampaignPageToutiaoLocators.TEXT_SUMMARY).click(timeout=5000)  # 点击摘要库
            except Exception as e:
                pytest.fail(f"点击摘要库失败：{e}")

            try:
                self.page.get_by_role("row").nth(1).locator("span").nth(1).click(timeout=5000)  # 勾选第一行
            except Exception as e:
                pytest.fail(f"勾选摘要第一行失败：{e}")

            try:
                self.page.get_by_role("button", name="确定").click(timeout=5000)
            except Exception as e:
                pytest.fail(f"点击确定按钮失败：{e}")

            # self.page.get_by_role("group", name="文本摘要*").get_by_role("img").nth(1).click() #[注：点击摘要库添加会自动新增一个框，点击删除按钮]

            # [注：点击摘要库添加会自动新增一个框，点击删除按钮]
            try:
                self.page.locator("//div[@class='clearfix container'][2]/div/div/i").click(timeout=5000)
            except Exception as e:
                pytest.fail(f"点击删除按钮失败：{e}")

        # 应用类型：安卓应用，选择落地页【选择原则：根据游戏名称game固定选择落地页】
        # 例如：
        # 战火勋章，选择：官包-Wgame-真实战场灰-长版 ；
        # 万龙觉醒，选择：万龙觉醒，国风新版本！
        if land_page:
            land_name = ""
            if game == "战火勋章":
                land_name = "官包-Wgame-真实战场灰-长版"
            elif game == "万龙觉醒":
                land_name = "万龙觉醒，国风新版本！"

            try:
                self.page.locator(CampaignPageToutiaoLocators.LAND_PAGE_SELECT_BUTTON_NEW).click(timeout=5000)  # 点击 添加落地页 按钮【新版】
            except Exception as e:
                pytest.fail(f"点击‘添加落地页’按钮失败：{e}")

            try:
                # 先找包含目标文本的单元格，再定位该行的复选框
                checkbox_locator = ((self.page.get_by_text(land_name)
                                    .locator('..')
                                    .locator('preceding-sibling::td'))
                                    .locator('input.ep-checkbox__original'))  # 定位到指定落地页名称所在行的复选框
                checkbox_locator.click(timeout=5000)  # 勾选复选框
            except Exception as e:
                pytest.fail(f"勾选落地页【{land_name}】复选框失败：{e}")

            try:
                self.page.get_by_role("button", name="确定").click(timeout=5000)
            except Exception as e:
                pytest.fail(f"点击‘确定’按钮失败：{e}")

        # 添加鼠标滚动
        try:
            self.page.mouse.wheel(0, 100)
        except Exception as e:
            pytest.fail(f"鼠标滚动失败：{e}")

    def set_budget(self, time, time_period, ad_budget, ad_bid, bidding_strategy=None, daily_budget=None, budget_type=None):
        """7.设置排期与预算"""
        self.page.locator(CampaignPageToutiaoLocators.LIST_SCHEDULE_BUDGET).click(timeout=5000)

        # 竞价策略【选择原则：通投-自动--选择“最大转化”；其他选择默认值，即不操作】
        # 在base_data中设置，bidding_strategy只有“最大转化”，其他场景不操作
        if bidding_strategy:
            try:
                self.page.locator(CampaignPageToutiaoLocators.SCHEDULE_AND_BUDGET_NEW).get_by_text(
                    f"{bidding_strategy}").click(timeout=5000)
            except PlaywrightTimeoutError:
                pytest.fail(f"点击竞价策略‘{bidding_strategy}’超时")
            except Exception as e:
                pytest.fail(f"点击竞价策略‘{bidding_strategy}’失败：{e}")

        # 项目预算
        if budget_type == "不限":
            try:
                self.page.get_by_label("项目预算").get_by_text(f"{budget_type}").click()  # 点击不限
            except PlaywrightTimeoutError:
                pytest.fail(f"点击项目预算：{budget_type}超时，无法点击")
            except Exception as e:
                pytest.fail(f"点击项目预算：{budget_type}出错：{e}")
        elif budget_type == "日预算":
            try:
                self.page.locator(
                    CampaignPageToutiaoLocators.BUDGET_TYPE_SELECTED.format(budget_type)
                ).click()  # 点击日预算
            except PlaywrightTimeoutError:
                pytest.fail(f"点击项目预算：{budget_type}超时，无法点击")
            except Exception as e:
                pytest.fail(f"点击项目预算：{budget_type}出错：{e}")

            try:
                self.page.locator(
                    CampaignPageToutiaoLocators.DAILY_BUDGET_INPUT
                ).fill(str(daily_budget))  # 输入项目预算
            except PlaywrightTimeoutError:
                pytest.fail(f"输入项目预算：{daily_budget} 超时，无法输入")
            except Exception as e:
                pytest.fail(f"输入项目预算：{daily_budget} 出错：{e}")

        # 付费方式 默认只有一个选项，不需要操作
        try:
            self.page.mouse.wheel(0, 50)
        except Exception as e:
            pytest.fail(f"鼠标滚动操作出错：{e}")
        # 广告预算
        if budget_type is None:  # 通投-自动，项目日预算
            try:
                self.page.locator(CampaignPageToutiaoLocators.AD_DAILY_BUDGET_INPUT).fill(str(ad_budget))
            except PlaywrightTimeoutError:
                pytest.fail(f"输入广告日预算：{ad_budget} 超时，无法输入")
            except Exception as e:
                pytest.fail(f"输入广告日预算：{ad_budget} 出错：{e}")
        else:  # 其他场景，广告预算
            try:
                self.page.locator(CampaignPageToutiaoLocators.AD_BUDGET_INPUT).fill(str(ad_budget))
            except PlaywrightTimeoutError:
                pytest.fail(f"输入广告预算：{ad_budget} 超时，无法输入")
            except Exception as e:
                pytest.fail(f"输入广告预算：{ad_budget} 出错：{e}")

        # 广告/项目出价【竞价策略选择最大转化时，不展示出价】
        ad_bid_selector = self.page.locator(CampaignPageToutiaoLocators.AD_BID_INPUT)
        if ad_bid_selector.is_visible():
            try:
                self.page.locator(CampaignPageToutiaoLocators.AD_BID_INPUT).fill(str(ad_bid))
            except PlaywrightTimeoutError:
                pytest.fail(f"输入广告出价：{ad_bid} 超时，无法输入")
            except Exception as e:
                pytest.fail(f"输入广告出价：{ad_bid} 出错：{e}")

    def set_search_express(self, bid_factor, expansion):
        """8.设置搜索快投"""
        try:
            self.page.locator(CampaignPageToutiaoLocators.LIST_SEARCH).click()
        except PlaywrightTimeoutError:
            pytest.fail("点击侧边栏搜索快投超时，无法点击")
        except Exception as e:
            pytest.fail(f"点击侧边栏搜索快投出错：{e}")
        # 关键词 非必需字段【搜索关键字 test】【可选可不选】
        # self.click_element(CampaignPageToutiaoLocators.KEY_BAG_BUTTON) #点击选择关键词包按钮
        # key_bag_name = "test"
        # self.fill_input(CampaignPageToutiaoLocators.KEY_BAG_SEARCH, key_bag_name) #输出关键词包名搜索
        # self.page.get_by_role("row", name=key_bag_name).locator("span").nth(1).click() #勾选
        # self.page.get_by_role("button", name="确认").click()  # 确认按钮
        # self.page.get_by_role("button", name="取消").click()  # 取消按钮
        try:
            self.page.locator(CampaignPageToutiaoLocators.BID_FACTOR_INPUT).fill(str(bid_factor))  # 输入出价系数
        except PlaywrightTimeoutError:
            pytest.fail(f"输入出价系数：{bid_factor} 超时，无法输入")
        except Exception as e:
            pytest.fail(f"输入出价系数：{bid_factor} 出错：{e}")
        # 定向拓展【默认值，可不操作】
        # self.page.locator(CampaignPageToutiaoLocators.SEARCH_QUICK_LABEL).filter(has_text=expansion).click()

    def set_generation(self, generation_type, campaign_type, campaign_status, ad_status):
        """9.设置项目生成方式与标签"""
        # 可以取默认值，不操作
        try:
            self.page.locator(CampaignPageToutiaoLocators.LIST_GENERATION).click()
        except PlaywrightTimeoutError:
            pytest.fail("点击侧边栏项目生成方式与标签超时，无法点击")
        except Exception as e:
            pytest.fail(f"点击侧边栏项目生成方式与标签出错：{e}")
        # 项目生成方式   直播-直播素材，只能选择“按受众”选项[此时，他们对应的“按受众”是disabled状态]
        # if generation_type == "按受众":
        #     radio = self.page.get_by_role("radio", name=generation_type).first
        #     if radio and 'is-disabled' not in radio.get_attribute('class'):
        #         radio.click() #活动状态才点击
        #     else:
        #         print("按受众radio为disabled状态，不需要点击，跳过")
        # else:
        #     self.page.locator(CampaignPageToutiaoLocators.LABEL_LOCATOR).filter(has_text=generation_type).click()
        # #投放类型
        # self.page.locator(CampaignPageToutiaoLocators.LABEL_LOCATOR).filter(has_text=campaign_type).click()

        # 项目标签【非必需字段，可以将其默认设为NONE，在创建广告时中先判断test_data中是否包含该字段，有则进行操作】
        # self.click_element(CampaignPageToutiaoLocators.CAMPAIGN_TAG) #点击项目标签＋号
        # self.page.get_by_text("项目生成方式 按受众 按受众、创意 投放类型 拉新 回流 混投 项目标签").click() #点击空白处

        # 项目启停、广告启停【默认值即可，不需要操作】
        # 项目启停设置
        # self.page.locator(CampaignPageToutiaoLocators.LABEL_LOCATOR).filter(has_text=campaign_status).click()
        # 广告启停设置
        # self.page.locator(CampaignPageToutiaoLocators.LABEL_LOCATOR).filter(has_text=ad_status).click()

    def _verify_creation_success(self):
        """点击按钮后直接返回成功（不检查成功消息）"""
        # 点击“预览广告”，并捕获新页面
        try:
            self.page.get_by_text("预览广告").click()
        except PlaywrightTimeoutError:
            pytest.fail("点击“预览广告”超时，无法点击")
        except Exception as e:
            pytest.fail(f"点击“预览广告”出错：{e}")

        # 等待预览页面加载完成
        self.page.wait_for_load_state("networkidle")

        # 判断预览页面是否存在“名称过长”错误
        self.page.wait_for_url("**/preview?**", timeout=5000)  # 等待 URL 包含 /preview
        # 检查“名称过长”
        error_locator = self.page.locator(
            "//div[@class='error-popover-content' and contains(.,'名称过长')]"
        )
        # 等待错误提示可见
        # 注意：点击“预览广告”后，页面在当前 tab 导航为 SPA，错误提示是动态渲染的 popover，因此直接用 is_visible()
        # 或 expect_page() 会失效，需要先等待 URL 切换到 preview 页面再用 locator.wait_for(state="visible") 检测元素。
        try:
            # TODO 这里最好先等加载按钮消失，再进行判断；
            #  否则有时候还没加载完error_locator.wait_for(state="visible", timeout=5000)就超时了，参考前面代码怎么等待加载按钮消失的
            # 捕获不到会报错，报错代表没出现该元素，直接pass
            error_locator.wait_for(state="visible", timeout=5000)
            # # 元素出现后直接跳回表单页面并fail
            # self.page.goto("http://dap-staging-6.micro-stage.lilith.sh/promotion/toutiao/batch-create/form-info")
            # pytest.xfail("广告预览时：名称过长，最长100字符（已考虑账户备注长度8字符）。请注意选择的素材名称")
            # # warnings.warn(
            # #     "广告预览时：名称过长，最长100字符（已考虑账户备注长度8字符）。请注意选择的素材名称",
            # #     UserWarning
            # # )
            # 在 allure 报告里挂警告信息（不会让用例 fail）
            with allure.step("⚠️ 警告：广告预览时名称过长"):
                allure.attach(
                    "广告预览时：名称过长，最长100字符（已考虑账户备注长度8字符）。请注意选择的素材名称",
                    name="警告详情",
                    attachment_type=allure.attachment_type.TEXT
                )
        except PlaywrightTimeoutError:
            # 元素未出现，继续执行
            pass

        # 返回表单页面
        self.page.goto(
            "http://dap-staging-6.micro-stage.lilith.sh/promotion/toutiao/batch-create/form-info"
        )

        return True
