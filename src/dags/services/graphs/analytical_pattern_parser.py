import ast
from typing import Any

from jinja2 import Template

from configurations.analytical_pattern_templates.load_dataset import LOAD_DATASET_TEMPLATE
from configurations.analytical_pattern_templates.register_dataset import REGISTER_DATASET_TEMPLATE


class AnalyticalPatternParser:
    def __init__(self):
        pass

    def gen_register_dataset(self, values: dict[str, Any]) -> dict[str, Any]:
        template = Template(REGISTER_DATASET_TEMPLATE)
        return ast.literal_eval(template.render(**values))

    def gen_load_dataset(self, values: dict[str, Any]) -> dict[str, Any]:
        template = Template(LOAD_DATASET_TEMPLATE)
        return ast.literal_eval(template.render(**values))
