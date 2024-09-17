import re
from dataclasses import dataclass
from typing import Mapping

from utils import is_sequence


# class ReferenceResolver:
#     def __init__(self, registry, value, value_type=None):
#         self.registry = registry
#         self.value = value
#         self.value_type = value_type
#
#     def __getattr__(self, item) -> "DataTable":
#         data_table = self.registry[item]
#         return data_table[self.value]
#
#     def __iter__(self):
#         return iter(
#             ReferenceResolver(self.registry, it)
#             for it in self.value
#         )
#
#     def __str__(self):
#         return str(self.value)


class UReference:
    def __init__(self, *, attr: str = None, table: str):
        self._attr = attr
        self._data_table_key = table

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
        data_table = obj.registry[self._data_table_key]
        key = obj.id if self._attr == "id" else obj.data[self._attr]
        if key == "None":
            return None
        if is_sequence(key):
            return [data_table[it] for it in key]
        return data_table[key]


class UReferenceObjectArray:
    def __init__(self, *, attr: tuple[str, str], table: str):
        self._attr = attr
        self._data_table_key = table

    def __set__(self, obj, value):
        pass

    def __get__(self, obj, obj_type=None):
        if obj is None:
            return None
        field_key, item_key = self._attr
        data_table = obj.registry[self._data_table_key]
        obj_data = obj.data[field_key]

        return [
            data_table[it[item_key]]
            for it in obj_data
        ]


class DataTableIndexError(Exception):
    def __init__(self, table_name, key):
        super().__init__(f"table {table_name!r} missing key {key!r}")
        self.table_name = table_name
        self.key = key

    def __repr__(self):
        return f"DataTableIndexError(table_name={self.table_name}, key={self.key})"


class DataTable:
    def __init__(self, registry, row_type, data):
        self.data = data
        self.row_type = row_type
        self.registry = registry
        registry[self.data["Name"]] = self

    @property
    def rows(self) -> dict:
        return self.data["Rows"]

    def keys(self):
        return self.rows.keys()

    def __contains__(self, key):
        return key in self.rows

    def __getitem__(self, key):
        try:
            return self.row_type(self.registry, self.rows[key], key)
        except KeyError as e:
            raise DataTableIndexError(self.data["Name"], key) from None

    def __iter__(self):
        return iter(
            self.row_type(self.registry, it, key)
            for key, it in self.rows.items()
        )

    def get(self, id):
        row = self.rows.get(id)
        if row is None:
            return
        return self.row_type(self.registry, row, id)


class MissionRewardTable(DataTable):
    def __init__(self, registry, row_type, data):
        super().__init__(registry, row_type, data)
        self.init_rows(data)
        self.init_reward_item_mapped()

    def init_rows(self, data):
        self._rows = {}
        for key, item in data["Rows"].items():
            is_graded = re.match("(.+?)_?([ABCDS])$", key)
            if is_graded:
                mission_key = is_graded.group(1)
                clear_grade = {"_ClearGrade": is_graded.group(2)}
            else:
                mission_key = key
                clear_grade = {}
            for reward_item in item["_RewardItemInfoArray"]:
                mission_row = self._rows.setdefault(mission_key, [])
                mission_row.append({
                    **reward_item,
                    **clear_grade,
                })

    def init_reward_item_mapped(self):
        self.reward_item_mapped = {}
        for mission_key, mission_rewards in self._rows.items():
            for mission_reward in mission_rewards:
                reward_item_id = mission_reward["_RewardItemId"]
                missions = self.reward_item_mapped.setdefault(reward_item_id, [])
                missions.append(mission_key)

    @property
    def rows(self) -> dict:
        return self._rows

    def mission_by_reward_item(self, item_id) -> list:
        self.reward_item_mapped.get(item_id, [])


class BaseRowType:
    def __init__(self, registry, data, id):
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


class UField:
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
        value = obj.data[self._attr]
        if value == "None":
            return None
        return value


@dataclass(frozen=True)
class DataMSList:
    registry: Mapping
    data: Mapping
    id: str

    head: UField = UField("_head")
    body: UField = UField("_body")
    arm_r: UField = UField("_armR")
    arm_l: UField = UField("_armL")
    leg: UField = UField("_leg")
    backpack: UField = UField("_backpack")
    equip0: UField = UField("_equip0")
    equip1: UField = UField("_equip1")
    equip2: UField = UField("_equip2")
    equip3: UField = UField("_equip3")
    equip4: UField = UField("_equip4")
    equip5: UField = UField("_equip5")
    equip6: UField = UField("_equip6")
    equip7: UField = UField("_equip7")

    ms_number_localized: UReference = UReference(attr="id", table="localized_text_ms_number")
    ms_name_localized: UReference = UReference(attr="id", table="localized_text_preset_character_name")

    head_localized: UReference = UReference(attr="_head", table="localized_text_parts_name")
    body_localized: UReference = UReference(attr="_body", table="localized_text_parts_name")
    arm_r_localized: UReference = UReference(attr="_armR", table="localized_text_parts_name")
    arm_l_localized: UReference = UReference(attr="_armL", table="localized_text_parts_name")
    leg_localized: UReference = UReference(attr="_leg", table="localized_text_parts_name")
    backpack_localized: UReference = UReference(attr="_backpack", table="localized_text_parts_name")

    head_part_params: UReference = UReference(attr="_head", table="PartsParameter")
    body_part_params: UReference = UReference(attr="_body", table="PartsParameter")
    arm_r_part_params: UReference = UReference(attr="_armR", table="PartsParameter")
    arm_l_part_params: UReference = UReference(attr="_armL", table="PartsParameter")
    leg_part_params: UReference = UReference(attr="_leg", table="PartsParameter")
    backpack_part_params: UReference = UReference(attr="_backpack", table="PartsParameter")

    equip0_params: UReference = UReference(attr="_equip0", table="EquipParameter")
    equip1_params: UReference = UReference(attr="_equip1", table="EquipParameter")
    equip2_params: UReference = UReference(attr="_equip2", table="EquipParameter")
    equip3_params: UReference = UReference(attr="_equip3", table="EquipParameter")
    equip4_params: UReference = UReference(attr="_equip4", table="EquipParameter")
    equip5_params: UReference = UReference(attr="_equip5", table="EquipParameter")
    equip6_params: UReference = UReference(attr="_equip6", table="EquipParameter")
    equip7_params: UReference = UReference(attr="_equip7", table="EquipParameter")




