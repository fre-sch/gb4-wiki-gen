import logging
import tomllib
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import suppress
from pathlib import Path
from pprint import pprint
import click


from gb4_wiki_gen.database import load_data
from gb4_wiki_gen.generator.equip_page import collect_equipment, make_equip_page_content
from gb4_wiki_gen.generator.kit_page import make_kit_page_content
from gb4_wiki_gen.generator.suit_page import make_suit_page_content
from gb4_wiki_gen.models import DataTableIndexError
from gb4_wiki_gen.wiki_client import ApiSession
from gb4_wiki_gen.utils import slugify


log = logging.getLogger(__name__)


@click.group()
@click.argument("dir_path", type=click.Path(
    exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path))
@click.pass_context
def main(context, dir_path):
    context.ensure_object(dict)
    context.obj["config"] = tomllib.load(open("config.toml", "rb"))
    context.obj["registry"] = load_data(dir_path)


@main.command()
@click.argument("part_id")
@click.pass_context
def derives_into(context, part_id):
    """
    (debug) information about derives
    """
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
def suits_grades(context):
    """
    (debug) suit grades
    """
    registry = context.obj["registry"]
    mslist = registry["MSList"]
    for suit in mslist:
        grades = mslist.grade_variants(suit)
        print(f"{suit.id}, {grades}")


@main.command()
@click.pass_context
def suits_localized(context):
    """
    (debug) info on suits (main id, parts ids, gunpla box)
    """
    registry = context.obj["registry"]
    boxes = registry["ItemGunplaBox"]
    for suit in registry["MSList"]:
        try:
            box = boxes.find_by_suit_id(suit.id)
            box_id = box.id
            shop_price = box.shop_item.price
        except Exception:
            box_id = "-/-"
            shop_price = "-/-"
        try:
            parts_ids = " ".join(str(id) for id in suit.parts_ids)
        except Exception:
            pass
        try:
            name = " ".join(suit.ms_name_localized._text.split())
            print(suit.id, parts_ids, name, f"[{box_id} {shop_price}]")
        except DataTableIndexError:
            print(suit.id, parts_ids, "-/-", f"[{box_id} {shop_price}]")


@main.command()
@click.pass_context
def missions(context):
    """
    (debug) attempt to resolve mission part drops
    """
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
    """
    (incomplete) generate mission pages with drops
    """
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
@click.argument("suit_id", type=str, nargs=-1)
@click.option("--upload", is_flag=True, default=False)
@click.option("--dump", is_flag=True, default=False)
@click.option("--wiki-namespace", type=str, default="Generated")
@click.pass_context
def suit(context, suit_id, upload, dump, wiki_namespace):
    """
    generate mediawiki page for selected suit_ids or `all`, with optional upload
    """
    if not suit_id:
        return

    registry = context.obj["registry"]

    suit_ids = []
    if "all" in suit_id:
        suit_ids = [it for it in registry["MSList"].keys() if "HG_" in it]
    else:
        for it in suit_id:
            suit_ids.extend(it.split(" "))

    def try_make_pages(registry, suit_ids, wiki_namespace):
        for suit_id in suit_ids:
            try:
                yield make_suit_page_content(registry, suit_id, wiki_namespace)
            except DataTableIndexError as e:
                log.exception(f"failed making suit page {suit_id}")
            except Exception:
                log.exception(f"failed making suit page {suit_id}")

    pages = list(try_make_pages(registry, suit_ids, wiki_namespace))

    if pages and upload:
        csrf_token, wiki_client = _init_wiki_client(context.obj["config"])
        for page_title, page_content in pages:
            wiki_client.edit(csrf_token, page_title, page_content)
            log.info(f"Upload okay: {page_title}")
    elif dump:
        for page_title, page_content in pages:
            print(page_title, page_content)
            if not click.confirm("continue?", default=True):
                return
    else:
        for page_title, page_content in pages:
            log.info(page_title)


