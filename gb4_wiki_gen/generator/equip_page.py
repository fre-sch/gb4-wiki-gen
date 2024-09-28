from models import DataEquipParameter, DataTableIndexError
from templates import template_env
from utils import slugify


def collect_equipment(registry):
    mslist = registry["MSList"]
    boxes = registry["ItemGunplaBox"]
    equipment = {}
    for suit in mslist:
        # check for valid suits
        try:
            suit.ms_name_localized._text
        except (DataTableIndexError, AttributeError):
            continue

        for equip in suit.equip_params:
            entry = equipment.setdefault(equip.parts_name.rstrip("L"), {})
            entry["equip"] = equip
            entry_suits = entry.setdefault("suits", {})
            entry_suits[suit.gradeless_id] = suit.ms_name_localized._text

    for box in boxes:
        try:
            box.name_localized
        except (DataTableIndexError, AttributeError):
            continue

        for equip in box.items_equip_parameters:
            if equip is None:
                continue
            entry = equipment.setdefault(equip.parts_name.rstrip("L"), {})
            entry["equip"] = equip
            entry_suits = entry.setdefault("kits", {})
            entry_suits[box.suit_id] = (box.box_art_id[:2], box.name_localized)

    return equipment



def make_equip_page_content(registry, entry, wiki_namespace):
    equip_param = entry["equip"]
    template = template_env.get_template("equip_page.jinja2")
    equip_type, equip_name, equip_skills = make_equip_data(equip_param)
    normal_skills, ex_skills, op_skills, awaken_skills = equip_skills
    page_slug = f"{wiki_namespace}:{slugify(equip_name)}"
    page_content = template.render(
        WIKI_NAMESPACE=wiki_namespace,
        PAGE_SLUG=page_slug,
        EQUIP_NAME=equip_name,
        EQUIP_SKILLS=equip_skills,
        EQUIP_TYPE=equip_type,
        SUITS=entry.get("suits", []),
        KITS=entry.get("kits", []),
        CATEGORY_WITH_EX=len(ex_skills) > 0,
        CATEGORY_WITH_OP=len(op_skills) > 0,
        CATEGORY_WITH_AWAKEN=len(awaken_skills) > 0
    )
    return page_slug, page_content


def make_equip_data(equip_params: DataEquipParameter):
    if equip_params is None:
        return None

    normal_skills = []
    ex_skills = []
    op_skills = []
    awaken_skills = []

    for skill_data in equip_params.skill_array_data:
        try:
            skill_data.ui_name_localized
            skill_data.ui_info_localized
            equip_params.name_localized
        except DataTableIndexError:
            continue
        ns, ability_type = skill_data.ability_cartridge_category.split("::")
        item = {
            "name": skill_data.ui_name_localized,
            "info": skill_data.ui_info_localized,
            "ability_type": ability_type,
        }
        if "NML_" in ability_type:
            normal_skills.append(item)

        elif "ORIGINAL" in ability_type:
            awaken_skills.append(item)

        elif "EX" in ability_type:
            ex_skills.append(item)

        elif "OP" in ability_type:
            op_skills.append(item)

    ns, equip_type = equip_params.parts_category.split("::")

    return equip_type, equip_params.name_localized, (normal_skills, ex_skills, op_skills, awaken_skills)
