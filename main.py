import os
import subprocess
import shutil

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

class CodeEditor(str):
    CODE = "code"
    WEBSTORM = "webstorm"
    PYCHARM = "pycharm"
    INTELLIJ = "intellij"
    GOLAND = "goland"
    RUSTROVER = "rustrover"
    RIDER = "rider"

class CodeEditorResolver:
    DEFAULT_EDITOR = CodeEditor.CODE

    LANGUAGE_EDITOR_MAP = {
        'python': CodeEditor.PYCHARM,
        'javascript': CodeEditor.WEBSTORM,
        'java': CodeEditor.INTELLIJ,
        'go': CodeEditor.GOLAND,
        'rust': CodeEditor.RUSTROVER,
        'csharp': CodeEditor.RIDER,
    }

    LANGUAGE_FILE_EXTENSIONS = {
        'python': ['.py'],
        'javascript': ['.js', '.jsx', '.ts', '.tsx'],
        'java': ['.java', '.kt', '.kts'],
        'csharp': ['.cs', '.sln'],
        'go': ['.go'],
        'rust': ['.rs'],
    }

    @staticmethod
    def detect_language(folder_path: str) -> set:
        language_counts = {language: 0 for language in CodeEditorResolver.LANGUAGE_FILE_EXTENSIONS}

        for _, _, files in os.walk(folder_path):
            for file in files:
                _, ext = os.path.splitext(file)
                for language, extensions in CodeEditorResolver.LANGUAGE_FILE_EXTENSIONS.items():
                    if ext in extensions:
                        language_counts[language] += 1

        languages_with_more_than_10_files = [lang for lang, count in language_counts.items() if count > 10]

        if len(languages_with_more_than_10_files) > 1:
            return "unknown"
        
        most_common_language = max(language_counts, key=language_counts.get, default=None)

        return most_common_language if language_counts[most_common_language] > 0 else "unknown"

    @staticmethod
    def get_editor(folder_path: str) -> str:
        language = CodeEditorResolver.detect_language(folder_path)
        editor = CodeEditorResolver.LANGUAGE_EDITOR_MAP[language] if language in CodeEditorResolver.LANGUAGE_EDITOR_MAP else CodeEditorResolver.DEFAULT_EDITOR
        return editor

class RepoOpenerExtension(Extension):
    tool_command_map = {
        'code': None,
        'intellij': None,
        'rider': None,
        'pycharm': None,
        'webstorm': None,
        'goland': None,
        'rustrover': None,
    }

    shorthand_tool_map = {
        'c': 'code',
        'i': 'intellij',
        'r': 'rider',
        'p': 'pycharm',
        'w': 'webstorm',
        'g': 'goland',
        'rr': 'rustrover'
    }

    search_path = None
    mono_repositories: str = None

    repos = []

    def __init__(self):
        super(RepoOpenerExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,
                       PreferencesUpdateEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def resolve_installed_tools(self):
        for tool, path in self.tool_command_map.items():
            self.tool_command_map[tool] = shutil.which(path if path is not None else tool)

    def find_and_store_local_git_repos(self):
        root_path = self.search_path
        repos = [{"path": folder_entry[0],
                  "name": os.path.basename(folder_entry[0]),
                  "tool": self.get_editor(folder_entry[0])
                  }
                 for folder_entry in os.walk(os.path.expandvars(root_path)) if ".git" in folder_entry[1]]
        
        if self.mono_repositories:
            for m in [x for x in self.mono_repositories.split(';') if x]:
                parts = m.split(':')
                if len(parts) != 2:
                    continue
                repo_name = parts[0]
                repo = next((repo for repo in repos if repo["name"].lower() == repo_name.lower()), None)
                if repo is None:
                    continue
                for f in [x for x in parts[1].split(',') if x]:
                    folder_path = os.path.join(repo["path"], f)
                    if os.path.isdir(folder_path):
                        repos.append({
                            "path": folder_path,
                            "name": repo["name"] + " - " + f,
                            "tool": self.get_editor(folder_path)
                        })

        self.repos = repos

    def get_editor(self, folder_path: str) -> str:
        editor = CodeEditorResolver.get_editor(folder_path)
        if self.tool_command_map[editor] is not None:
            return editor
        return CodeEditorResolver.DEFAULT_EDITOR


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
            extension.resolve_installed_tools()
            extension.find_and_store_local_git_repos()
        elif action == "open":
            repo = event_data["repo"]
            extension.open_repo(repo)


class PreferencesEventListener(EventListener):
    def on_event(self, event, extension: RepoOpenerExtension):
        extension.search_path = event.preferences["search_path"]
        extension.tool_command_map["code"] = event.preferences["vscode_command"]
        extension.tool_command_map["intellij"] = event.preferences["intellij_command"]
        extension.tool_command_map["rider"] = event.preferences["rider_command"]
        extension.tool_command_map["pycharm"] = event.preferences["pycharm_command"]
        extension.tool_command_map["webstrom"] = event.preferences["webstrom_command"]
        extension.tool_command_map["goland"] = event.preferences["goland_command"]
        extension.tool_command_map["rustrover"] = event.preferences["rustrover_command"]
        extension.mono_repositories = event.preferences["mono_repositories"]
        extension.resolve_installed_tools()
        extension.find_and_store_local_git_repos()


class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event, extension: RepoOpenerExtension):
        if event.id == "search_path" or "mono_repositories":
            extension.search_path = event.new_value
            extension.find_and_store_local_git_repos()
            return
        if event.id == "vscode_command":
            extension.tool_command_map["code"] = event.new_value
        elif event.id == "intellij_command":
            extension.tool_command_map["intellij"] = event.new_value
        elif event.id == "rider_command":
            extension.tool_command_map["rider"] = event.new_value
        elif event.id == "webstrom_command":
            extension.tool_command_map["webstrom"] = event.new_value
        elif event.id == "pycharm_command":
            extension.tool_command_map["pycharm"] = event.new_value
        elif event.id == "goland_command":
            extension.tool_command_map["goland"] = event.new_value
        elif event.id == "rustrover_command":
            extension.tool_command_map["rustrover"] = event.new_value
        
        extension.resolve_installed_tools()


if __name__ == "__main__":
    RepoOpenerExtension().run()