@main.command()
@click.argument("kit_id", type=str, nargs=-1)
@click.option("--upload", is_flag=True, default=False)
@click.option("--dump", is_flag=True, default=False)
@click.option("--wiki-namespace", type=str, default="Generated")
@click.pass_context
def kit(context, kit_id, upload, dump, wiki_namespace):
    """
    generate mediawiki page for selected kit_ids or `all`, with optional upload
    """
    if not kit_id:
        return

    registry = context.obj["registry"]

    kit_ids = []
    if "all" in kit_id:
        kit_ids = list(registry["ItemGunplaBox"].keys())
    else:
        for it in kit_id:
            kit_ids.extend(it.split(" "))

    def try_make_pages(registry, kit_ids, wiki_namespace):
        for kit_id in kit_ids:
            try:
                yield make_kit_page_content(registry, kit_id, wiki_namespace)
            except DataTableIndexError as e:
                if e.table_name == "ShopGoodsTable":
                    pass
                else:
                    log.exception(f"failed making kit {kit_id} page")
            except Exception:
                log.exception(f"failed making kit {kit_id} page")


    pages = list(try_make_pages(registry, kit_ids, wiki_namespace))

    if pages and upload:
        csrf_token, wiki_client = _init_wiki_client(context.obj["config"])
        for page_title, page_content in pages:
            wiki_client.edit(csrf_token, page_title, page_content)
            log.info(f"Upload okay: {page_title}")
    elif dump:
        for page_title, page_content in pages:
            print(page_title, page_content)
            if not click.confirm("continue?", default=True):
                return
    else:
        for page_title, page_content in pages:
            log.info(page_title)


@main.command()
@click.option("--upload", is_flag=True, default=False)
@click.option("--wiki-namespace", type=str, default="Generated")
@click.pass_context
def series(context, upload, wiki_namespace):
    """
    generate mediawiki category pages for series, with optional upload
    """
    registry = context.obj["registry"]
    pages = []

    for item in registry["localized_text_gundam_series"]:
        page_name = slugify(item._text)
        pages.append(
            (
                f"{wiki_namespace}:{page_name}",
                "<includeonly>\n"
                '<div class="series-include">\n'
                f"[[File:{wiki_namespace}:Series_Icon_{page_name}.png|left|frameless]]\n <span>[[{wiki_namespace}:{page_name}|{item._text}]]</span>\n"
                "</div>\n"
                "</includeonly>\n"
                "<noinclude>\n"
                f"= {item._text} =\n\n"
                "[[Category:Gundam Breaker 4]]\n"
                "[[Category:Series]]\n"
                "</noinclude>\n"
            )
        )

    if pages and upload:
        csrf_token, wiki_client = _init_wiki_client(context.obj["config"])
        for page_title, page_content in pages:
            wiki_client.edit(csrf_token, page_title, page_content)
            log.info(f"Upload okay: {page_title}")
    else:
        for page_title, page_content in pages:
            log.info(page_title)


@main.command()
@click.option("--upload", is_flag=True, default=False)
@click.option("--dump", is_flag=True, default=False)
@click.option("--wiki-namespace", type=str, default="Generated")
@click.pass_context
def equipment(context, upload, dump, wiki_namespace):
    """
    generate mediawiki pages for all equipment, with optional upload
    """
    registry = context.obj["registry"]

    def try_make_pages(registry, wiki_namespace):
        equip_params = collect_equipment(registry)
        for equip_id, entry in equip_params.items():
            try:
                yield make_equip_page_content(registry, entry, wiki_namespace)
            except Exception:
                log.exception(f"failed making equip page f{equip_id}")

    pages = list(try_make_pages(registry, wiki_namespace))

    if pages and upload:
        csrf_token, wiki_client = _init_wiki_client(context.obj["config"])
        pool = ThreadPoolExecutor(max_workers=4)
        for page_title, page_content in pages:
            pool.submit(_wiki_upload_page, wiki_client, csrf_token, page_title, page_content)

        pool.shutdown(wait=True)

    elif dump:
        for page_title, page_content in pages:
            print(page_title, page_content)
            if not click.confirm("continue?", default=True):
                return
    else:
        for page_title, page_content in pages:
            log.info(page_title)
        log.info(f"len pages: {len(pages)}")


def _init_wiki_client(config):
    if (
            "wiki_client" not in config
            or not config["wiki_client"].get("username")
            or not config["wiki_client"].get("password")
    ):
        raise Exception("missing 'wiki_client' in config, "
                        "excepted `[wiki_client]` section "
                        "with `username`, `password`")

    wiki_client_config = config["wiki_client"]
    wiki_client = ApiSession("https://gundambreaker.miraheze.org/w/")
    wiki_client.bot_login(wiki_client_config["username"], wiki_client_config["password"])
    csrf_token = wiki_client.csrf_token()
    return csrf_token, wiki_client


def _wiki_upload_page(wiki_client, csrf_token, page_title, page_content):
    wiki_client.edit(csrf_token, page_title, page_content)
    log.info(f"Upload okay: {page_title}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s %(name)s %(message)s"
    )
    main()