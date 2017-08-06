# BetterSwitchHeaderImplementation

A simple plugin that "takes over" the menu item in Goto -> Switch File ->
Switch Header/Implementation. Actually, it takes over the *command* that gets
invoked by that menu item.

## Usage
Just use Switch Header/Implementation like you normally would. Except now
parent directories are also traversed. A sanity limit of going up three parent
directories is in place. Do not make this number too high, or Sublime might
freeze.

For example, if your header file lives in

    $project_path/include/awesome/foo.hpp

and your implementation file lives in

    $project_path/lib/foo.cpp

then this plugin will *actually* do the switch.

## Limitations
If your code base looks like this:

    $project_path/include/foo/bar.hpp
    $project_path/include/foo/baz/bar.hpp
    $project_path/src/bar.cpp

then switching from `src/bar.cpp`, you'll most likely end up in
`include/foo/bar.hpp`, as that's the first good match.
