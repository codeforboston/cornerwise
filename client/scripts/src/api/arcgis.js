define(["jquery", "config"], function($, config) {
    // URL endpoint for geocoding
    var ADDRESS_URL = "http://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/geocodeAddresses";


    var ACCESS_TOKEN = null,
        // Timestamp
        ACCESS_EXPIRATION = null;

    return {
        getStoredToken: function() { return ACCESS_TOKEN; },
        getStoredExpiration: function() { return ACCESS_EXPIRATION; },
        getAuthToken: function() {
            if (ACCESS_TOKEN && (new Date().valueOf() < ACCESS_EXPIRATION)) {
                // Pass along the existing access token
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
            return this.getAuthToken().then(function(token) {
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
                                     token: token,
                                     f: "pjson"
                                 }).then(function(json) {
                                     if (!json.locations ||
                                         json.locations.length == 0) {
                                         return $.Deferred().reject(
                                             {reason: "No matching locations."});
                                     }

                                     return json;
                                 });
            });
        },

        /**
         * Given a JSON response from the ArcGIS geocoding API, extract
         * and return the latitude and longitude from the first address
         * it contains.
         *
         * @param {object} response
         * @return {Array} array of [lat, long]
         */
        getLatLngForFirstAddress: function(response) {
            var loc = response.locations[0].location;

            return [loc.y, loc.x];
        },

        reverseGeocode: function(lat, long) {
            return this.getAuthToken().then(function(token) {
                return $.getJSON("http://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode",
                      {
                          location: JSON.stringify({
                              x: lat,
                              y: long
                          }),
                          token: token,
                          f: "pjson"
                      });
            });
        }
    };
});
