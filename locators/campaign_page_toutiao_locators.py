"""
头条批量创建页面元素定位符
"""
from dataclasses import dataclass


@dataclass
class CampaignPageToutiaoLocators:
    # 验证页面是否加载完成
    PAGE_TITLE = "text=批量创建"

    # 1.1选择关联游戏 下的XPATH定位元素:
    GAME_SELECTOR_NEW = ("//div[@id='gameAccount']//div[contains(@class,'ep-select__selected-item') "
                         "and contains(@class,'ep-select__placeholder')]")
    # 在控制台中可以：setTimeout(() => { debugger; }, 3000); 对于动态元素方便定位
    GAME_SELECTED = "//ul[contains(@class,'ep-select-dropdown__list')]//li//div[normalize-space(text())='{game}']"

    # 2.营销目标与场景
    LIST_PURPOSE_SCENE = "//li[contains(normalize-space(text()),'营销目标与场景')]"
    PURPOSE_SCENE_SELECTOR_NEW = "//div[@id='marketingScene']//div[normalize-space(text())='{purpose}']"
    SUB_PURPOSE_LABEL_LOCATOR = "//label[contains(.,'{sub_purpose}')]"
    PURPOSE_SCENE_LABEL_NEW = "//div[@id='marketingScene']//span[text()='{scene_ad_type_delivery_mode}']"
    LANHAI_KEY = "//button[normalize-space(.)='添加蓝海关键词']"
    LANHAI_KEYWORD_TITLE = "//h3[@class='group-title' and normalize-space(text())='{game}']"
    GAME_GROUP_SELECTOR = "//h3[@class='group-title' and normalize-space(text())='{game}']/.."
    LANHAI_FIRST_KEYWORD = ("(//h3[@class='group-title' and normalize-space(text())='{game}']"
                            "/following-sibling::div[contains(@class,'group-keywords')]"
                            "//div[@class='keyword-option']//label[contains(@class,'ep-checkbox')])[1]")
    CUSTOM_KEY = "//div[@class='blue-ocean-custom-keyword']//div[text()='选择']"
    CUSTOM_KEYWORD_TITLE = "//div[text()='添加自定义关键词']"
    CUSTOM_KEYWORD_INPUT = "//input[@placeholder='最多可输入10个关键词进行搜索']"
    CUSTOM_KEYWORD_QUERY = "//span[normalize-space(.)='查询']"
    CUSTOM_KEYWORD_ADD = "//span[normalize-space(.)='添加']"
    LANHAI_BAG = "//span[contains(text(), '未选择蓝海流量包')]//..//following-sibling::div//div[normalize-space(text())='选择']"
    LANHAI_BAG_TITLE = "//span[text()='蓝海流量包']"
    LANHAI_BAG_ROW_RADIO = "//table[contains(@class,'ep-table__body')]//tr[contains(.,'{game}')]//td[1]//span/span"

    # 1.2 选择投放账户
    ACCOUNT_ADD = "//button[normalize-space(.)='添加账户']"
    ACCOUNT_FILL_NEW = "//h1[text()='投放账户']//..//following-sibling::div//input[@placeholder='请输入']"
    ACCOUNT_ID = "//table[@class='ep-table__body']//div[@title='{account}']"
    ACCOUNT_ID_SELECTED = "//tr[.//div[@title='{account}']]//td[1]//div[contains(@class,'cursor-pointer')]"

    # 3.投放内容与目标【应用类型、推广应用、转化目标】
    LIST_CONTENT_TARGET = "//li[contains(normalize-space(text()),'投放内容与目标')]"
    STAR_TASK_SELECTOR = ("//div[span[text()='未选择星广联投任务']]//..//..//div[span[contains(text(),'未选择星广联投任务')]]"
                          "/following-sibling::div/div[contains(text(),'选择')]")
    STAR_TASK_INPUT = "//input[@placeholder='请输入任务名称']"
    STAR_TASK_CHECKBOX = "//tr[contains(.,'战火勋章25年3月星广联投素材-常规剪辑赛道-芦鸣')]/td[1]//span[@class='ep-radio__inner']"
    APP_TYPE_SELECTED = "//label[span[text()='{app_type}']]"
    APP_SELECTOR_BOX_NEW = ("//*[@id='deliveryGoal']//div[contains(@class,'ep-select__selection')]/div["
                            "contains(@class,'ep-select__selected-item') and contains(@class,'ep-select__placeholder')]"
                            )
    DEEP_CONVERSION_LABEL = "label:has-text('深度转化方式')"
    DEEP_CONVERSION_WAY = "span:has-text('每次付费+7日ROI')"
    CONVERSION_SEARCH_INPUT_NEW = "input[placeholder='请输入关键词']"

    # 4. 投放版位
    LIST_PLACEMENT = "li:has-text('投放版位')"
    LIST_PLACEMENT_SELECTED = "//label[span[contains(.,'{position}')]]"

    # 5. 用户定向
    LIST_USER_TARGETING = "li:has-text('用户定向')"
    TARGETING_PACK_BUTTON = "button:has-text('添加定向包')"

    # 6. 广告创意（旧版）/广告设置
    LIST_AD_SET_NEW = "li:has-text('广告设置')"
    AD_MATERIAL_LABEL_SELECTOR_NEW = "#promotionSetting label"
    MATERIAL_TYPE_SELECTED = "//label[span[contains(.,'{material_type}')]]"
    DOUYIN_SELECT_BUTTON = "button:has-text('选择抖音号')"
    DOUYIN_SELECTOR_NEW = "span[placeholder='未选择抖音号']"  # 新版
    DOUYIN_SELECTOR_BUTTON_NEW = "../following-sibling::button"  # 新版xpath 兄弟层级定位
    DOUYIN_SEARCH_INPUT = "role=textbox[name='请输入名称、ID或备注搜索']"
    DOUYIN_SEARCH_INPUT_NEW = "input[placeholder='请输入抖音号']"  # 新版
    DOUYIN_SEARCH_BUTTON = "dialog[role='dialog'][name='选择抖音号'] i"
    PRODUCT_NAME = "#adMaterial"
    PRODUCT_NAME_LABEL = "label:has-text('产品名称')"
    PRODUCT_NAME_CONTENT = ".. >> div.el-form-item__content"
    AD_MATERIAL_IMG = "#adMaterial"
    TEXT_SUMMARY_INPUT = "input[placeholder='至少49个字符']"
    TEXT_SUMMARY = "button:has-text('摘要库')"
    TEXT_TEST = "testtesttesttesttesttesttesttesttesttesttesttesttest"
    LANHAI_KEY_SELECTOR = "input[placeholder='请选择蓝海关键词']"

    # 素材组
    # 新版
    MATERIAL_SELECT_BUTTON = "button:has-text('批量选择素材')"
    LANHAI_KEY_SELECTOR_SET = ".ep-select__selected-item:has-text('请选择蓝海关键词')"
    # 【素材组设置】

    VIDEO = "div.drawer-content-inner div.ep-input__wrapper span:has-text('视频')"
    IMG = "div.drawer-content-inner div.ep-input__wrapper span:has-text('图片')"
    GROUPIMG = "div.drawer-content-inner div.ep-input__wrapper span:has-text('图文')"
    TEXT = "div.drawer-content-inner div.ep-input__wrapper span:has-text('文案')"
    DOUYIN_VIDEO = "div.drawer-content-inner div.ep-input__wrapper span:has-text('抖音视频')"
    DOUYIN_IMG = "div.drawer-content-inner div.ep-input__wrapper span:has-text('抖音图文')"

    # 【素材类别按钮】
    VIDEOBUTTON = "span.ep-tooltip__trigger:has-text('视频（'):has-text('）')"
    IMGBUTTON = "span.ep-tooltip__trigger:has-text('图片（'):has-text('）')"
    GROUPIMGBUTTON = "span.ep-tooltip__trigger:has-text('组图（'):has-text('）')"
    MUSICBUTTON = "span.ep-tooltip__trigger:has-text('音乐库（'):has-text('）')"
    TEXTBUTTON = "span.ep-tooltip__trigger:has-text('文案库（'):has-text('）')"
    DOUYIN_VIDEO_BUTTON = "span.ep-tooltip__trigger:has-text('抖音视频（'):has-text('）')"
    DOUYIN_IMG_BUTTON = "span.ep-tooltip__trigger:has-text('抖音图文（'):has-text('）')"

    # 旧版[创意盒子]
    ADMATERIAL_BOX = "a:has-text('DAP创意')"
    DAP_DIALOG_SELECTOR = 'div.el-dialog__wrapper:has-text("DAP创意")'
    FIRST_CREATIVE_SELECTOR = '.image-list-wrap.el-row .image-item.hand.p-b-5.m-b-15.el-col.el-col-24' # DAP创意第一个素材
    DOUYIN_BOX_A = "a:has-text('抖音创意')"
    DOUYIN_BOX_BUTTON = "button:has-text('抖音号创意')"
    ADMATERIAL_BOX_SEARCH_INPUT = "input[placeholder='请输入素材、创意名称、文案或创建人搜索']"
    ADMATERIAL_BOX_SEARCH_BUTTON = "button.el-button el-button--default el-button--small is-plain"
    ADMATERIAL_BOX_SEARCH_RESULT_FIRST = ".creative-wp"
    ADMATERIAL_BOX_SEARCH_RESULT_FOURTH = "div:nth-child(4) > .creative-wp > .content"
    LAND_PAGE_SELECT_BUTTON = "a:has-text('添加落地页')"  # 旧版，添加落地页（a）
    LAND_PAGE_SELECT_BUTTON_NEW = "button:has-text('添加落地页')"  # 新版，添加落地页（button）
    LAND_PAGE_SEARCH_INPUT = "input[placeholder='请输入名称关键词']"
    LAND_PAGE_SEARCH_BUTTON = "dialog[role='dialog'] i"

    # 7. 排期与预算
    LIST_SCHEDULE_BUDGET = "li:has-text('排期与预算')"
    SCHEDULE_AND_BUDGET = "#scheduleAndBudget"
    SCHEDULE_AND_BUDGET_NEW = "#scheduleBudget"  # 新版
    PRICE_STRATEGY = "label:has-text('竞价策略')"  # 竞价策略
    DAILY_BUDGET_INPUT = "input[placeholder='请输入项目预算']"
    AD_DAILY_BUDGET_INPUT = "input[placeholder='请输入项目日预算']"
    AD_BUDGET_INPUT = "input[placeholder='请输入广告预算']"
    AD_BID_INPUT = "//input[@placeholder='请输入出价']"
    DEEP_ROI = "input[placeholder='请输入深度转化ROI系数']"
    BUDGET_TYPE_SELECTED = "//label[span[contains(.,'{budget_type}')]]"

    # 8. 搜索快投
    LIST_SEARCH = "li:has-text('搜索快投')"
    KEY_BAG_BUTTON = "button:has-text('选择关键词包')"
    KEY_BAG_SEARCH = "input[placeholder='请输入关键词包名称进行搜索']"
    BID_FACTOR_INPUT = "input[placeholder='请输入出价系数，不少于1.00，不超过2.00']"
    SEARCH_QUICK_LABEL = "#searchQuickPut label"

    # 9. 项目生成方式与标签
    LIST_GENERATION = "li:has-text('项目生成方式与标签')"
    GENERATION_TYPE = "select[name='generationType']"
    CAMPAIGN_TYPE = "select[name='campaignType']"
    CAMPAIGN_STATUS = "div[class*='campaign-status'] label:has-text('{0}')"
    AD_STATUS = "div[class*='ad-status'] label:has-text('{0}')"
