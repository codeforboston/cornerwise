"use strict";
define(["utils"], function($u) {
    var type_match = "(revision to|special permit|time extension|variance)",
        per_re = /seeks? (a )/i;

     function abridgeLegalNotice(s) {
         var m = per_re.exec(s);

         return m ? $u.capitalize(s.slice(m.index+m[0].length).trim()) : s;
     }

    $u.registerHelper("abridgeLegalNotice", abridgeLegalNotice);

    return {
        abridgeLegalNotice: abridgeLegalNotice
    };
});
