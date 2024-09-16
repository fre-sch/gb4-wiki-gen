import json
from collections.abc import Mapping
from pathlib import Path

import argparse

from models import DataTable, BaseRowType, \
    DataMSList, DataItemGunplaBox, DataPartsParameter, DataSkillIdInfoData, \
    DataEquipParameter

data_sources = (
    (
        Path("GB4/Content/Text/en/Common/localized_text_ability_cartridge_name.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Text/en/Common/localized_text_ability_cartridge_info.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Text/en/Common/localized_text_preset_character_name.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Text/en/Common/localized_text_ms_number.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Text/en/Common/localized_text_skill_info.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Text/en/Common/localized_text_skill_name.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Text/en/Common/localized_text_parts_name.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Text/en/Common/localized_text_weapon_name.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Text/en/Common/localized_text_shield_name.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Data/MS/AbilityCartridge.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Data/MS/AbilityInfo.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Data/MS/AbilityPerformance.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Data/MS/EquipAttachParameter.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Data/MS/EquipParameter.json"),
        DataEquipParameter,
    ),
    (
        Path("GB4/Content/Data/MS/EquipPerformance.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Data/MS/MSList.json"),
        DataMSList,
    ),
    (
        Path("GB4/Content/Data/MS/PartsIdList.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Data/MS/PartsParameter.json"),
        DataPartsParameter,
    ),
    (
        Path("GB4/Content/Data/Item/ItemGunplaBox.json"),
        DataItemGunplaBox,
    ),
    (
        Path("GB4/Content/Data/Skill/SkillIdInfo.json"),
        DataSkillIdInfoData,
    )
)


def load_data(dir_path) -> Mapping[str, DataTable]:
    registry = dict()
    for path, row_type in data_sources:
        with open(dir_path / path, "r", encoding="utf8") as fp:
            raw = json.load(fp)
            DataTable(registry, row_type, raw[0])
    return registry


def load_from_args() -> Mapping[str, DataTable]:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    args = ap.parse_args()
    dir_path = Path(args.dir)
    return load_data(dir_path)


if __name__ == "__main__":
    registry = load_from_args()
