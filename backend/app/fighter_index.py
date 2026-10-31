import unicodedata

from .fighter_models import FighterRecord


def name_key(value):
    return " ".join(
        "".join(
            c
            for c in unicodedata.normalize("NFKD", value.casefold())
            if not unicodedata.combining(c)
        ).split()
    )


def metadata(payload):
    try:
        f = FighterRecord.model_validate(payload)
        from .fighters import validated

        validated(payload)
        return dict(
            search_name=name_key(f.name),
            competition_category=f.competition_division,
            career=f.career_status,
            stance_index=f.stance or "Unknown",
            division_index="|" + "|".join(sorted(d.name for d in f.division_history)) + "|",
            current_division_index=f.current_division or "",
            valid_index=True,
        )
    except (ValueError, TypeError):
        return dict(
            search_name="",
            competition_category="Unknown",
            career="Unknown",
            stance_index="Unknown",
            division_index="",
            current_division_index="",
            valid_index=False,
        )
