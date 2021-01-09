from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import \
    ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import \
    RenderResultListAction
from ulauncher.api.shared.event import (ItemEnterEvent, KeywordQueryEvent,
                                        PreferencesEvent,
                                        PreferencesUpdateEvent)
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem


class RepoOpenerExtension(Extension):

    def __init__(self):
        super(RepoOpenerExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,
                       PreferencesUpdateEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        results = []

        return RenderResultListAction(results)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        pass


class PreferencesEventListener(EventListener):
    def on_event(self, event, extension):
        pass


class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event, extension):
        pass


if __name__ == "__main__":
    RepoOpenerExtension().run()
