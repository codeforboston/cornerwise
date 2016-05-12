// Currently unused and incomplete.
// The intended purpose is to provide information about the local representative
// for a given proposal.
define(["jquery", "config"],
       function($, config) {
           var API_KEY = config.googleKey,
               URL_BASE = "https://www.googleapis.com/civicinfo/v2/representatives";

           var civic = {
               get: function(address) {
                   if (!API_KEY)
                       return $.Deferred().reject("");

                   return $.getJSON(URL_BASE,
                                    {key: API_KEY,
                                     address: address});
               }
           };

           return civic;
       });
