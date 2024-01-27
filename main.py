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
        'code': None,
        'intellij': None
    }

    shorthand_tool_map = {
        'c': 'code',
        'i': 'intellij'
    }

    search_path = None

    repos = []

    def __init__(self):
        super(RepoOpenerExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,
                       PreferencesUpdateEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def find_and_store_local_git_repos(self):
        root_path = self.search_path
        repos = [{"path": folder_entry[0],
                  "subdirs": folder_entry[1],
                  "name": os.path.basename(folder_entry[0]),
                  "tool": "intellij" if ".idea" in folder_entry[1] else "code"
                  }
                 for folder_entry in os.walk(os.path.expandvars(root_path)) if ".git" in folder_entry[1]]

        self.repos = repos

    def open_repo(self, repo):
        path = repo["path"]
        tool = self.tool_command_map[repo["tool"]]

        subprocess.Popen([tool, path])


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension: RepoOpenerExtension):
        query = event.get_argument() or ""

        if not query:
            return RenderResultListAction([self.gen_refresh_item()])

        splitted_query = query.split(':')
        if len(splitted_query) > 2:
            name = "You may only have 1 x ':' in your query."
            description = "Adjust your query."
            return RenderResultListAction([self.gen_result_item(name, description)])

        has_custom_tool = len(splitted_query) == 2
        tool = None
        search_term = query
        if has_custom_tool:
            tool_alias = splitted_query[0]
            tool = extension.shorthand_tool_map.get(tool_alias)
            search_term = splitted_query[1]
            if not tool:
                name = "The given tool shorthand does not exist."
                description = "Use another shorthand."
                return RenderResultListAction([self.gen_result_item(name, description)])

        repos = [repo.copy() for repo in extension.repos if search_term.lower()
                 in repo["name"].lower()]

        if has_custom_tool:
            for repo in repos:
                repo["tool"] = tool

        results = [self.gen_repo_item(repo) for repo in repos]

        return RenderResultListAction(results)

    def gen_repo_item(self, repo):
        icon = repo["tool"]
        open_action = ExtensionCustomAction({"action": "open", "repo": repo})
        return ExtensionResultItem(icon=f"images/{icon}.png",
                                   name=repo["name"],
                                   description=repo["path"],
                                   on_enter=open_action)

    def gen_refresh_item(self):
        name = "Renew cache"
        description = "Otherwise type to start looking through your repos."
        refresh_action = ExtensionCustomAction({"action": "refresh"})
        return ExtensionResultItem(icon="images/icon.png",
                                   name=name,
                                   description=description,
                                   on_enter=refresh_action)

    def gen_result_item(self, name, description):
        return ExtensionResultItem(icon="images/icon.png",
                                   name=name,
                                   description=description,
                                   on_enter=HideWindowAction())


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension: RepoOpenerExtension):
        event_data = event.get_data()
        action = event_data["action"]

        if action == "refresh":
            extension.find_and_store_local_git_repos()
        elif action == "open":
            repo = event_data["repo"]
            extension.open_repo(repo)


class PreferencesEventListener(EventListener):
    def on_event(self, event, extension: RepoOpenerExtension):
        extension.search_path = event.preferences["search_path"]
        extension.tool_command_map["code"] = event.preferences["vscode_command"]
        extension.tool_command_map["intellij"] = event.preferences["intellij_command"]
        extension.find_and_store_local_git_repos()


class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event, extension: RepoOpenerExtension):
        if event.id == "search_path":
            extension.search_path = event.new_value
            extension.find_and_store_local_git_repos()
        elif event.id == "vscode_command":
            extension.tool_command_map["code"] = event.new_value
        elif event.id == "intellij_command":
            extension.tool_command_map["intellij"] = event.new_value
        else:
            pass


if __name__ == "__main__":
    RepoOpenerExtension().run()
