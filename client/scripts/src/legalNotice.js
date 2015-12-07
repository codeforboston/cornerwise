"use strict";
define(["utils"], function($u) {
    var type_match = /(revision to|special permit|time extension|variance)/i,
        per_re = /seeks? a/i;

     function abridge(s) {
         var m = per_re.exec(s);

         return m ? $u.capitalize(s.slice(m.index+m[0].length).trim()) : s;
     }

    $u.registerHelper("abridge", abridge);

    return {
        abridge: abridge
    };
});
