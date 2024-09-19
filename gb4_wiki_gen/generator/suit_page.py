from itertools import zip_longest

from slugify import slugify

from models import DataTableIndexError, DataEquipParameter, DataPartsParameter


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
        if "EX" in ability_type:
            ex_skills.append(item)

        elif "OP" in ability_type:
            op_skills.append(item)

        elif skill_data.hyper_trance_id != "None":
            awaken_skills.append(item)

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
    synthesis_recipes = []

    for item in suit.synthesis.synthesize_recipe_array:
        base = mslist[item["_SrcPartsId1"]].ms_name_localized._text
        material = mslist[item["_SrcPartsId2"]].ms_name_localized._text

        synthesis_recipes.append({
            "base_name": base,
            "base_page_uri": slugify(base),
            "material_name": material,
            "material_page_uri": slugify(material)
        })
    return synthesis_recipes


def make_derive_into_data(suit):
    mslist = suit.registry["MSList"]
    synthesis_table = suit.registry["DerivedSynthesizeParameter"]
    synthesis_recipes = []
    for item in synthesis_table:
        for recipe in item.synthesize_recipe_array:
            if suit.id in (recipe["_SrcPartsId1"], recipe["_SrcPartsId2"]):
                try:
                    result = mslist[item.target_parts_id].ms_name_localized._text
                    material_id = recipe["_SrcPartsId1"] if recipe["_SrcPartsId2"] == suit.id else recipe["_SrcPartsId2"]
                    material = mslist[material_id].ms_name_localized._text
                    synthesis_recipes.append({
                        "result_name": result,
                        "result_page_uri": slugify(result),
                        "material_name": material,
                        "material_page_uri": slugify(material)
                    })
                except DataTableIndexError as e:
                    print(e)
                    pass
    return synthesis_recipes
