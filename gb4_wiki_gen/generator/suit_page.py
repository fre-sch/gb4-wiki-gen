from itertools import zip_longest

from slugify import slugify

from models import DataTableIndexError, DataEquipParameter, DataPartsParameter, \
    DataMSList


def make_skill_data(part_param: DataPartsParameter):
    ex_skills = []
    op_skills = []
    awaken_skills = []

    for skill_data in part_param.skill_array_data:
        ns, ability_type = skill_data.ability_cartridge_category.split("::")
        item = {
            "name": skill_data.name_localized._text,
            "info": skill_data.info_localized._text,
            "ability_type": ability_type
        }
        if "ORIGINAL" in ability_type:
            awaken_skills.append(item)

        elif "EX" in ability_type:
            ex_skills.append(item)

        elif "OP" in ability_type:
            op_skills.append(item)

    return list(zip_longest(ex_skills, op_skills, awaken_skills, fillvalue=None))


def make_equip_data(equip_params: DataEquipParameter):
    if equip_params is None:
        return None

    normal_skills = []
    ex_skills = []
    op_skills = []
    awaken_skills = []

    for skill_data in equip_params.skill_array_data:
        ns, ability_type = skill_data.ability_cartridge_category.split("::")
        item = {
            "name": skill_data.ui_name_localized,
            "info": skill_data.ui_info_localized,
            "ability_type": ability_type,
        }
        if "NML_" in ability_type:
            normal_skills.append(item)

        elif "EX" in ability_type:
            ex_skills.append(item)

        elif "OP" in ability_type:
            op_skills.append(item)

        elif "ORIGINAL" in ability_type:
            awaken_skills.append(item)

    ns, equip_type = equip_params.parts_category.split("::")
    equip_name = equip_params.name_localized._text

    return equip_type, equip_name, list(zip_longest(normal_skills, ex_skills, op_skills, awaken_skills, fillvalue=None))


def make_derive_from_data(suit):
    try:
        suit.synthesis
    except DataTableIndexError as e:
        return []

    mslist = suit.registry["MSList"]
    part_param_table = suit.registry["PartsParameter"]
    synthesis_table = suit.registry["DerivedSynthesizeParameter"]
    recipes = {}

    for part_id in suit.non_shared_parts_ids:
        for result_id, source1_id, source2_id in synthesis_table.find_derives_from(part_id):
            part_type = part_param_table[result_id].other["_PerformanceGroupName"].replace("Parts", "")
            recipes.setdefault(part_type, []).append(
                {
                    "result_part_name": part_param_table[result_id].parts_name_localized._text,
                    "result_suit_name": mslist.primary_suit_by_part_id(result_id).ms_name_localized._text,
                    "source1_part_name": part_param_table[source1_id].parts_name_localized._text,
                    "source1_suit_name": mslist.primary_suit_by_part_id(source1_id).ms_name_localized._text,
                    "source2_part_name": part_param_table[source2_id].parts_name_localized._text,
                    "source2_suit_name": mslist.primary_suit_by_part_id(source2_id).ms_name_localized._text
                }
            )
    return recipes


def make_derive_into_data(suit: DataMSList):
    mslist = suit.registry["MSList"]
    part_param_table = suit.registry["PartsParameter"]
    synthesis_table = suit.registry["DerivedSynthesizeParameter"]
    recipes = {}

    for part_id in suit.non_shared_parts_ids:
        for result_id, source1_id, source2_id in synthesis_table.find_derives_into(part_id):
            part_type = part_param_table[result_id].other["_PerformanceGroupName"].replace("Parts", "")
            if source1_id == part_id:
                base_id = source1_id
                material_id = source2_id
            else:
                base_id = source2_id
                material_id = source1_id
            recipes.setdefault(part_type, []).append(
                {
                    "result_part_name": part_param_table[result_id].parts_name_localized._text,
                    "result_suit_name": mslist.primary_suit_by_part_id(result_id).ms_name_localized._text,
                    "base_part_name": part_param_table[base_id].parts_name_localized._text,
                    "base_suit_name": mslist.primary_suit_by_part_id(base_id).ms_name_localized._text,
                    "material_part_name": part_param_table[material_id].parts_name_localized._text,
                    "material_suit_name": mslist.primary_suit_by_part_id(material_id).ms_name_localized._text
                }
            )
    return recipes
