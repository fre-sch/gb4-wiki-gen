from functools import partial
import re
import jinja2
from slugify import slugify


template_env = jinja2.Environment(
    loader=jinja2.PackageLoader("gb4_wiki_gen", "templates"),
    block_start_string="[%",
    block_end_string="%]",
    variable_start_string="[=",
    variable_end_string="]",
    comment_start_string="[#",
    comment_end_string="#]",
)
template_env.filters["slugify"] = partial(slugify, separator="_", lowercase=False)


def fix_tags(value):
    if value is None or value == "":
        return

    pattern = r"<([^>]+)>([^<]+)</>"
    replace = r'<span class="gb4-localized-\1">\2</span>'
    value = re.sub(pattern, replace, value, flags=re.MULTILINE)

    pattern = r"<(SkillInfo[^>]+)>"
    replace = r'<span class="gb4-localized-\1"></span>'
    value = re.sub(pattern, replace ,value, flags=re.MULTILINE)
    return value


template_env.filters["fix_tags"] = fix_tags