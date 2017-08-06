import sublime_plugin
import sublime
import os


class bidict(dict):
    def __init__(self, *args, **kwargs):
        super(bidict, self).__init__(*args, **kwargs)
        self.inverse = {}
        for key, value in self.iteritems():
            self.inverse.setdefault(value,[]).append(key)

    def __setitem__(self, key, value):
        if key in self:
            self.inverse[self[key]].remove(key)
        super(bidict, self).__setitem__(key, value)
        self.inverse.setdefault(value,[]).append(key)

    def __delitem__(self, key):
        self.inverse.setdefault(self[key],[]).remove(key)
        if self[key] in self.inverse and not self.inverse[self[key]]:
            del self.inverse[self[key]]
        super(bidict, self).__delitem__(key)


class BetterSwitchHeaderImplementationCommand(sublime_plugin.WindowCommand):

    _cache = bidict()

    def run(self, extensions):

        view = self.window.active_view()
        if not view:
            return
        fn = view.file_name()
        if not fn:
            return
        result = self.__class__._cache.get(fn, None)
        if result:
            self.window.run_command("open_file", {"file": result})
            return
        result = self.__class__._cache.inverse.get(fn, None)
        if result:
            self.window.run_command("open_file", {"file": result})
            return

        basedir, self.basename = os.path.split(fn)
        self.name, self.ext = os.path.splitext(self.basename)
        if self.ext != "" and self.ext[1:] not in extensions:
            return

        self.extensions = tuple(extensions)  # so we can use it with .endswith
        self.dirs_visited = set()            # dont visit dirs twice

        # use a sanity limit
        count = 0
        sanity_limit = sublime.load_settings(
            "BetterSwitchHeaderImplementation.sublime-settings").get(
                "sanity_limit", 3)
        result = self._find(basedir)
        while (not result) and (count < sanity_limit):
            basedir = os.path.abspath(os.path.join(basedir, ".."))
            result = self._find(basedir)
            count += 1
        if result:
            self.window.run_command("open_file", {"file": result})
            self.__class__._cache[fn] = result
        elif count == sanity_limit:
            sublime.error_message("Reached sanity limit (which is {}) for "
                                  "going up parent directories. You can "
                                  "increase the sanity limit by heading over "
                                  "to Preferences -> Package Settings -> "
                                  "BetterSwitchHeaderImplementation -> "
                                  "Settings.".format(sanity_limit))
        else:
            sublime.error_message("Could not find a header/implementation "
                                  "for {}".format(fn))

    def _find(self, dir):
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
                    if (self.name in file and
                            not file.endswith(self.ext) and
                            file.endswith(self.extensions)):
                        return os.path.join(root, file)
                self.dirs_visited.add(root)
        return None


class BetterSwitchHeaderImplementationListener(sublime_plugin.EventListener):

    def on_window_command(self, view, command_name, command_args):
        if command_name == "switch_file" and command_args == {
            "extensions": ["cpp", "cxx", "cc", "c", "hpp", "hxx", "hh", "h",
                           "ipp", "inl", "m", "mm"]
                }:
            return ("better_switch_header_implementation", command_args)
        else:
            return None
