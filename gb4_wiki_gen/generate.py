from pathlib import Path

from gb4_wiki_gen.templates import template_env
from gb4_wiki_gen.database import load_from_args, load_data
from slugify import slugify
from itertools import zip_longest
import click

from models import DataPartsParameter, DataEquipParameter


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

        elif skill_data.hyper_trance_id != "None":
            awaken_skills.append(item)

    ns, equip_type = equip_params.parts_category.split("::")
    equip_name = equip_params.name_localized._text

    return equip_type, equip_name, list(zip_longest(normal_skills, ex_skills, op_skills, awaken_skills, fillvalue=None))


@click.group()
@click.argument("dir_path", type=click.Path(
    exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path))
@click.pass_context
def main(context, dir_path):
    context.ensure_object(dict)
    context.obj["registry"] = load_data(dir_path)


@main.command()
@click.argument("suit_id", type=str)
@click.pass_context
def suit(context, suit_id):
    registry = context.obj["registry"]
    template = template_env.get_template("suit_page.jinja2")
    mslist = registry["MSList"]
    # HG_1790
    # MG_1540
    suit = mslist[suit_id]
    suit_slug = slugify(suit.ms_name_localized._text, separator="_")

    print(template.render(
        SUIT_NAME=suit.ms_name_localized._text,
        SUIT_NUMBER=suit.ms_number_localized._text,
        SUIT_SLUG=suit_slug,
        PAGE_URI=f"Generated:{suit_slug}",
        PARTS=[
            ("Head", make_skill_data(suit.head_part_params)),
            ("Body", make_skill_data(suit.body_part_params)),
            ("ArmR", make_skill_data(suit.arm_r_part_params)),
            ("ArmL", make_skill_data(suit.arm_l_part_params)),
            ("Leg", make_skill_data(suit.leg_part_params)),
            ("Backpack", make_skill_data(suit.backpack_part_params)),
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
        ]
    ))


if __name__ == "__main__":
    main()