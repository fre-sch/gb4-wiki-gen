from gb4_wiki_gen.templates import template_env
from gb4_wiki_gen.database import load_from_args
from slugify import slugify


def make_skill_data(registry, part_param):
    name_text = registry["localized_text_skill_name"]
    info_text = registry["localized_text_skill_info"]
    info_data = registry["SkillIdInfo"]
    template_data = []
    for skill in part_param.skill_array:
        skill_data = info_data[skill["_SkillId"]]
        template_data.append({
            "id": skill["_SkillId"],
            "is_ex_skill": "::EX" in skill_data.ability_cartridge_category,
            "is_op_skill": "::OP" in skill_data.ability_cartridge_category,
            "is_awaken_skill": skill_data.hyper_trance_id != "None",
            "name": name_text[skill["_SkillId"]]._text,
            "info": info_text[skill["_SkillId"]]._text
        })
    return template_data


if __name__ == "__main__":
    registry = load_from_args()
    template = template_env.get_template("suit_page.jinja2")

    mslist = registry["MSList"]
    suit = mslist["HG_1790"]
    ms_numbers = registry["localized_text_ms_number"]
    skill_names = registry["localized_text_skill_name"]
    skill_infos = registry["localized_text_skill_info"]
    skill_datas = registry["SkillIdInfo"]
    suit_slug = slugify(suit.head.localized_text_parts_name._text, separator="_")

    print(template.render(
        SUIT_NAME=suit.head.localized_text_parts_name._text,
        SUIT_NUMBER=ms_numbers[suit.id]._text,
        SUIT_SLUG=suit_slug,
        PAGE_URI=f"Generated:{suit_slug}",
        PARTS=[
            ("{{GB4PartHead}}", make_skill_data(registry, suit.head.PartsParameter)),
            ("{{GB4PartBody}}", make_skill_data(registry, suit.body.PartsParameter)),
            ("{{GB4PartArmR}}", make_skill_data(registry, suit.arm_r.PartsParameter)),
            ("{{GB4PartArmL}}", make_skill_data(registry, suit.arm_l.PartsParameter)),
            ("{{GB4PartLeg}}", make_skill_data(registry, suit.leg.PartsParameter)),
            ("{{GB4PartBackpack}}", make_skill_data(registry, suit.backpack.PartsParameter)),
        ]
    ))
