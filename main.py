import os
import subprocess

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

    tool_command_map = {
        'code': 'code-insiders',
        'intellij': 'intellij-idea-ultimate'
    }

    def __init__(self):
        super(RepoOpenerExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,
                       PreferencesUpdateEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def fill_cache(self):
        self.repos = self.find_local_git_repos()

    def find_local_git_repos(self):
        root_path = self.search_path
        repos = [{"path": folder_entry[0],
                  "subdirs": folder_entry[1],
                  "name": os.path.basename(folder_entry[0])}
                 for folder_entry in os.walk(os.path.expandvars(root_path)) if ".git" in folder_entry[1]]

        for repo in repos:
            tool = "code"
            if ".idea" in repo["subdirs"]:
                tool = "intellij"

            repo["tool"] = tool

        return repos

    def open_repo(self, repo):
        path = repo["path"]
        tool = self.tool_command_map[repo["tool"]]

        subprocess.Popen([tool, path])


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or ""

        results = [self.gen_repo_item(
            repo) for repo in extension.repos if query.lower() in repo["name"]]
        return RenderResultListAction(results)

    def gen_repo_item(self, repo):
        icon = repo["tool"]
        open_action = ExtensionCustomAction({"action": "open", "repo": repo})
        return ExtensionResultItem(icon=f"images/{icon}.png",
                                   name=repo["name"],
                                   description=repo["path"],
                                   on_enter=open_action)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        event_data = event.get_data()
        action = event_data["action"]

        if action == "open":
            repo = event_data["repo"]
            extension.open_repo(repo)


class PreferencesEventListener(EventListener):
    def on_event(self, event, extension):
        extension.search_path = event.preferences["search_path"]
        extension.fill_cache()


class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event, extension):
        if event.id == "search_path":
            extension.search_path = event.new_value
            extension.fill_cache()


if __name__ == "__main__":
    RepoOpenerExtension().run()
