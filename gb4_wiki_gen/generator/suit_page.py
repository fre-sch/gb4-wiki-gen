from itertools import zip_longest

from slugify import slugify

from models import DataTableIndexError, DataEquipParameter, DataPartsParameter, \
    DataMSList
from templates import template_env


def make_skill_data(part_param: DataPartsParameter):
    ex_skills = []
    op_skills = []
    awaken_skills = []

    for skill_data in part_param.skill_array_data:
        ns, ability_type = skill_data.ability_cartridge_category.split("::")
        item = {
            "name": skill_data.ui_name_localized,
            "info": skill_data.ui_info_localized,
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
        return {}

    mslist = suit.registry["MSList"]
    part_param_table = suit.registry["PartsParameter"]
    synthesis_table = suit.registry["DerivedSynthesizeParameter"]
    recipes = {}

    for part_id in suit.unique_parts_ids:
        part_id = part_id.replace("MG_", "HG_")
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

    for part_id in suit.unique_parts_ids:
        part_id = part_id.replace("MG_", "HG_")
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


def make_box_price(grade, suit):
    registry = suit.registry
    boxes_table = registry["ItemGunplaBox"]
    if not suit.id.startswith(f"{grade}_"):
        try:
            gradeless_id = suit.id[3:]
            grade_suit_id = f"{grade}_{gradeless_id}"
            suit = registry["MSList"][grade_suit_id]
        except DataTableIndexError:
            return []
    boxes = []
    for box in boxes_table.find_by_parts_ids(suit.unique_parts_ids):
        try:
            boxes.append({
                "grade": grade,
                "name": box.name_localized,
                "price": box.shop_item.price
            })
        except DataTableIndexError:
            pass
    return boxes


def make_suit_page_content(registry, suit_id, wiki_namespace):
    template = template_env.get_template("suit_page.jinja2")
    mslist = registry["MSList"]
    suit = mslist[suit_id]
    page_slug = slugify(suit.ms_name_localized._text, separator="_", lowercase=False)
    page_title = f"{wiki_namespace}:{page_slug}"
    grade_hg, grade_mg, grade_sd = mslist.grade_variants(suit)
    unique_part_ids = suit.unique_parts_ids
    hg_box_price = make_box_price("HG", suit)
    mg_box_price = make_box_price("MG", suit)
    sd_box_price = make_box_price("SD", suit)

    page_content = template.render(
        WIKI_NAMESPACE=wiki_namespace,
        SUIT_NAME=suit.ms_name_localized._text,
        SUIT_NUMBER=suit.ms_number_localized._text,
        SERIES=suit.series_localized,
        GRADE_HG="HG" if grade_hg else "",
        GRADE_MG="MG" if grade_mg else "",
        GRADE_SD="SD" if grade_sd else "",
        BOX_HG=hg_box_price,
        BOX_MG=mg_box_price,
        BOX_SD=sd_box_price,
        DERIVE_ONLY=not (hg_box_price or mg_box_price or sd_box_price),
        PARTS=[
            (
                "Head", suit.head_part_params.parts_name_localized._text,
                make_skill_data(suit.head_part_params),
                suit.head in unique_part_ids
            ),
            (
                "Body", suit.body_part_params.parts_name_localized._text,
                make_skill_data(suit.body_part_params),
                suit.body in unique_part_ids
            ),
            (
                "ArmR", suit.arm_r_part_params.parts_name_localized._text,
                make_skill_data(suit.arm_r_part_params),
                suit.arm_r in unique_part_ids,
            ),
            (
                "ArmL", suit.arm_l_part_params.parts_name_localized._text,
                make_skill_data(suit.arm_l_part_params),
                suit.arm_l in unique_part_ids,
            ),
            (
                "Leg", suit.leg_part_params.parts_name_localized._text,
                make_skill_data(suit.leg_part_params),
                suit.leg in unique_part_ids,
            ),
            (
                "Backpack",
                suit.backpack_part_params.parts_name_localized._text,
                make_skill_data(suit.backpack_part_params),
                suit.backpack in unique_part_ids,
            ),
        ],
        EQUIP=[
            make_equip_data(suit.equip0_params),
            make_equip_data(suit.equip1_params),
            make_equip_data(suit.equip2_params),
            make_equip_data(suit.equip3_params),
            make_equip_data(suit.equip4_params),
            make_equip_data(suit.equip5_params),
            make_equip_data(suit.equip6_params),
            make_equip_data(suit.equip7_params),
        ],
        DERIVE_FROM=make_derive_from_data(suit),
        DERIVE_INTO=make_derive_into_data(suit),
    )
    return page_title, page_content
