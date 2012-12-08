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

using Gtk;
using GLib;

public class Bluspam.TabLogs
{
	private static TextBuffer tb;
	private static TextView tv;
	private static ScrolledWindow sw;
	private static CheckButton cb;

	public static Widget getWidget()
	{
		VBox vb = new VBox(false, 5);
		tb = new TextBuffer(null);
		sw = new ScrolledWindow(null,null);
		sw.set_policy(PolicyType.AUTOMATIC, PolicyType.AUTOMATIC);
		tv = new TextView.with_buffer(tb);
		tv.cursor_visible = false;
		tv.editable = false;
		sw.add(tv);
		sw.set_placement(Gtk.CornerType.BOTTOM_LEFT);
		vb.add(sw);
		vb.border_width = 3;
		vb.pack_end(bottom_logs_buttons(), false, false, 3);
		tb_update(true);

		return vb;
	}

	private static HButtonBox bottom_logs_buttons()
	{
		HButtonBox hbb = new HButtonBox();
		hbb.set_layout(ButtonBoxStyle.END);

		cb = new CheckButton.with_label("Update");
		hbb.pack_start(cb, false, false, 3);

		/* add start button */
		Button c = new Button.from_stock("gtk-clear");
		c.clicked += btn => {
			tb.set_text("",0);
			Engine.clear_logs();
		};
		hbb.pack_start(c, false, false, 3);

		/* add save button */
		Button d = new Button.from_stock("gtk-save");
		d.clicked += btn => {
			FileChooserDialog fcd = new FileChooserDialog("Get a file",
				null, FileChooserAction.SAVE,
				"gtk-cancel", 0,
				"gtk-ok", 1);
			fcd.set_position(WindowPosition.CENTER);

			if (fcd.run() == 1) {
				string file = fcd.get_filename();
				Engine.save_logs(file);
			}

			fcd.destroy();
			fcd = null;
		};
		hbb.pack_start(d, false, false, 3);

		/* add refresh button 
		Button a = new Button.from_stock("gtk-refresh");
		a.clicked += btn => {
			tb_update(true);
		};
		hbb.pack_start(a, false, false, 3);
		*/

		return hbb;
	}

	public static void tb_update(bool first_time)
	{
		if (tb != null) {
			if (first_time || cb.get_active()) {
				string logs = Engine.slurp_logs();
				tb.set_text(logs, (int)logs.size());
				TextIter iter = new TextIter();
				tb.get_end_iter(ref iter);
				tv.scroll_to_iter(ref iter, 0,false,0,0);
			}
		}
	}
}
