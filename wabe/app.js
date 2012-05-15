/* 

Simple server (key words for "Just thrown together").  Download node.js and run "node server.js" to run a node.

*/

var http = require('http');
var fs = require('fs');
var path = require('path');
var url = require('url');

var sha = require('./rsa2_files/sha1');
var jsbn = require('./rsa2_files/jsbn');

var mytime=0



function Sleep(t) {
    var now = new Date().getTime();
    while(new Date().getTime() < now + t) { }
}

function IsMatch(query,entry) {
    for (i in query) {
        if(
            (typeof(query[i])=="object"&&!IsMatch(query[i],entry[i])) ||
            (query[i]!=entry[i]))
                return false;
    }
    return true;
}

function QueryDB(query) {
    var ret=[]
    for (i in database) {
        var entry=database[i];
        if(IsMatch(query,entry)) {
            ret.push(entry);
        }
    }
    return ret;
}
database=[{pubkey:"xrep"},{pubkey:"notxrep"}]
query={pubkey:"xrep"}
console.log(QueryDB(query))
database=[]

DEBUGMODE=false
//console.log(process.argv.splice(2)[0])
//console.log(process.argv[3])

fs.readFile(process.argv[3] || "./database.json", function(err,c) {
            if(err) {
                console.log(err);
            } else {
                database=JSON.parse(c)
                console.log("Loaded database length: "+c.length)
                //console.log("The file was saved!");
            }
        }); 


// This is probably what you're interested in:

var port=process.argv[2] || 8124;

http.createServer(function (request, response) {
    
    var success=false
    console.log(unescape(request.url))
    var curdate = new Date();
    
    if(request.url.length<50&&!(request.url.indexOf("..")>=0 || request.url.indexOf("//")>=0)) {
        var file='.'+request.url;
        /*if() {
            response.writeHead(500, { 'Content-Type': 'text/html'});
            response.end(cont, 'utf-8');
            return; // haxor prevention!
        }*/
        if(request.url=='/') file="index.html"
        if(path.existsSync(file)) {
            //console.log("file exists")
            
            var cont=fs.readFileSync(file)
            var ext=request.url.split('.').pop()
            
            if(ext=="txt" || ext=="js")
                response.writeHead(200, { 'Content-Type': 'text/plain'});
            else if(ext=="rar")
                response.writeHead(200, { 'Content-Type': 'application/octet-stream'});
            else
                response.writeHead(200, { 'Content-Type': 'text/html'});
            response.end(cont);
            return;
        }
    }
    //Sleep(50)
    var url_parts = url.parse(request.url, true);
    console.log(url_parts.pathname)
    console.log(request.connection.remoteAddress)

    // Generic handler, can take "/json" to get the whole database, or '/json{"signature":"avmiomdioa"}'
    if(request.url.substr(0,5)=="/json") {
        response.writeHead(200, { 'Content-Type': 'text/plain' });
        
        var restof=request.url.substr(5)
        var restof=unescape(url_parts.query.d);
        
        try{
            console.log(restof)
            var parsed=JSON.parse(restof);
            console.log(JSON.stringify(parsed,null,4))
            response.end("callback("+JSON.stringify(QueryDB(parsed))+")", 'utf-8');
        } catch (e) {
            response.end("callback("+JSON.stringify(database)+")", 'utf-8');
        }
        return
    }
    /*if(request.url.substr(0,5)=="/post") {
        //var entrystr=url_parts.query.d;
        var entrystr=unescape(request.url.substr(5))*/
        
    if(url_parts.pathname=="/post") {
        var entrystr=url_parts.query.d;
        console.log("entry "+entrystr)
        var entry=JSON.parse(entrystr)
        entry.time=mytime++
        response.writeHead(200, { 'Content-Type': 'text/plain' });
        response.end("posted()", 'utf-8');
        database.push(entry)
        console.log("new database legnth: "+database.length)
        //response.end("cb('hi')")
        fs.writeFile("./database.json", JSON.stringify(database), function(err) {
            if(err) {
                console.log(err);
            } else {
                console.log("The file was saved!");
            }
        }); 
        return
    }
    // for development.
    if(DEBUGMODE && url_parts.pathname=="/reset") {
        database=[{pubkey:"root", signature: "root", message:{ comment:""}}]
    }
   
    response.writeHead(200, {'Content-Type': 'text/plain'});
    response.write(request.url+"\n")
    response.write("test\n")
    response.write(JSON.stringify(database))
    for (i in database) {
        d=database[i]
        m=d.message;
        response.write(d.pubkey+": ");
        
        if(m.comment) {
            response.write("says \""+m.comment+"\" ");
            response.write("Comment id: "+m.id+" ") 
        }
        if(m.parent)
           response.write("Parent "+m.parent)
        response.write("\n");
    }
    response.end('Hello World\n');
}).listen(port);

console.log('Server running at '+port);


