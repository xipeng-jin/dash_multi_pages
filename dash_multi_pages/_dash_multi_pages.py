import logging
from pathlib import Path
from typing import List

import dash
import dash_bootstrap_components as dbc
import flask

from dash_multi_pages._constants import STATIC_URL_PREFIX
from dash_multi_pages.managers import data_manager, model_manager
from dash_multi_pages.models import Dashboard

logger = logging.getLogger(__name__)


class DashMultiPages:
    """The main class of the `dash_multi_pages` package."""

    def __init__(self, **kwargs):
        """Initializes Dash app, stored in `self.dash`.

        Args:
            kwargs: Passed through to `Dash.__init__`, e.g. `assets_folder`, `url_base_pathname`. See
                [Dash documentation](https://dash.plotly.com/reference#dash.dash) for possible arguments.

        """
        self.dash = dash.Dash(**kwargs, use_pages=True, pages_folder="", title="DashMultiPages")
        self.dash.config.external_stylesheets.extend(
            [
                "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined",
                # Bootstrap theme has no effect on styling as it gets overwritten by our CSS. However, it is
                # necessary to add a default theme here so that added dbc components work properly.
                dbc.themes.BOOTSTRAP,
            ]
        )

        # Include dash_multi_pages assets (in the static folder) as external scripts and stylesheets. We extend self.dash.config
        # objects so the user can specify additional external_scripts and external_stylesheets via kwargs.
        dash_multi_pages_assets_folder = Path(__file__).with_name("static")
        requests_pathname_prefix = self.dash.config.requests_pathname_prefix
        dash_multi_pages_css = [requests_pathname_prefix + path for path in self._get_external_assets(dash_multi_pages_assets_folder, "css")]
        dash_multi_pages_js = [
            {"src": requests_pathname_prefix + path, "type": "module"}
            for path in self._get_external_assets(dash_multi_pages_assets_folder, "js")
        ]
        self.dash.config.external_stylesheets.extend(dash_multi_pages_css)
        self.dash.config.external_scripts.extend(dash_multi_pages_js)

        # Serve all assets (including files other than css and js) that live in dash_multi_pages_assets_folder at the
        # route /dash_multi_pages. Based on code in Dash.init_app that serves assets_folder. This respects the case that the
        # dashboard is not hosted at the root of the server, e.g. http://www.example.com/dashboard/dash_multi_pages.
        routes_pathname_prefix = self.dash.config.routes_pathname_prefix
        blueprint_prefix = routes_pathname_prefix.replace("/", "_").replace(".", "_")
        self.dash.server.register_blueprint(
            flask.Blueprint(
                f"{blueprint_prefix}dash_multi_pages_assets",
                self.dash.config.name,
                static_folder=dash_multi_pages_assets_folder,
                static_url_path=routes_pathname_prefix + STATIC_URL_PREFIX,
            )
        )

    def build(self, dashboard: Dashboard):
        """Builds the `dashboard`.

        Args:
            dashboard (Dashboard): [`Dashboard`][dash_multi_pages.models.Dashboard] object.

        Returns:
            DashMultiPages: App object

        """
        # Note Dash.index uses self.dash.title instead of self.dash.app.config.title.
        if dashboard.title:
            self.dash.title = dashboard.title

        # Note that model instantiation and pre_build are independent of Dash.
        self._pre_build()

        self.dash.layout = dashboard.build()

        return self

    def run(self, *args, **kwargs):  # if type annotated, mkdocstring stops seeing the class
        """Runs the dashboard.

        Args:
            args: Passed through to `dash.run`.
            kwargs: Passed through to `dash.run`.

        """
        data_manager._frozen_state = True
        model_manager._frozen_state = True

        self.dash.run(*args, **kwargs)

    @staticmethod
    def _pre_build():
        """Runs pre_build method on all models in the model_manager."""
        # Note that a pre_build method can itself add a model (e.g. an Action) to the model manager, and so we need to
        # iterate through set(model_manager) rather than model_manager itself or we loop through something that
        # changes size.
        # Any models that are created during the pre-build process *will not* themselves have pre_build run on them.
        # In future may add a second pre_build loop after the first one.
        for model_id in set(model_manager):
            model = model_manager[model_id]
            if hasattr(model, "pre_build"):
                model.pre_build()

    @staticmethod
    def _reset():
        """Private method that clears all state in the `DashMultiPages` app."""
        data_manager._clear()
        model_manager._clear()
        dash._callback.GLOBAL_CALLBACK_LIST = []
        dash._callback.GLOBAL_CALLBACK_MAP = {}
        dash._callback.GLOBAL_INLINE_SCRIPTS = []
        dash.page_registry.clear()
        dash._pages.CONFIG.clear()
        dash._pages.CONFIG.__dict__.clear()

    @staticmethod
    def _get_external_assets(folder: Path, extension: str) -> List[str]:
        """Returns a list of paths to assets with given `extension` in `folder`, prefixed with `STATIC_URL_PREFIX`.

        e.g. with STATIC_URL_PREFIX="dash_multi_pages", extension="css", folder="/path/to/dash_multi_pages/static",
        we will get ["dash_multi_pages/css/accordion.css", "dash_multi_pages/css/button.css", ...].
        """
        return sorted(
            (STATIC_URL_PREFIX / path.relative_to(folder)).as_posix() for path in folder.rglob(f"*.{extension}")
        )
