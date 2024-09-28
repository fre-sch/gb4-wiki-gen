from templates import template_env
from slugify import slugify
from gb4_wiki_gen.generator.suit_page import make_part_skill_data
from generator.equip_page import make_equip_data


def make_kit_page_content(registry, kit_id, wiki_namespace):
    template = template_env.get_template("kit_page.jinja2")
    kits_table = registry["ItemGunplaBox"]
    kit = kits_table[kit_id]
    kit_grade = kit.box_art_id[:2]
    page_slug = slugify(kit.name_localized, separator="_", lowercase=False)
    page_title = f"{wiki_namespace}:Kit_{kit_grade}_{page_slug}"

    page_content = template.render(
        WIKI_NAMESPACE=wiki_namespace,
        KIT_NAME=kit.name_localized,
        KIT_PRICE=kit.shop_item.price,
        KIT_GRADE=kit_grade,
        KIT_PARTS=make_kit_parts(kit),
        KIT_EQUIP=make_kit_equip(kit),
        SERIES=kit.gundam_series_name_localized._text
    )
    return page_title, page_content


def make_kit_parts(kit):
    parts = []
    for part in kit.items_parts_parameters:
        if part is None:
            continue
        part_type = part.other["_PerformanceGroupName"].replace("Parts", "")
        part_name = part.parts_name_localized._text
        suit = kit.registry["MSList"].primary_suit_by_part_id(part)
        suit_name = suit.ms_name_localized._text
        parts.append(
            (part_type, part_name, suit_name, make_part_skill_data(part))
        )
    return parts


def make_kit_equip(kit):
    parts = []
    for equip in kit.items_equip_parameters:
        if equip is None:
            continue
        parts.append(make_equip_data(equip))
    return parts