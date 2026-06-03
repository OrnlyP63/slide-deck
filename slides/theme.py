from pydantic import BaseModel


class ColorPalette(BaseModel):
    primary: str = "#003366"
    secondary: str = "#333333"
    accent: str = "#C9A84C"
    background: str = "#FFFFFF"
    muted: str = "#F5F5F5"


class Typography(BaseModel):
    title_font: str = "helvet"
    body_font: str = "helvet"
    title_size: int = 20
    body_size: int = 11


class Theme(BaseModel):
    name: str
    colors: ColorPalette = ColorPalette()
    typography: Typography = Typography()
    beamer_theme: str = "default"


THEMES: dict[str, Theme] = {
    "consulting": Theme(
        name="consulting",
        colors=ColorPalette(primary="#003366", secondary="#333333", accent="#C9A84C"),
        typography=Typography(title_font="helvet", body_font="helvet"),
    ),
    "minimal": Theme(
        name="minimal",
        colors=ColorPalette(primary="#000000", secondary="#222222", accent="#555555"),
        typography=Typography(title_font="helvet", body_font="helvet"),
    ),
    "dark": Theme(
        name="dark",
        colors=ColorPalette(primary="#1A1A2E", secondary="#E0E0E0", accent="#E94560", background="#16213E"),
        typography=Typography(title_font="helvet", body_font="helvet"),
    ),
}


def get_theme(name: str) -> Theme:
    if name not in THEMES:
        raise ValueError(f"Unknown theme '{name}'. Available: {list(THEMES)}")
    return THEMES[name]


def register_theme(theme: Theme) -> None:
    THEMES[theme.name] = theme
