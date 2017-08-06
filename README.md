# BetterSwitchHeaderImplementation

A simple plugin that "takes over" the menu item in Goto -> Switch File ->
Switch Header/Implementation. Actually, it takes over the *command* that gets
invoked by that menu item.

## Usage
Just use Switch Header/Implementation like you normally would. That is, either
from the menu item in Goto -> Switch File -> Switch Header/Implementation, or
by its keybinding, whatever that may be.

For example, if your header file lives in

    $project_path/include/awesome/foo.hpp

and your implementation file lives in

    $project_path/lib/foo.cpp

then this plugin will *actually* do the switch.

## Two Modes of Operation

When you're in **folder mode** (you have not opened a `.sublime-project` file),
then the plugin will traverse parent directories. A sanity limit of going up
three parent directories is in place. You can change this number in the
settings of the plugin, but do not make this number too high, or Sublime might
freeze.

If your code base looks like this:

    $project_path/include/foo/bar.hpp
    $project_path/include/foo/baz/bar.hpp
    $project_path/src/bar.cpp

then switching from `src/bar.cpp`, you'll most likely end up in
`include/foo/bar.hpp`, as that's the first good match. This is the downside of
folder mode.

When you're in **project mode** (you have opened a `.sublime-project` file),
then the plugin will assume that the project file is at the root of the
directory, and the search will start there. All candidate files are collected,
and if there's more than one candidate file, a quick panel will pop up asking
you to select the correct file. From that point on the plugin will always
choose your selection for switching. This mode is much more powerful. Use the
power of the sublime project file.

## Limitations

The plugin might come up with false positives. For example, if your code base
looks like this:

    $project_path/include/awesome/foo.hpp
    $project_path/include/awesome/bar/foo.hpp
    $project_path/src/bar/foo.cpp

then switching from `include/awesome/foo.hpp`, it will open `src/bar/foo.cpp`.
But `src/bar/foo.cpp` is probably paired with `include/awesome/bar/foo.hpp`.
