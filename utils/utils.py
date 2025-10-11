import yaml
import os
from pathlib import Path
from dotenv import load_dotenv
from itertools import product
from typing import Dict, Any, Optional, Iterator, Tuple, List


def load_yaml(file_path: str | Path) -> dict:
    """
    加载 YAML 文件内容（通用方法，测试/业务代码均可复用）
    :param file_path: YAML 文件路径
    :return: 解析后的 YAML 数据（字典格式）
    :raises FileNotFoundError: 文件不存在时抛出异常
    :raises yaml.YAMLError: YAML 解析失败时抛出异常
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"YAML 文件未找到: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML 解析失败: {str(e)}") from e


def generate_test_combinations(scenario: Dict[str, Any],
                               base_data: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
    """生成测试数据组合"""
    # 1. 提取场景字段
    scene_fields = {
        "scene": scenario["scene"],
        "ad_type": scenario["ad_type"],
        "delivery_mode": scenario["delivery_mode"]
    }
    if "extra_fields" in scenario:
        scene_fields.update(scenario["extra_fields"])

    # 2. 准备基础字段
    base_fields = {
        "app_type": base_data["contents"]["app_types"],
        "placement": base_data["placements"]["positions"],
        "filter_type": base_data["targetings"]["filter_types"],
        "filter_days": base_data["targetings"]["filter_days"],
        "time": base_data["budget"]["time"],
        "time_period": base_data["budget"]["time_periods"],
        "bidding_strategy": base_data["budget"]["bidding_strategies"],
        "budget_type": base_data["budget"]["budget_types"],
        "daily_budget": base_data["budget"]["daily_budgets"],
        "ad_budget": base_data["budget"]["ad_budgets"],
        "ad_bid": base_data["budget"]["ad_bids"],
        "generation_type": base_data["generation"]["generation_types"],
        "campaign_type": base_data["generation"]["campaign_types"],
        "campaign_status": base_data["generation"]["campaign_status"],
        "ad_status": base_data["generation"]["ad_status"]
    }

    # 3. 处理特殊字段
    if scenario["ad_type"] == "通投广告" and scenario["delivery_mode"] == "手动投放":
        base_fields["bid_factor"] = base_data["search_express"]["bid_factors"]
        base_fields["expansion"] = base_data["search_express"]["expansion_options"]

    if scene_fields["scene"] == "直播" and scene_fields.get("material_type") == "直播素材":
        base_fields["generation_type"] = ["按受众"]

    # 4. 生成组合
    purpose_sub_combos = [
        combo for purpose in base_data["purposes"]
        for combo in purpose["purpose_sub_combos"]
    ]
    other_field_names = list(base_fields.keys())
    other_field_values = list(base_fields.values())

    for other_values, (purpose, sub_purpose) in product(
            product(*other_field_values), purpose_sub_combos):

        test_data = dict(zip(other_field_names, other_values))
        test_data.update({
            "purpose": purpose,
            "sub_purpose": sub_purpose,
            **scene_fields,
            "scenario_name": scenario["name"]
        })

        # 获取单个game和account值
        try:
            game, account = match_resources(
                base_data,
                test_data["scene"],
                purpose,
                test_data.get("app_type")
            )
            test_data["game"] = game
            test_data["account"] = account
            yield test_data
        except ValueError as e:
            print(f"跳过无效组合: {str(e)}")
            continue


def match_resources(base_data: Dict[str, Any], scene: str,
                    purpose: str, app_type: str) -> Tuple[str, str]:
    """
    精确匹配游戏和账户资源，返回单个值
    :return: (game, account)
    :raises ValueError: 如果找不到匹配资源
    """
    matched_games = []
    matched_accounts = []

    for mapping in base_data.get("resource_mapping", []):
        scene_match = mapping["scene"] == scene
        purpose_match = (mapping["purpose"] == "*" or
                         mapping["purpose"] == purpose)
        app_type_match = (mapping["app_type"] == "*" or
                          mapping["app_type"] == app_type)

        if scene_match and purpose_match and app_type_match:
            if mapping["games_key"] in base_data["games"]:
                matched_games.extend(base_data["games"][mapping["games_key"]])
            if mapping["accounts_key"] in base_data["accounts"]:
                matched_accounts.extend(base_data["accounts"][mapping["accounts_key"]])

    if not matched_games or not matched_accounts:
        raise ValueError(f"未找到匹配的资源: scene={scene}, purpose={purpose}, app_type={app_type}")

    # 返回第一个匹配项
    return matched_games[0], matched_accounts[0]
