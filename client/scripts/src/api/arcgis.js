define(["jquery", "config", "collection/regions"], function($, config, regions) {
    // URL endpoint for geocoding
    var ADDRESS_URL = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/geocodeAddresses";


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
                var activeRegions = regions.getSelection(),
                    region = activeRegions.length && activeRegions[0].attributes;
                return $.getJSON(ADDRESS_URL,
                                 {
                                     addresses: JSON.stringify({
                                         records: [
                                             {
                                                 attributes: {
                                                     OBJECTID: 1,
                                                     Address: addr,
                                                     City: region.city,
                                                     Region: region.state
                                                 }
                                             }
                                         ]
                                     }),
                                     token: token,
                                     f: "pjson"
                                 }).then(function(json) {
                                     var error;
                                     if (!json.locations ||
                                         json.locations.length === 0) {
                                         error = "No matching locations.";
                                     } else {
                                         var attrs = json.locations[0].attributes;

                                         if (!attrs.StAddr || attrs.score < 80) {
                                             error = "No good matches";
                                         } else {
                                             var regionMatches = regions.where({city: attrs.City,
                                                                                state: attrs.RegionAbbr,
                                                                                _selected: true});
                                             if (!regionMatches.length)
                                                 error = "No matches for this region.";
                                         }

                                     }

                                     if (error)
                                         return $.Deferred().reject({reason: error});

                                     return json;
                                 });
            });
        },

        /**
         * Given a JSON response from the ArcGIS geocoding API, extract
         * and return the latitude and longitude from the first address
         * it contains, along with a dictionary of attributes.
         *
         * @param {object} response
         * @return {Array} array of [lat, long, attributes]
         */
        getLatLngForFirstAddress: function(response) {
            var loc = response.locations[0].attributes;

            return [loc.Y, loc.X, loc];
        },

        reverseGeocode: function(lat, long) {
            return this.getAuthToken().then(function(token) {
                return $.getJSON("https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/reverseGeocode",
                      {
                          location: (long + "," + lat),
                          token: token,
                          f: "pjson"
                      });
            });
        }
    };
});
