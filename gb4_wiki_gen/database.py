import csv
import json
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint

import argparse


def is_sequence(value):
    return (
        isinstance(value, Sequence)
        and not isinstance(value, (str, bytes))
    )


class RelationResolver:
    def __init__(self, registry, value):
        self.registry = registry
        self.value = value

    def __getattr__(self, item):
        data_table = self.registry[item]
        return data_table[self.value]

    def __str__(self):
        return str(self.value)


class WithRelations:
    def __init__(self, attr: str = None):
        self._attr = attr

    def __set_name__(self, owner, name):
        if self._attr is None:
            self._attr = "_" + ''.join(
                word.title() for word in name.split('_')
            )

    def __set__(self, obj, value):
        pass

    def __get__(self, obj, obj_type=None):
        if obj is None:
            return None
        # if is_sequence(obj.data[self._attr]):
        #     return [
        #         RelationResolver(
        #             obj.registry,
        #             item,
        #         ) for item in obj.data[self._attr]
        #     ]
        return RelationResolver(
            obj.registry,
            obj.data[self._attr]
        )


class DataTable:
    def __init__(self, registry, row_type, data):
        self.data = data
        self.row_type = row_type
        self.registry = registry
        registry[self.data["Name"]] = self

    def keys(self):
        return self.data["Rows"].keys()

    def __contains__(self, key):
        return key in self.data["Rows"]

    def __getitem__(self, key):
        return self.row_type(self.registry, self.data["Rows"][key], key)

    def __iter__(self):
        return iter(
            self.row_type(self.registry, it, key)
            for key, it in self.data["Rows"].items()
        )

    def get(self, id):
        row = self.data["Rows"].get(id)
        if row is None:
            return
        return self.row_type(self.registry, row, id)


class BaseRowType:
    def __init__(self, registry, data, id_):
        self.registry = registry
        self.data = data
        self.id = id

    def __getattr__(self, name):
        try:
            _name = "_" + ''.join(
                word.title() for word in name.split('_')
            )
            return self.data[_name]
        except KeyError:
            return self.data[name]


class AliasAttr:
    def __set_name__(self, owner, name):
        self._attr = name

    def __set__(self, obj, value):
        pass

    def __get__(self, obj, obj_type=None):
        if obj is None:
            return None
        try:
            data_key = "_" + ''.join(
                word.title() for word in self._attr.split('_')
            )
            return obj.data[data_key]
        except KeyError:
            return obj.data[self._attr]


@dataclass(frozen=True)
class DataMSList:
    registry: Mapping
    data: Mapping
    id: str

    head: WithRelations = WithRelations("_head")
    body: WithRelations = WithRelations("_body")
    arm_r: WithRelations = WithRelations("_armR")
    arm_l: WithRelations = WithRelations("_armL")
    leg: WithRelations = WithRelations("_leg")
    backpack: WithRelations = WithRelations("_backpack")


@dataclass(frozen=True)
class DataItemGunplaBox:
    registry: Mapping
    data: Mapping
    id: str

    item_id: AliasAttr = AliasAttr()
    box_art_id: AliasAttr = AliasAttr()
    gundam_series_name: AliasAttr = AliasAttr()
    item_array: WithRelations = WithRelations()


@dataclass(frozen=True)
class DataPartsParameter:
    registry: Mapping
    data: Mapping
    id: str

    parts_name: AliasAttr = AliasAttr()
    parts_category: AliasAttr = AliasAttr()
    inner_parts_array: AliasAttr = AliasAttr()
    equip_attach_type_name: AliasAttr = AliasAttr()
    model_id: AliasAttr = AliasAttr()
    form_motion_type: AliasAttr = AliasAttr()
    move_motion_type: AliasAttr = AliasAttr()
    motion_priority: AliasAttr = AliasAttr()
    is_motion_fixed: AliasAttr = AliasAttr()
    skill_array: AliasAttr = AliasAttr()
    muzzle_array: AliasAttr = AliasAttr()
    skill_parts_info_array: AliasAttr = AliasAttr()
    parts_animation: AliasAttr = AliasAttr()
    hidden_info: AliasAttr = AliasAttr()
    ability_array: AliasAttr = AliasAttr()
    other: AliasAttr = AliasAttr()


@dataclass(frozen=True)
class DataSkillIdInfoData:
    registry: Mapping
    data: Mapping
    id: str

    ui_info_array: AliasAttr = AliasAttr()
    skill_range: AliasAttr = AliasAttr()
    skill_power: AliasAttr = AliasAttr()
    skill_permission_rank: AliasAttr = AliasAttr()
    skill_permission_flag_array: AliasAttr = AliasAttr()
    is_enemy_disable: AliasAttr = AliasAttr()
    ai_cool_time: AliasAttr = AliasAttr()
    ability_cartridge_category: AliasAttr = AliasAttr()
    attack_data_id_for_parameter_display: AliasAttr = AliasAttr()
    hyper_trance_id: AliasAttr = AliasAttr()


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
        Path("GB4/Content/Text/en/Common/localized_text_skill_info.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Text/en/Common/localized_text_skill_name.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Text/en/Common/localized_text_ms_number.json"),
        BaseRowType,
    ),
    (
        Path("GB4/Content/Text/en/Common/localized_text_parts_name.json"),
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
        BaseRowType,
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
        BaseRowType,
    )
)


def load_data(dir_path):
    registry = dict()
    for path, row_type in data_sources:
        with open(dir_path / path, "r", encoding="utf8") as fp:
            raw = json.load(fp)
            DataTable(registry, row_type, raw[0])
    return registry


def load_from_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    args = ap.parse_args()
    dir_path = Path(args.dir)
    return load_data(dir_path)


if __name__ == "__main__":
    registry = load_from_args()

    mslist = registry["MSList"]
    boxlist = registry["ItemGunplaBox"]

    for item in boxlist:
        print("type", list(item.item_array))