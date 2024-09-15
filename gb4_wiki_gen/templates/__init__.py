import jinja2

template_env = jinja2.Environment(
    loader=jinja2.PackageLoader("gb4_wiki_gen", "templates"),
    block_start_string="[%",
    block_end_string="%]",
    variable_start_string="[=",
    variable_end_string="]",
    comment_start_string="[#",
    comment_end_string="#]",
)