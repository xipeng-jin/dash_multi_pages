from typing import Literal

import dash_bootstrap_components as dbc
from dash import dcc, get_relative_path

from pydantic import Field

from dash_multi_pages.models import MultiPagesBaseModel
from dash_multi_pages.models._models_utils import _log_call


class Card(MultiPagesBaseModel):
    """Creates a card utilizing `dcc.Markdown` as title and text component.

    Args:
        type (Literal["card"]): Defaults to `"card"`.
        text (str): Markdown string to create card title/text that should adhere to the CommonMark Spec.
        href (str): URL (relative or absolute) to navigate to. If not provided the Card serves as a text card
            only. Defaults to `""`.

    """

    type: Literal["card"] = "card"
    text: str = Field(
        ...,
        description="Markdown string to create card title/text that should adhere to the CommonMark Spec.",
    )
    href: str = Field(
        "",
        description="URL (relative or absolute) to navigate to. If not provided the Card serves as a text card only.",
    )

    @_log_call
    def build(self):
        text = dcc.Markdown(
            self.text, className="card_text", dangerously_allow_html=False, id=self.id
        )
        card_content = (
            dbc.NavLink(
                text,
                href=(
                    get_relative_path(self.href)
                    if self.href.startswith("/")
                    else self.href
                ),
                className="card-link",
            )
            if self.href
            else text
        )
        card_class = "nav-card" if self.href else "card"
        return dbc.Card(card_content, className=card_class, id=f"{self.id}_outer")
