#!/usr/bin/nodejs

var fs = require('fs');

function phoneType(type) {
  type = type.toUpperCase();
  type = type.split('.');
  for(var i in type) {
    if(type[i] == 'MOBILE')
      type[i] = 'CELL';
  }
  return type.join(';');
}

contents = fs.readFileSync('./contacts-full.json');
json = JSON.parse(contents);
for(var i in json) {
var card = json[i];
console.log('BEGIN:VCARD');
console.log('VERSION:3.0');
for(var k in card) {
  if(k == 'contactId') {
    console.log('UID:' + card[k]);
  } else if(k == 'person') {
    var p = card[k];
    console.log('N:' + (p['firstname']?p['firstname']:'') + ';' + (p['lastname']?p['lastname']:''));
    for(var kp in p) {
      if(kp == 'lastname') {
      } else if(kp == 'id') {
      } else if(kp == 'typeStr') {
      } else if(kp == 'hasPhoto') {
      } else if(kp == 'photoLarge') {
        console.log('PHOTO;ENCODING=BASE64;TYPE=JPEG:' + p[kp]);
      } else if(kp == 'phone') {
      } else if(kp == 'phones') {
        var ph = p[kp];
        for(var kph in ph) {
          var phi = ph[kph]; for(var kphi in phi) {
            if(kphi == 'value') {
            } else if(kphi == 'primary') {
            } else if(kphi == 'type') {
            } else {
              console.log('X-PERSON-PHONE-UNKNOWN-' + kphi.toUpperCase() + ':' + phi[kphi]);
            }
          }
          console.log('TEL' + 
                (phi['primary']=='TRUE'?';PREF':'') +
                (phi['type']?';'+phoneType(phi['type']):'') +
                ':' + phi['value']);
        }
      } else if(kp == 'email') {
      } else if(kp == 'emails') {
        var ph = p[kp];
        for(var kph in ph) {
          var phi = ph[kph]; for(var kphi in phi) {
            if(kphi == 'value') {
            } else {
              console.log('X-PERSON-EMAIL-UNKNOWN-' + kphi.toUpperCase() + ':' + phi[kphi]);
            }
          }
          console.log('EMAIL;INTERNET' +
                ':' + phi['value']);
        }
      } else if(kp == 'addresses') {
        var ph = p[kp];
        for(var kph in ph) {
          var phi = ph[kph]; for(var kphi in phi) {
            if(kphi == 'type') {
            } else if(kphi == 'street') {
            } else {
              console.log('X-PERSON-ADDRESS-UNKNOWN-' + kphi.toUpperCase() + ':' + phi[kphi]);
            }
          }
          //Post Office Address ; Extended Address ; Street ; Locality ; Region ; Postal Code ; Country
          console.log('ADR' +
                (phi['type']?';'+phoneType(phi['type']):'') +
                ':' +
                (phi['pobox']?phi['pobox']:'') + ';' +
                (phi['extendedaddress']?phi['extendedaddress']:'') + ';' +
                (phi['street']?phi['street']:'') + ';' +
                (phi['city']?phi['city']:'') + ';' +
                (phi['region']?phi['region']:'') + ';' +
                (phi['postalcode']?phi['postalcode']:'') + ';' +
                (phi['country']?phi['country']:''));
        }
      } else {
        console.log('X-PERSON-UNKNOWN-' + kp.toUpperCase() + ':' + p[kp]);
      }
    }
  } else {
    console.log('X-UNKNOWN-' + k.toUpperCase() + ':' + card[k]);
  }
}
console.log('END:VCARD');
}
