from slugify import slugify

from models import DataTableIndexError, DataPartsParameter, \
    DataMSList
from templates import template_env


def make_part_skill_data(part_param: DataPartsParameter):
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
    if ex_skills or op_skills or awaken_skills:
        return ex_skills, op_skills, awaken_skills
    return None


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
    unique_parts_ids = suit.unique_parts_ids
    for box in boxes_table.find_by_parts_ids(unique_parts_ids):
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
            make_part_data("Head", suit.head, suit.head_part_params, unique_part_ids),
            make_part_data("Body", suit.body, suit.body_part_params, unique_part_ids),
            make_part_data("ArmR", suit.arm_r, suit.arm_r_part_params, unique_part_ids,),
            make_part_data("ArmL", suit.arm_l, suit.arm_l_part_params, unique_part_ids),
            make_part_data("Leg", suit.leg, suit.leg_part_params, unique_part_ids),
            make_part_data("Backpack", suit.backpack, suit.backpack_part_params, unique_part_ids),
        ],
        EQUIP=[
            equip.name_localized
            for equip in suit.equip_params
        ],
        DERIVE_FROM=make_derive_from_data(suit),
        DERIVE_INTO=make_derive_into_data(suit),
    )
    return page_title, page_content


def make_part_data(part_type, part, part_params, unique_part_ids):
    if part is None:
        return None
    return (
        part_type,
        part_params.parts_name_localized._text,
        make_part_skill_data(part_params),
        part in unique_part_ids,
    )
