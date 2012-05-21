var fs = require ("fs");

if (process.argv.length != 3) {
	console.log ("Usage: test.js [file.txt]");
	process.exit (1);
}

var file = process.argv[2];

function loadText(file, cb) {
	var w = 1;
	var h = 0;
	var txt = fs.readFileSync (file);
	var col = 0;
	for (var i=0;i<txt.length;i++) {
		if (txt[i] ==10) {
			h++;
			if (col>w) w = col-1;
			col = 1;
		} else col++;
	}
	cb (file, txt.toString (), w, h);
}

loadText (file, function (f,t,w,h) {
	console.log ("w",w,"h",h);
	console.log ("txt",t);
	var e = require ("./escapes").escapes (f, function (x) {
		var stream = x.canvas.createSyncPNGStream ();
		var fh = fs.openSync (f+".png","w");
		stream.on ("data", function (x) {
			fs.writeSync (fh, x, 0, x.length);
		});
		stream.on ("end", function (x) {
			fs.closeSync (fh);
		});
	}, {
		'width':w*8,
		'height':h*16,
	});
});
