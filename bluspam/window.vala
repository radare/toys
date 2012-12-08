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
using Bluspam;

public class Bluspam.MainWindow : Window
{
	public static Statusbar statusbar;
	public List left_list;
	public List right_list;

        construct
	{
                create_widgets ();
                title = "Bluspam v" + Bluspam.Config.Version;
		border_width = 3;
		set_position(WindowPosition.CENTER);
		resize(500,400);
        }

        private void create_widgets()
	{
                destroy += w => {
			Engine.stop();
			Gtk.main_quit();
		};

		VBox vb = new VBox(false, 0);

		Notebook nb = new Notebook();
		nb.append_page(page1(),                new Label("Bluespam"));
		nb.append_page(TabLogs.getWidget(),    new Label("Logs"));
		nb.append_page(TabCounter.getWidget(), new Label("Counters"));
		nb.append_page(TabConfig.getWidget(),  new Label("Config"));
		nb.append_page(TabAbout.getWidget(),   new Label("About"));
		vb.add(nb);
		
		statusbar = new Statusbar();
		statusbar.push(0, "Interface loaded.");
		vb.pack_end(statusbar, false, false, 0);

		add(vb);
        }

	public static void statusmsg(string msg)
	{
		if (statusbar != null) {
			MainWindow.statusbar.pop(0);
			MainWindow.statusbar.push(0, msg);
		}
	}

	/* main window */
	private Widget page1()
	{
		VBox vb = new VBox(false, 0);
		vb.add(two_main_panels());
		return vb;
	}

	public void update()
	{
		right_list.update();
		TabLogs.tb_update(false);
	}

	private HBox two_main_panels()
	{
		HBox hb = new HBox(false, 3);
		hb.add(left_panel());
		hb.add(right_panel());
		return hb;
	}

	private VBox left_panel()
	{
		VBox vb = new VBox(false, 3);
		left_list = new List().with_title("Files");
		left_list.action += ignore => {
			left_list.clear();
			foreach(string s in Engine.files()) {
				left_list.add(s);
			}
		};
		left_list.update();
		vb.add(left_list.widget);
		vb.pack_end(left_panel_buttons(), false, false, 3);
		return vb;
	}

	private HButtonBox left_panel_buttons()
	{
		HButtonBox hbb = new HButtonBox();
		hbb.set_layout(ButtonBoxStyle.END);
		Button but = new Button.from_stock("gtk-add");
		but.clicked += btn => {
			FileChooserDialog fcd = new FileChooserDialog("Get a file",
				null, FileChooserAction.OPEN,
				"gtk-cancel", 0,
				"gtk-ok", 1);
			fcd.set_position(WindowPosition.CENTER);

			if (fcd.run() == 1) {
				string file = fcd.get_filename();
				Engine.add_file(file);
				left_list.update();
			}

			fcd.destroy();
			fcd = null;
		};
		hbb.pack_start(but, false, false, 3);

		Button but2 = new Button.from_stock("gtk-remove");
		but2.clicked += btn => {
			string file = left_list.get();
			Engine.rm_file(file);
			left_list.update();
		};

		hbb.pack_start(but2, false, false, 3);
		return hbb;
	}

	private VBox right_panel()
	{
		VBox vb = new VBox(false, 3);
		right_list = new List().with_title("Devices");
		right_list.action += ignore => {
			right_list.clear();
			foreach(string s in Engine.devices()) {
				right_list.add(s);
			}
		};
		right_list.update();
		vb.add(right_list.widget);
		vb.pack_end(bottom_buttons(), false, false, 3);
		//vb.pack_end(left_panel_buttons(), false, false, 0);
		return vb;
	}

	private HButtonBox bottom_buttons()
	{
		HButtonBox hbb = new HButtonBox();
		hbb.set_layout(ButtonBoxStyle.END);

		/* add start button */
		Button c = new Button.from_stock("gtk-media-play");
		c.clicked += btn => {
			if (Engine.running) {
				btn.label="gtk-media-stop";
				Engine.stop();
				MainWindow.statusmsg("Stopped");
			} else {
				if (Engine.start()) {
					btn.label="gtk-media-play";
					MainWindow.statusmsg("Spamming...");
				} else {
					MainWindow.statusmsg("Err..");
				}
			}
		};
		hbb.pack_start(c, false, false, 3);

		/* return hbb  */
		return hbb;
	}
}
