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

public class Bluspam.TabConfig
{
	public static Entry name;
	public static Entry timeout;
	public static ComboBox order;
	public static ComboBox mode;
	public static CheckButton check;

	private static string getOrder(int i)
	{
		switch(i) {
		case 0: return "az";
		case 1: return "random";
		} return "az";
	}

	private static string getMode(int i)
	{
		switch(i) {
		case 0: return "single";
		case 1: return "multiple";
		} return "single";
	}

	public static Widget getWidget()
	{
		VBox vb = new VBox(false, 0);
		HBox hb = new HBox(false,0);
			hb.pack_start(new Label("Name"),false,false,3);
			name = new Entry();
			name.text = Config.name;
			hb.add(name);
		vb.pack_start(hb, false, false, 3);

		hb = new HBox(false,0);
			hb.pack_start(new Label("Timeout"),false,false,3);
			timeout = new Entry();
			timeout.text = Config.timeout;
			hb.add(timeout);
		vb.pack_start(hb, false, false, 3);

		hb = new HBox(false,0);
			hb.pack_start(new Label("Order"),false,false,3);
			order = new ComboBox.text();
			order.append_text(getOrder(0));
			order.append_text(getOrder(1));
			// XXX bad design here
			if (Config.order == "az")
				order.set_active(0);
			else
				order.set_active(1);
			//name.text = Config.order;
			hb.add(order);
		vb.pack_start(hb, false, false, 3);

		hb = new HBox(false,0);
			hb.pack_start(new Label("Mode"),false,false,3);
			mode = new ComboBox.text();
			mode.append_text("single");
			mode.append_text("multiple");
			if (Config.mode == "single")
				mode.set_active(0);
			else
				mode.set_active(1);
			//name.text = Config.order;
			hb.add(mode);
		vb.pack_start(hb, false, false, 3);

		hb = new HBox(false,0);
	//		hb.pack_start(new Label("Anoyance"),false,false,3);
			check = new CheckButton.with_label("Retry after success");
			if (Config.retry == "1")
				check.active = true;
			else
				check.active = false;
			hb.add(check);
		vb.pack_start(hb, false, false, 3);
		
		vb.pack_end(bottom_config_buttons(), false, false, 3);
		return vb;
	}

	private static HButtonBox bottom_config_buttons()
	{
		HButtonBox hbb = new HButtonBox();
		hbb.set_layout(ButtonBoxStyle.END);

		/* add refresh button */
		Button b = new Button.from_stock("gtk-refresh");
		b.clicked += btn => {
			Config.parse();
		};
		hbb.pack_start(b, false, false, 3);

		/* add save button */
		Button c = new Button.from_stock("gtk-save");
		c.clicked += btn => {
			bool run = Engine.running;
			if (run)
				Engine.stop();

			MainWindow.statusmsg("Configuration saved.");
			/* copy data from widgets to config */

			Config.name = name.text;
			Config.order = getOrder(order.get_active());
			Config.mode = getMode(mode.get_active());
			Config.timeout = timeout.text.to_int().to_string();
			if (check.active)
				Config.retry = "1";
			else	Config.retry = "0";

			/* go save */
			Config.save();
			if (run)
				Engine.start();
		};
		hbb.pack_start(c, false, false, 3);

		return hbb;
	}
}
