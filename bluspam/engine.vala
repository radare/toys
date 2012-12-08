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

public class Bluspam.Engine
{
	// XXX must be read-only protected
	public static bool running = false;

	public static bool start()
	{
		if (system("(cd sh && sudo ./start)") == 0)
			Engine.running = true;
		else	return false;

		return true;
	}

	public static void stop()
	{
		Engine.running = false;
		system("(cd sh && sudo ./stop)");
	}

	public static void clear_logs()
	{
		system("sudo rm -f sh/db/log && :> sh/db/log");
	}

	public static void save_logs(string file)
	{
		system("cp sh/db/log '"+file+"'");
	}

	public static void add_file(string file)
	{
		if (file != "")
			system("sudo cp '"+file+"' sh/files/");
	}

	public static void rm_file(string file)
	{
		if (file != "")
			system("sudo rm -f 'sh/files/"+file+"'");
	}

	public static SList<string> files()
	{
		SList<string> str = new SList<string>();
		try {
			string name;
			Dir d = Dir.open("sh/files/");
			while(null != (name=d.read_name())) {
				str.append(name);
			}
			d = null;
		} catch(FileError e) {
			stderr.printf("Cannot open 'sh/files' directory.\n");
		}
		
		return str;
	}

	public static SList<string> devices()
	{
		SList<string> str = new SList<string>();
		String line = new String.sized(1024);
		FileStream fs = FileStream.open("sh/db/list", "r");

		while(!fs.eof()) {
			fs.gets(line.str, 1000);
			if (!fs.eof()) {
				string tmp = line.str.chomp();
				if (tmp.size() > 0)
					str.append(tmp);
			}
		}

		return str;
	}

	public static string slurp_logs()
	{
		string ret = "";
		String line = new String.sized(1024);
		FileStream fs = FileStream.open("sh/db/log", "r");

		while(!fs.eof()) {
			fs.gets(line.str, 1000);
			if (!fs.eof())
				ret += line.str;
		}

		fs = null;
		return ret;
	}

        [Import ()]
        public static int system(string name);
}
