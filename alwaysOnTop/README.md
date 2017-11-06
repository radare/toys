alwaysOnTop
===========

This shellscript uses Frida to inject code to any OSX application
to enable or disable the "always on top" option for any window.

Usage
-----

	$ alwaysOnTop TextEdit

To disable this option:

	$ alwaysOnTop -d TextEdit

TODO
----

* Implement frida -e
* Implement frida -q
* Add setAlpha_() support in alwaysOnTop -a

	ObjC.classes.NSApplication.sharedApplication().windows().objectAtIndex_(0).setAlphaValue_(0.3)
