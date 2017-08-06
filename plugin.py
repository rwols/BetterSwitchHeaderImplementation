import sublime_plugin
import sublime
import os


class bidict(dict):
    def __init__(self):
        super(bidict, self).__init__()
        self.inverse = {}

    def __setitem__(self, key, value):
        if key in self:
            self.inverse[self[key]].remove(key)
        super(bidict, self).__setitem__(key, value)
        self.inverse[value] = key

    def __delitem__(self, key):
        self.inverse.setdefault(self[key], "").remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]:
            del self.inverse[self[key]]
        super(bidict, self).__delitem__(key)


class BetterSwitchHeaderImplementationCommand(sublime_plugin.WindowCommand):

    _cache = bidict()

    def run(self, extensions):

        view = self.window.active_view()
        if not view:
            return
        self.fn = view.file_name()
        if not self.fn:
            return
        result = self.__class__._cache.get(self.fn, None)
        if result:
            self.window.run_command("open_file", {"file": result})
            return
        result = self.__class__._cache.inverse.get(self.fn, None)
        if result:
            self.window.run_command("open_file", {"file": result})
            return

        self.basedir, self.basename = os.path.split(self.fn)
        self.name, self.ext = os.path.splitext(self.basename)
        if self.ext != "" and self.ext[1:] not in extensions:
            return

        self.extensions = tuple(extensions)  # so we can use it with .endswith

        if "project_path" in self.window.extract_variables():
            # we're in a sublime project.
            self._project_mode()
        else:
            self._folder_mode()

    def _folder_mode(self):
        self.dirs_visited = set()  # dont visit dirs twice
        # use a sanity limit
        count = 0
        sanity_limit = sublime.load_settings(
            "BetterSwitchHeaderImplementation.sublime-settings").get(
                "sanity_limit", 3)
        result = self._find_folder_mode(self.basedir)
        self.deeper = True
        while (not result) and (count < sanity_limit) and self.deeper:
            self.basedir = os.path.abspath(os.path.join(self.basedir, ".."))
            result = self._find_folder_mode(self.basedir)
            count += 1
        if result:
            self.window.run_command("open_file", {"file": result})
            self.__class__._cache[self.fn] = result
        elif count == sanity_limit:
            sublime.error_message("Reached sanity limit (which is {}) for "
                                  "going up parent directories. You can "
                                  "increase the sanity limit by heading over "
                                  "to Preferences -> Package Settings -> "
                                  "BetterSwitchHeaderImplementation -> "
                                  "Settings.".format(sanity_limit))
        elif not self.deeper:
            sublime.error_message("Could not find a header/implementation "
                                  "for {}".format(self.fn))
        else:
            sublime.error_message("Unknown stop condition. "
                                  "Please submit an issue.")

    def _project_mode(self):
        self._find_project_mode()

    def _find_folder_mode(self, dir):
        for root, dirs, files in os.walk(dir):
            if root.endswith((".git", ".svn", ".hg")):
                # Skip these directories prematurely (heuristic).
                self.dirs_visited.add(root)
                continue
            elif root in self.dirs_visited:
                # Already visited this dir, no point in doing it again.
                continue
            else:
                for file in files:
                    name, ext = os.path.splitext(file)
                    if ext == ".sublime-project":
                        self.deeper = False
                    elif (self.name == name and
                            self.ext != ext and
                            ext[1:] in self.extensions):
                        return os.path.join(root, file)
                self.dirs_visited.add(root)
        return None

    def _find_project_mode(self):
        self.candidates = []
        dir = self.window.extract_variables()["project_path"]
        for root, dirs, files in os.walk(dir):
            if root.endswith((".git", ".svn", ".hg")):
                # Skip these directories prematurely (heuristic).
                continue
            else:
                for file in files:
                    name, ext = os.path.splitext(file)
                    if (self.name == name and
                            self.ext != ext and
                            ext[1:] in self.extensions):
                        self.candidates.append(os.path.join(root, file))
        if len(self.candidates) == 0:
            sublime.error_message("Could not find a header/implementation "
                                  "for {}".format(self.fn))
        elif len(self.candidates) == 1:
            self.window.run_command("open_file", {"file": self.candidates[0]})
            self.__class__._cache[self.fn] = self.candidates[0]
        else:  # len(self.candidates) > 1
            self.window.show_quick_panel(self.candidates,
                                         self._on_done_select_candidate)

    def _on_done_select_candidate(self, index):
        if index == -1:
            return
        thefile = self.candidates[index]
        self.window.run_command("open_file", {"file": thefile})
        self.__class__._cache[self.fn] = thefile


class BetterSwitchHeaderImplementationListener(sublime_plugin.EventListener):

    def on_window_command(self, view, command_name, command_args):
        if command_name == "switch_file" and command_args == {
            "extensions": ["cpp", "cxx", "cc", "c", "hpp", "hxx", "hh", "h",
                           "ipp", "inl", "m", "mm"]
                }:
            return ("better_switch_header_implementation", command_args)
        else:
            return None
