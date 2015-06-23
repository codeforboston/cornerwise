/**
 * config.js
 *
 * Application configuration options
 */

define([], function() {
    return {
        // String template or function used by Leaflet to generate the
        // image URLs for map files.
        tilesURL: "http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",

        // URL from which to fetch the JSON representing the latest
        // planning and zoning report.
        pzURL: "https://script.google.com/macros/s/AKfycbwkWDB5YX_MnFTMwC1Et476CmeOQvTbbIADVmZXaKlXXL08y_CJ/exec",

        mapId: "zoning-map",

        // Lat/long for the southwest
        bounds: [[42.371861543730496, -71.13338470458984],
                 [42.40393908425197, -71.0679817199707]]
    };
});
