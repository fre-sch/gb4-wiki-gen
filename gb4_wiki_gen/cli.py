from contextlib import suppress
from pathlib import Path
from pprint import pprint

from gb4_wiki_gen.templates import template_env
from gb4_wiki_gen.database import load_data
from slugify import slugify
import click

from generator.suit_page import make_derive_into_data, make_derive_from_data, \
    make_equip_data, make_skill_data
from models import DataTableIndexError
from wiki_client import ApiSession


@click.group()
@click.argument("dir_path", type=click.Path(
    exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path))
@click.pass_context
def main(context, dir_path):
    context.ensure_object(dict)
    context.obj["registry"] = load_data(dir_path)


@main.command()
@click.argument("part_id")
@click.pass_context
def derives_into(context, part_id):
    registry = context.obj["registry"]
    derive_table = registry["DerivedSynthesizeParameter"]
    part_name_table = registry["localized_text_parts_name"]
    recipes = derive_table.find_derives_into(part_id)
    recipes_named = []
    for t, s1, s2 in recipes:
        t_name = part_name_table[t]._text
        s1_name = part_name_table[s1]._text
        s2_name = part_name_table[s2]._text
        recipes_named.append((
            f"{t} {t_name}", f"{s1} {s1_name}", f"{s2} {s2_name}"
        ))

    pprint(recipes_named)


@main.command()
@click.pass_context
def missions(context):
    registry = context.obj["registry"]
    mission_list_table = registry["MissionListTable"]
    operations = {}
    for item in mission_list_table:
        op = operations.setdefault(item.operation_mission_id, [])
        op.append(f"{item.id} {item.mission_comments}")
    pprint(operations)


@main.command()
@click.pass_context
def mission_rewards(context):
    registry = context.obj["registry"]
    mission_reward_table = registry["MissionRewardTable"]
    suit_names = registry["localized_text_preset_character_name"]
    bpart_names = registry["localized_text_bparts_name"]
    part_names = registry["localized_text_parts_name"]
    weapon_names = registry["localized_text_weapon_name"]
    shield_names = registry["localized_text_shield_name"]
    story_names = registry["localized_text_story_title_name"]

    def get_reward_name(reward_id):
        with suppress(Exception):
            return suit_names[reward_id]._text
        with suppress(Exception):
            return part_names[reward_id]._text
        with suppress(Exception):
            return weapon_names[reward_id]._text
        with suppress(Exception):
            return shield_names[reward_id]._text
        with suppress(Exception):
            return bpart_names[reward_id]._text
        return reward_id

    def get_mission_name(mission_reward_id: str) -> str:
        try:
            story_name_key = mission_reward_id.replace("MissionReward", "TextId")
            return story_names[story_name_key]._text
        except DataTableIndexError:
            return mission_reward_id

    print("= Mission Rewards =")
    for reward_id, mission_list in mission_reward_table.reward_item_mapped.items():
        reward_name = str(get_reward_name(reward_id)).replace("\n", " ")

        print(f"== {reward_name} ==")
        for mission_id in mission_list:
            mission_name = get_mission_name(mission_id)
            if mission_name == mission_id:
                print(f"* {mission_name}")
            else:
                print(f"* '''{mission_name}''' ")


@main.command()
@click.argument("suit_id", type=str)
@click.option("--upload", type=bool, default=False)
@click.option("--username", type=str)
@click.option("--password", type=str)
@click.pass_context
def suit(context, suit_id, upload, username, password):
    if not suit_id:
        return

    registry = context.obj["registry"]
    template = template_env.get_template("suit_page.jinja2")
    mslist = registry["MSList"]
    suit = mslist[suit_id]
    wiki_namespace="Generated"
    page_slug = slugify(suit.ms_name_localized._text, separator="_")
    page_title = f"{wiki_namespace}:{page_slug}"
    page_content = template.render(
        WIKI_NAMESPACE=wiki_namespace,
        SUIT_NAME=suit.ms_name_localized._text,
        SUIT_NUMBER=suit.ms_number_localized._text,
        PARTS=[
            ("Head", suit.head_part_params.parts_name_localized._text, make_skill_data(suit.head_part_params)),
            ("Body", suit.body_part_params.parts_name_localized._text, make_skill_data(suit.body_part_params)),
            ("ArmR", suit.arm_r_part_params.parts_name_localized._text, make_skill_data(suit.arm_r_part_params)),
            ("ArmL", suit.arm_l_part_params.parts_name_localized._text, make_skill_data(suit.arm_l_part_params)),
            ("Leg", suit.leg_part_params.parts_name_localized._text, make_skill_data(suit.leg_part_params)),
            ("Backpack", suit.backpack_part_params.parts_name_localized._text, make_skill_data(suit.backpack_part_params)),
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
    if upload and username and password:
        wiki_client = ApiSession("https://gundambreaker.miraheze.org/w/")
        wiki_client.bot_login(username, password)
        csrf_token = wiki_client.csrf_token()
        response = wiki_client.edit(csrf_token, page_title, page_content)
        print(page_title)
    else:
        print(page_content)



if __name__ == "__main__":
    main()