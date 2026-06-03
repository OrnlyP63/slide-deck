from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from slides.model import SlideBase
from slides.theme import Theme


def _to_snake(name: str) -> str:
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z])([A-Z])", r"\1_\2", s)
    return s.lower()


class Renderer:
    def __init__(self, templates_dir: Path | None = None) -> None:
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "templates"
        env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )
        env.filters["latex_escape"] = self.latex_escape
        self._env = env

    def render(self, slides: list[SlideBase], theme: Theme, deck_title: str = "", author: str = "") -> str:
        rendered = [self._render_slide(s) for s in slides]
        return self._env.get_template("deck.tex.j2").render(
            slides_content=rendered,
            theme=theme,
            deck_title=deck_title,
            author=author,
        )

    def _render_slide(self, slide: SlideBase) -> str:
        template_name = f"slides/{_to_snake(type(slide).__name__)}.tex.j2"
        return self._env.get_template(template_name).render(**slide.model_dump())

    @staticmethod
    def latex_escape(text: str) -> str:
        if not text:
            return text
        for old, new in [
            ("\\", r"\textbackslash{}"),
            ("&",  r"\&"),
            ("%",  r"\%"),
            ("$",  r"\$"),
            ("#",  r"\#"),
            ("_",  r"\_"),
            ("{",  r"\{"),
            ("}",  r"\}"),
            ("~",  r"\textasciitilde{}"),
            ("^",  r"\textasciicircum{}"),
        ]:
            text = text.replace(old, new)
        return text
