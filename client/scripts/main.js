'use strict';
require.config({
    paths: {
        // Dependencies:
        "underscore": "lib/underscore-min",
        "backbone": "lib/backbone",
        "leaflet": "lib/leaflet-0.7.3/leaflet",

        // Application: //
        "config": "src/config",
        "routes": "src/routes",

        // Backbone Models:
        "permit": "src/model/permit",

        // Backbone Views:
        "view/permits": "src/view/permits",
        "view/map": "src/view/map",


        // Leaflet
        "zoninglayer": "src/zoninglayer"
    },

    shim: {

    }
});

require(["routes"], function(routes) {
    routes.init();

});
