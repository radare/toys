var fs = require('fs');

if (process.argv.length != 3) {
  console.log('Usage: test.js [file.txt]');
  process.exit(1);
}

var file = process.argv[2];

function loadText (file, cb) {
  var w = 1;
  var h = 0;
  var txt = fs.readFileSync(file).toString();
  var col = 0;
  var text = '';
  var directives = [];

  var tlen = txt.length;
  console.log('txt ', file);
  console.log('len ', tlen);
  for (var i = 0; txt[i] == ';' && txt[i + 2] == '=' && i < tlen;) {
    for (var j = i; txt[j] != '\n' && j < tlen; j++);
    if (i == j) {
      console.log('break ', i);
      break;
    }
    var d = txt.substring(i + 3, j);
    console.log('directive', d, j);
    directives[txt[i + 1]] = d;
    i = j + 1;
  }
  console.log('i', i);
  txt = txt.substring(i);
  console.log(txt);
  for (var i = 0; i < txt.length; i++) {
    if (txt[i] == '\n') {
      h++;
      if (col > w) w = col - 1;
      col = 1;
    } else col++;
  }
  if (h > 0) cb(file, txt, w, h);
  else console.error('invalid sizes (h=0)');
}

loadText(file, function (f, t, w, h) {
  console.log('w', w, 'h', h);
  console.log(t);
  var e = require('./escapes').escapes(f, function (x) {
    var stream = x.canvas.createSyncPNGStream();
    var fh = fs.openSync(f + '.png', 'w');
    stream.on('data', function (x) {
      fs.writeSync(fh, x, 0, x.length);
    });
    stream.on('end', function (x) {
      fs.closeSync(fh);
    });
  }, {
    'width': w * 8,
    'height': h * 16
  });
});
