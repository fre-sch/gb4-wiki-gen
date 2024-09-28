import re
from functools import partial
from itertools import zip_longest

import jinja2
from gb4_wiki_gen.utils import slugify


template_env = jinja2.Environment(
    loader=jinja2.PackageLoader("gb4_wiki_gen", "templates"),
    block_start_string="[%",
    block_end_string="%]",
    variable_start_string="[=",
    variable_end_string="]",
    comment_start_string="[#",
    comment_end_string="#]",
)
template_env.filters["slugify"] = slugify


def fix_tags(value):
    if value is None or value == "":
        return

    pattern = r"<([^>]+)>([^<]+)</>"
    replace = r'<span class="gb4-localized-\1">\2</span>'
    value = re.sub(pattern, replace, value, flags=re.MULTILINE)

    pattern = r"<(SkillInfo[^>]+)>"
    replace = r'<span class="gb4-localized-\1"></span>'
    value = re.sub(pattern, replace ,value, flags=re.MULTILINE)

    value = re.sub(r"[^\w<>]+$", "", value)
    return value


template_env.filters["fix_tags"] = fix_tags


def tabulate(value):
    return zip_longest(*value, fillvalue=None)

template_env.filters["tabulate"] = tabulate