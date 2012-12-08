/*
 * Copyright (C) 2007
 *       pancake <youterm.com>
 *
 * bluspam is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * bluspam is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with bluspam; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 */

using GLib;
using Gtk;

public class Bluspam.Main : GLib.Object
{
	public static int counter;
	public static MainWindow w = null;

	construct {
		counter = 0;
		w = new MainWindow();
                w.show_all ();
	}
	
	public static bool global_updater(pointer arg0)
	{
		counter++;
		if (w != null)
			w.update();
		return true;
	}

	/* system monitor */
	public void run()
	{
		GLib.Timeout.add(2000, global_updater, null);
                Gtk.main ();
	}

	public static int main(string[] args)
	{
		Config.parse();
                Gtk.init (out args);
		Main m = new Main();
		m.run();
                return 0;
	}
}
