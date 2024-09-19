import json
from collections.abc import Mapping
from pathlib import Path

import argparse

from models import DataTable, BaseRowType, \
    DataMSList, DataItemGunplaBox, DataPartsParameter, DataSkillIdInfoData, \
    DataEquipParameter, MissionRewardTable, MSListTable, \
    DerivedSynthesizeParameterTable

data_sources = {
    "GB4/Content/Text/en/Common/localized_text_ability_cartridge_name.json": (
        BaseRowType,
    ),
    "GB4/Content/Text/en/Common/localized_text_ability_cartridge_info.json": (
        BaseRowType,
    ),
    "GB4/Content/Text/en/Common/localized_text_preset_character_name.json": (
        BaseRowType,
    ),
    "GB4/Content/Text/en/Common/localized_text_ms_number.json": (
        BaseRowType,
    ),
    "GB4/Content/Text/en/Common/localized_text_skill_info.json": (
        BaseRowType,
    ),
    "GB4/Content/Text/en/Common/localized_text_skill_name.json": (
        BaseRowType,
    ),
    "GB4/Content/Text/en/Common/localized_text_parts_name.json": (
        BaseRowType,
    ),
    "GB4/Content/Text/en/Common/localized_text_weapon_name.json": (
        BaseRowType,
    ),
    "GB4/Content/Text/en/Common/localized_text_shield_name.json": (
        BaseRowType,
    ),
    "GB4/Content/Text/en/Common/localized_text_bparts_name.json": (
        BaseRowType,
    ),
    "GB4/Content/Text/en/Menu/localized_text_story_title_name.json": (
        BaseRowType,
    ),
    "GB4/Content/Data/MS/AbilityCartridge.json": (
        BaseRowType,
    ),
    "GB4/Content/Data/MS/AbilityInfo.json": (
        BaseRowType,
    ),
    "GB4/Content/Data/MS/AbilityPerformance.json": (
        BaseRowType,
    ),
    "GB4/Content/Data/MS/EquipAttachParameter.json": (
        BaseRowType,
    ),
    "GB4/Content/Data/MS/EquipParameter.json": (
        DataEquipParameter,
    ),
    "GB4/Content/Data/MS/EquipPerformance.json": (
        BaseRowType,
    ),
    "GB4/Content/Data/MS/MSList.json": (
        DataMSList, MSListTable
    ),
    "GB4/Content/Data/MS/PartsIdList.json": (
        BaseRowType,
    ),
    "GB4/Content/Data/MS/PartsParameter.json": (
        DataPartsParameter,
    ),
    "GB4/Content/Data/Item/ItemGunplaBox.json": (
        DataItemGunplaBox,
    ),
    "GB4/Content/Data/Skill/SkillIdInfo.json": (
        DataSkillIdInfoData,
    ),
    "GB4/Content/Data/Item/ItemDrop/MissionRewardTable.json": (
        BaseRowType, MissionRewardTable
    ),
    "GB4/Content/Data/Mission/MissionListTable.json": (
        BaseRowType,
    ),
    "GB4/Content/Data/Synthesize/DerivedSynthesizeParameter.json": (
        BaseRowType, DerivedSynthesizeParameterTable
    ),
}


def load_data(dir_path) -> Mapping[str, DataTable]:
    registry = dict()
    for path, types in data_sources.items():
        match types:
            case (row_type,):
                table_type = DataTable
            case (row_type, table_type,):
                pass

        with open(Path(dir_path) / path, "r", encoding="utf8") as fp:
            raw = json.load(fp)
            table_type(registry, row_type, raw[0])
    return registry


def load_from_args() -> Mapping[str, DataTable]:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    args = ap.parse_args()
    dir_path = Path(args.dir)
    return load_data(dir_path)


if __name__ == "__main__":
    registry = load_from_args()
