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

public class Bluspam.Config
{
	public const string Version = "0.1";

	public static string name = "spam0";
	public static string timeout = "60";
	public static string retry = "0";
	public static string order = "az"; // random
	public static string mode = "single"; // random

	public static void parse()
	{
		int i;
		String line = new String.sized(1024);
		FileStream fs = FileStream.open("sh/config", "r");

		for(i=0;!fs.eof();i++) {
			fs.gets(line.str, 1000);
			if (fs.eof()) break;
			string tmp = line.str.chomp();
			stdout.printf("line: %d %s\n", i, line.str);
			if (line.str.has_prefix("NAME=")) {
				name = line.str.substring(5,line.str.size());
			} else
			if (line.str.has_prefix("MODE=")) {
				mode = line.str.substring(5,line.str.size());
			} else
			if (line.str.has_prefix("ORDER=")) {
				order = line.str.substring(6,line.str.size());
			} else
			if (line.str.has_prefix("RETRY=")) {
				retry = line.str.substring(6,line.str.size());
			} else
			if (line.str.has_prefix("TIMEOUT=")) {
				timeout = line.str.substring(8,line.str.size());
			}
		}

		fs = null;
	}

	public static void save()
	{
		FileStream stream = FileStream.open("sh/config", "w");
		stream.printf("# Automatically generated config file for bluspam\n");
		stream.printf("NAME=%s\n", name);
		stream.printf("TIMEOUT=%s\n", timeout);
		stream.printf("SLEEP=1\n"); // XXX forced
		stream.printf("RETRY=%s\n", retry);
		stream.printf("MODE=%s\n", mode);
		stream.printf("IFACES=hci0\n"); // XXX forced
		stream.printf("ORDER=%s\n", order);
		stream.printf("ORDER_DEVICE=%s\n", order); // XXX dupped
		stream.printf("DB=./db/\n");
		stream.printf("FILES=./files/\n");
		stream.printf("VERSION=%s\n", Config.Version);
		stream = null;
	}
}
