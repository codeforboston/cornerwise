define(["jquery", "config"], function($, config) {
    // URL endpoint for geocoding
    var ADDRESS_URL = "http://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/geocodeAddresses";

    var ACCESS_TOKEN = null,
        // Timestamp
        ACCESS_EXPIRATION = null;

    return {
        getAuthToken: function() {
            if (ACCESS_TOKEN) {
                return $.Deferred().resolve(ACCESS_TOKEN);
            }

            return $.getJSON("https://www.arcgis.com/sharing/oauth2/token", {
                grant_type: "client_credentials",
                client_id: config.clientId,
                client_secret: config.clientSecret,
                f: "pjson"
            }).then(function(json) {
                ACCESS_TOKEN = json.access_token;
                ACCESS_EXPIRATION = (new Date() + json.expires_in*1000);
                return json.access_token;
            });
        },

        geocode: function(addr) {
            return this.getAuthToken().then(function() {
                return $.getJSON(ADDRESS_URL,
                                 {
                                     addresses: JSON.stringify({
                                         records: [
                                             {
                                                 attributes: {
                                                     OBJECTID: 1,
                                                     Address: addr,
                                                     City: "Somerville",
                                                     Region: "MA"
                                                 }
                                             }
                                         ]
                                     }),
                                     token: ACCESS_TOKEN,
                                     f: "pjson"
                                 }).then(function(json) {
                          console.log(json);
                      });
            });
        }
    };
});
