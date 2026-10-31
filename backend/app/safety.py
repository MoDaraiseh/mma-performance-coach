"""Conservative lexical screens, not medical triage or comprehensive intent detection."""

import re


def unsafe_weight_goal(text):
    text = text.casefold()
    return bool(
        re.search(
            r"dehydrat|water[ -](?:cut|load)|weight[ -]cut|cut(?:ting)? weight|"
            r"rapid (?:weight|fat)|(?:crash|starvation) diet|starv|"
            r"lose weight (?:fast|quick)|(?:lose|drop|cut).{0,35}(?:overnight|tomorrow|in \d+ days)|"
            r"sauna|diuretic|laxative",
            text,
        )
    )
