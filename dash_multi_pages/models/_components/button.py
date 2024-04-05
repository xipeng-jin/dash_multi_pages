from typing import List, Literal

import dash_bootstrap_components as dbc
from dash import html

from pydantic import Field

# from dash_multi_pages.models import Action, MultiPagesBaseModel
# from dash_multi_pages.models._action._actions_chain import _action_validator_factory

from dash_multi_pages.models import MultiPagesBaseModel
from dash_multi_pages.models._models_utils import _log_call


class Button(MultiPagesBaseModel):
    """Component provided to `Page` to trigger any defined `action` in `Page`.

    Args:
        type (Literal["button"]): Defaults to `"button"`.
        text (str): Text to be displayed on button. Defaults to `"Click me!"`.
        actions (List[Action]): See [`Action`][vizro.models.Action]. Defaults to `[]`.

    """

    type: Literal["button"] = "button"
    text: str = Field("Click me!", description="Text to be displayed on button.")
    # actions: List[Action] = []

    # Re-used validators
    # _set_actions = _action_validator_factory("n_clicks")

    @_log_call
    def build(self):
        return html.Div(
            dbc.Button(id=self.id, children=self.text, className="button_primary"),
            className="button_container",
            id=f"{self.id}_outer",
        )
