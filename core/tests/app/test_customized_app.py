import asyncio
from unittest.mock import Mock

import pytest

import toga


class CustomizedApp(toga.App):
    def startup(self):
        self.main_window = toga.MainWindow()
        # Create a secondary simple window as part of app startup to verify
        # that toolbar handling is skipped.
        self.other_window = toga.Window()

        self._mock_open = Mock()
        self._mock_preferences = Mock()

    def open(self, path):
        self._mock_open(path)

    def preferences(self):
        self._mock_preferences()


class AsyncCustomizedApp(CustomizedApp):
    # A custom app where preferences and document-management commands are user-defined
    # as async handlers.

    async def preferences(self):
        self._mock_preferences()


@pytest.mark.parametrize(
    "AppClass",
    [
        CustomizedApp,
        AsyncCustomizedApp,
    ],
)
def test_create(event_loop, AppClass):
    """An app with overridden commands can be created"""
    custom_app = AppClass("Custom App", "org.beeware.customized-app")

    assert custom_app.formal_name == "Custom App"
    assert custom_app.app_id == "org.beeware.customized-app"
    assert custom_app.app_name == "customized-app"

    # The default implementations of the on_running and on_exit handlers
    # have been wrapped as simple handlers
    assert custom_app.on_running._raw.__func__ == toga.App.on_running
    assert custom_app.on_exit._raw.__func__ == toga.App.on_exit

    # About menu item exists and is disabled
    assert toga.Command.ABOUT in custom_app.commands
    assert custom_app.commands[toga.Command.ABOUT].enabled

    # Preferences exist and are enabled
    assert toga.Command.PREFERENCES in custom_app.commands
    assert custom_app.commands[toga.Command.PREFERENCES].enabled

    # A change handler has been added to the MainWindow's toolbar CommandSet
    assert custom_app.main_window.toolbar.on_change is not None


def test_open_menu(event_loop):
    """The custom preferences method is activated by the preferences menu"""
    custom_app = CustomizedApp("Custom App", "org.beeware.customized-app")

    file_path = Mock()
    custom_app._impl.dialog_responses["OpenFileDialog"] = [file_path]

    result = custom_app.commands[toga.Command.OPEN].action()
    if asyncio.isfuture(result):
        custom_app.loop.run_until_complete(result)
    custom_app._mock_open.assert_called_once_with(file_path)


@pytest.mark.parametrize(
    "AppClass",
    [
        CustomizedApp,
        AsyncCustomizedApp,
    ],
)
def test_preferences_menu(event_loop, AppClass):
    """The custom preferences method is activated by the preferences menu"""
    custom_app = AppClass("Custom App", "org.beeware.customized-app")

    result = custom_app.commands[toga.Command.PREFERENCES].action()
    if asyncio.isfuture(result):
        custom_app.loop.run_until_complete(result)
    custom_app._mock_preferences.assert_called_once_with()
