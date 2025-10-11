# 环境配置
playwright==1.52.0
pytest==8.4.1
pytest-playwright==0.7.1
allure-pytest==2.15.0
python-dotenv==1.1.1
PyYAML==6.0.2
JDK17：https://adoptium.net/zh-CN
Allure：https://github.com/allure-framework/allure2/releases


# 未做的事项：
（1）所有异常处理其实可以封装到BasePage中（BasePage中已经给了两个例子，click和fill的，但是没真的使用这两个方法）。这样做的好处是不用写那么多的try except了，坏处是错误定位可能不够精准、直观；不过后续还是推荐封装到基类中，代码不会那么冗余
（2）具体要验证哪些场景和用哪些数据，后期有需要请在test_cases和具体的页面对象pages中改流程，在test_data中改数据
（3）用例执行失败时的失败截图功能还没实现。最好是在异常捕获里面显示进行截图，这样截图比较准确。先暂时沿用思田的hook+screenshot，后面如果统一把异常处理放到BasePage中时，可以顺便加上失败截图
（4）设置失败重试机制，避免网络原因导致的加载失败，参考lass HomePage(BasePage): def create_toutiao_campaign(self):中的做法
（5）当有加载按钮出现时，最好先等加载按钮消失，再进行判断；campaign_page_toutiao.py的_verify_creation_success需要进行这样的改动；改动方法可参考campaign_page_toutiao.py的select_materials：loading = self.page.locator(".ep-loading-spinner") loading.wait_for(state="detached", timeout=10000)；定位该元素可能需要冻结页面，控制台中：setTimeout(() => { debugger; }, 3000);
（6）当页面报错时，获取到报错信息，而不是简单的在allure报告中输出异常（参考conftest中的capture_http_errors，还需要改进这个fixture）
（7）test_01和test_02用例融合到广告创建用例中即可，没必要单独写用例
（8）进入主页的刷新重试提示，会被错误的归类到第一个用例中，需要调整。提示形式如：第 1 次进入主页面失败，刷新页面后重试...
（9）浏览器启动参数：slow_mo: 200，设置为了200，这样好像可以避免操作太快导致502或找不到元素的问题；后续有更优的方式可以调整该参数（例如只在容易定位不到元素或容易出502错误的地方加特殊处理或延时处理）



# 使用说明
测试用法示例：
（1）pytest tests/test_cases/test_login.py -s -v --alluredir=reports/allure-results
pytest tests/test_cases/test_login.py 运行指定的测试文件。
-s 让 pytest 显示 print() 的输出（调试时常用）。
-v verbose模式，显示更详细的执行信息。
--alluredir=reports/allure-results 指定 pytest 把 Allure 结果（JSON/XML 格式）输出到 reports/allure-results 目录。
（2）allure generate reports/allure-results -o reports/allure-report --clean
allure generate 生成报告命令。
reports/allure-results 输入目录，里面是上一步 pytest 生成的结果文件。
-o reports/allure-report 输出目录，存放生成好的 HTML 报告文件。
--clean 生成之前清空输出目录，避免旧报告文件残留。
（3）allure open reports/allure-report
allure open 启动一个本地 web 服务并打开浏览器。
reports/allure-report 指定报告的目录。
（4）npx playwright show-trace trace.zip路径 打开追踪文件

推荐直接用.bat来执行，run_test_03.bat是执行test_03_toutiao_campaign.py的批处理脚本，做了清空allure-results目录->运行用例->生成带时间戳的allure报告的操作

调试时：参考测试用例中这样的方法，去跳过不需要调试的用例
if index < 0:
    pytest.skip(f"调试阶段，跳过第{index + 1}个用例")

注意：
（1）不要用time.sleep();playwright底层使用的是异步的Python库进行各种事件处理，time.sleep会破坏异步框架的处理逻辑



# 修改说明
（1）当元素定位发生变化时，一般在locators中找到对应定位修改即可（由于要改的内容过多，campaign_page_toutiao.py中只有一小部分定位放到了locators中；后面的定位基本是playwright定位+CSS定位+XPATH定位混用；也不完全推荐用XAPTH定位，一是定位繁琐、受页面影响因素大，二是XPATH定位速度慢。后续推荐学习AI工具Midscene来定位或探索下有没有别的插件来辅助）
（2）当创建广告的流程发生了变化时，根据提示的异常信息，定位在哪里报错，并修改对应代码结构
（3）当新增广告创建校验，如腾讯广告批量创建，推荐的流程为：
    1.在conftest中建立对应的fixture（参考头条的campaign_page_toutiao fixture）  （提供页面）
    2.在pages中建立对应POM对象（参考头条的campaign_page_toutiao.py）  （提供操作）
    3.在locators中给出对应的页面定位（参考头条的campaign_page_toutiao_locators.py）  （提供定位）
    在test_cases用例中，通过fixture中实例的pom对象，去进行各种操作
