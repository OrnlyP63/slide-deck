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
    # --- existing ---
    "consulting": Theme(
        name="consulting",
        colors=ColorPalette(primary="#003366", secondary="#333333", accent="#C9A84C"),
        typography=Typography(),
    ),
    "minimal": Theme(
        name="minimal",
        colors=ColorPalette(primary="#000000", secondary="#222222", accent="#555555"),
        typography=Typography(),
    ),
    "dark": Theme(
        name="dark",
        colors=ColorPalette(primary="#1A1A2E", secondary="#E0E0E0", accent="#E94560", background="#16213E"),
        typography=Typography(),
    ),
    # --- audience themes ---
    "startup": Theme(
        name="startup",
        colors=ColorPalette(primary="#FF6B35", secondary="#2D2D2D", accent="#00D4AA", background="#FFFFFF", muted="#FFF4F0"),
        typography=Typography(),
    ),
    "academic": Theme(
        name="academic",
        colors=ColorPalette(primary="#5C1A1A", secondary="#444444", accent="#8B6914", background="#FAFAF8", muted="#F0EDE8"),
        typography=Typography(),
    ),
    "finance": Theme(
        name="finance",
        colors=ColorPalette(primary="#1B4332", secondary="#333333", accent="#52B788", background="#FFFFFF", muted="#F0F7F4"),
        typography=Typography(),
    ),
    "tech": Theme(
        name="tech",
        colors=ColorPalette(primary="#0F4C81", secondary="#4A4A4A", accent="#00B4D8", background="#F8F9FA", muted="#EEF3F8"),
        typography=Typography(),
    ),
    "government": Theme(
        name="government",
        colors=ColorPalette(primary="#1C2B4A", secondary="#3D3D3D", accent="#C0392B", background="#FFFFFF", muted="#F2F4F7"),
        typography=Typography(),
    ),
    "healthcare": Theme(
        name="healthcare",
        colors=ColorPalette(primary="#005B96", secondary="#444444", accent="#48CAE4", background="#F0F7FF", muted="#E0F0FF"),
        typography=Typography(),
    ),
    "creative": Theme(
        name="creative",
        colors=ColorPalette(primary="#6A0572", secondary="#333333", accent="#FFB703", background="#FFFDF7", muted="#F7F0FF"),
        typography=Typography(),
    ),
}


def get_theme(name: str) -> Theme:
    if name not in THEMES:
        raise ValueError(f"Unknown theme '{name}'. Available: {list(THEMES)}")
    return THEMES[name]


def register_theme(theme: Theme) -> None:
    THEMES[theme.name] = theme