@dataclass(frozen=True)
class DataItemGunplaBox:
    registry: Mapping
    data: Mapping
    id: str

    item_id: UField = UField()
    box_art_id: UField = UField()
    gundam_series_name: UField = UField()
    item_array: UField = UField()

    items_parts_parameters: UReference = UReference(attr="_ItemArray", table="PartsParameters")


@dataclass(frozen=True)
class DataPartsParameter:
    registry: Mapping
    data: Mapping
    id: str

    parts_name: UField = UField()
    parts_category: UField = UField()
    inner_parts_array: UField = UField()
    equip_attach_type_name: UField = UField()
    model_id: UField = UField()
    form_motion_type: UField = UField()
    move_motion_type: UField = UField()
    motion_priority: UField = UField()
    is_motion_fixed: UField = UField()
    skill_array: UField = UField()
    muzzle_array: UField = UField()
    skill_parts_info_array: UField = UField()
    parts_animation: UField = UField()
    hidden_info: UField = UField()
    ability_array: UField = UField()
    other: UField = UField()

    parts_name_localized: UReference = UReference(attr="_PartsName", table="localized_text_weapon_name")
    skill_array_data: UReferenceObjectArray = UReferenceObjectArray(
        attr=("_SkillArray", "_SkillId"), table="SkillIdInfo")


@dataclass(frozen=True)
class DataSkillIdInfoData:
    registry: Mapping
    data: Mapping
    id: str

    ui_info_array: UField = UField()
    skill_range: UField = UField()
    skill_power: UField = UField()
    skill_permission_rank: UField = UField()
    skill_permission_flag_array: UField = UField()
    is_enemy_disable: UField = UField()
    ai_cool_time: UField = UField()
    ability_cartridge_category: UField = UField()
    attack_data_id_for_parameter_display: UField = UField()
    hyper_trance_id: UField = UField()

    name_localized: UReference = UReference(attr="id", table="localized_text_skill_name")
    info_localized: UReference = UReference(attr="id", table="localized_text_skill_info")

    ui_info_array_data: UReferenceObjectArray = UReferenceObjectArray(
        attr=("_UiInfoArray", "_TextId"), table="localized_text_skill_name"
    )

    @property
    def ui_name_localized(self):
        try:
            t = self.registry["localized_text_skill_name"]
            for item in self.ui_info_array:
                return t[item["_TextId"]]._text
        except Exception:
            return None

    @property
    def ui_info_localized(self):
        try:
            t = self.registry["localized_text_skill_info"]
            for item in self.ui_info_array:
                return t[item["_TextId"]]._text
        except Exception:
            return None


@dataclass(frozen=True)
class DataEquipParameter:
    registry: Mapping
    data: Mapping
    id: str

    parts_name: UField = UField()
    parts_category: UField = UField()
    equip_type: UField = UField()
    inner_flag: UField = UField()
    inner_parts_array: UField = UField()
    model_id_arm_right: UField = UField()
    model_id_arm_left: UField = UField()
    sub_model_id_arm_right: UField = UField()
    sub_model_id_arm_left: UField = UField()
    mirror_type_arm_right: UField = UField()
    mirror_type_arm_left: UField = UField()
    attach_position_arm_right: UField = UField()
    attach_position_arm_left: UField = UField()
    attach_rotation_arm_right: UField = UField()
    attach_rotation_arm_left: UField = UField()
    root_locator_name: UField = UField()
    motion_type: UField = UField()
    skill_array: UField = UField()
    muzzle_array: UField = UField()
    skill_parts_info_array: UField = UField()
    parts_animation: UField = UField()
    hidden_info: UField = UField()
    ability_array: UField = UField()
    other: UField = UField()

    skill_array_data: UReferenceObjectArray = UReferenceObjectArray(
        attr=("_SkillArray", "_SkillId"), table="SkillIdInfo")

    @property
    def name_localized(self):
        if self.parts_category == "MS_EQUIP_CATEGORY::SHIELD":
            t = self.registry["localized_text_shield_name"]
            return t[self.parts_name]
        else:
            t = self.registry["localized_text_weapon_name"]
            return t[self.parts_name]