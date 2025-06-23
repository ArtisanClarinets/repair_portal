# --- File: apps/repair_portal/scripts/a11y_check.py ---
"""Simple luminance contrast checker for theme audit."""
# Updated: 2025-07-12
# Version: 1.0
# Purpose: Ensure text and background colors meet WCAG 2.1 AA.

from __future__ import annotations

from pathlib import Path


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    value = value.lstrip("#")
    lv = len(value)
    return tuple(int(value[i : i + lv // 3], 16) / 255 for i in range(0, lv, lv // 3))


def luminance(rgb: tuple[float, float, float]) -> float:
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    r, g, b = channel(r), channel(g), channel(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    l1 = luminance(hex_to_rgb(fg)) + 0.05
    l2 = luminance(hex_to_rgb(bg)) + 0.05
    return max(l1, l2) / min(l1, l2)


def main() -> None:
    css = Path("repair_portal/public/css/theme.css").read_text()
    colors = [line.split(":")[1].strip(" ;") for line in css.splitlines() if line.startswith("  --clr")]
    primary, accent, neutral = colors[:3]
    pairs = [("primary", primary, neutral), ("accent", accent, neutral)]
    for name, fg, bg in pairs:
        ratio = contrast_ratio(fg, bg)
        status = "PASS" if ratio >= 4.5 else "FAIL"
        print(f"{name} on neutral: {ratio:.2f} ({status})")


if __name__ == "__main__":
    main()