总结：当测试用例（test_cases）运行时，会通过参数化方式获取测试数据（来自 test_data），再调用 conftest 中定义的 fixture，fixture 
内部会实例化并返回对应的 POM 对象（pages 中的类）；POM 类中封装了具体的页面操作方法，这些方法需要的元素定位统一从 locators 中获取，
而测试数据则由用例传入（参数化方式获取测试数据这一步）。这样，定位变动只需改 locators，流程变动只需改 pages，新业务新增 fixture + pages + locators + test_case + test_data

当发生报错时：根据报错信息在对应pages中的py文件搜索，看在代码的哪块报错了，再去进行对应的修改（如果有更高效简便的方式忽略这点）


# 代码结构
## configs
存放所有配置相关文件
### browser.yaml
有关浏览器的参数配置
### screenshot.yaml
失败用例截图的参数配置，该功能还没做完，所以在conftest中先注释掉了：screenshot_config capture_screenshot_on_failure pytest_runtest_makereport


## locators
存放部分定位（有些定位直接用playwright的定位方式，就没在这里面写）（考虑有什么更高效的定位方式）
详细介绍参考飞书文档：https://lilithgames.feishu.cn/docx/EqU1dKlLao2bRWxiNA5cB8LCnie （该链接已废弃，2025-09-26，不再更新）
当元素发生变化时，请及时修改locators中对应的元素以及飞书文档上对应的内容，便于维护
### login_page_locators.py
登录页面元素定位符
### home_page_locators.py
主页面元素定位符
### campaign_page_toutiao_locators.py
头条广告创建页面（新版）的定位符



## pages
### base_page.py
POM（Page Object Model 页面对象模式）模式的基类，统一保存 Playwright 的 Page 实例
### login_page.py
登录页面：http://dap-staging-6.micro-stage.lilith.sh/login?from
### home_page.py
首页：http://dap-staging-6.micro-stage.lilith.sh/advertise-2/home
在进行登录后到达的页面
### campaign_page_toutiao.py
头条广告创建页面（新版）



## tests
### test_cases
#### test_01_login.py
### test_data
test_data沿用之前思田的DDT（数据驱动测试）结构，测试数据与用例分离，修改测试数据时只需要关注test_data中对应内容即可。
#### base_data.yaml
略，具体参考其中注释
#### scenarios.yaml
营销场景数据，会通过utils中的generate_test_combinations、match_resources，与base_data配合去生成测试数据
例如：test_03_toutiao_campaign.py中的generate_test_combinations(scenario, base_data)



## utils
沿用思田的dap_ad_autotest的src/common/utils.py中的通用方法
（1）load_yaml(file_path: str) -> dict 
略
（2）generate_test_combinations(scenario: Dict, base_data: Dict) -> Iterator[Dict]
待总结（下面是ai总结）
根据场景配置和基础数据，自动生成多维度的测试数据组合（支持特殊逻辑处理），并结合资源映射生成可用的测试数据字典，适合用于 pytest 参数化。
（3）match_resources(base_data: Dict, scene: str, purpose: str, app_type: str) -> Tuple[str, str]
待总结（下面是ai总结）
在资源映射表中查找匹配的游戏与账号资源，确保每个测试组合都能绑定实际资源， 如果找不到则抛出异常。


## .env
存放账号密码敏感资源，放到公共仓时删除该文件


## conftest
全局共用的资源
### fixture：credentials
加载系统环境变量配置：基础路径、用户名、密码等敏感信息；通过读取.env文件来实现
### browser_config
返回浏览器相关参数配置
### browser_type_launch_args
合并默认的和自定义的浏览器启动参数
### browser_context_args
合并默认的和自定义的浏览器上下文参数
### authenticated_context
浏览器上下文，全局共享
### login_page
进行登录操作，并返回已登录的Page对象
### home_page
基于已登录的 login_page。返回的对象已经是广告创建页面的 POM
### campaign_page_toutiao
头条广告创建页面的 POM
