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
        pzURL: "https://script.google.com/macros/s/AKfycbxdNiXwOYTAxEZE4LuGcCFsOW-JpQr9bQl6hx3NZIF4oc19UoBT/exec",
        mapId: "zoning-map",

        // Lat/long for the southwest
        bounds: [[42.371861543730496, -71.13338470458984],
                 [42.40393908425197, -71.0679817199707]],

        // Default reference location:
        refPointDefault: {lat: 42.387545768736246,
                          lng: -71.09950304031372},
        refMarkerColor: "red",

        // Map of { "permit abbreviation": "human readable permit name" }
        permitTypes: {

        },

        // Esri:
        clientId: "jYLY7AeA1U9xDiWu",
        clientSecret: "64a66909ff724a0a9928838ef4462909"
    };
});
