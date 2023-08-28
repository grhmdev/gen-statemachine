import logging
from pathlib import Path
from mako.template import Template
from mako.lookup import TemplateLookup
from mako.runtime import Context
from mako import exceptions
from io import StringIO

from gen_statemachine.model import StateMachine

LOGGER = logging.getLogger(__name__)


class MakoRenderer:
    def __init__(self, template_dir: Path, statemachine_model: StateMachine):
        self.template_lookup = TemplateLookup(directories=[template_dir])
        self.statemachine = statemachine_model

    def render_template(self, template_str: str) -> str:
        buffer = StringIO()
        context = Context(buffer, statemachine=self.statemachine)
        template = Template(template_str, lookup=self.template_lookup)
        try:
            template.render_context(context)
        except Exception as e:
            LOGGER.error(exceptions.text_error_template().render())
            raise e

        return buffer.getvalue()
