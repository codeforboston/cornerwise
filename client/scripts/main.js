'use strict';
require.config({
    paths: {
        // Dependencies:
        "underscore": "lib/underscore-min",
        "backbone": "lib/backbone",
        "leaflet": "http://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.3/leaflet",
        "jquery": "http://code.jquery.com/jquery-1.11.3.min",

        // Utilities:
        "utils": "src/utils",

        // APIs:
        "arcgis": "src/api/arcgis",

        // Application: //
        "config": "src/config",
        "local-config": "src/localConfig",
        "routes": "src/routes",
        "ref-location": "src/refLocation",

        // Leaflet stuff:
        "ref-marker": "src/leaflet/refMarker",
        "info-layer-helper": "src/leaflet/infoLayer",

        // Backbone Models:
        "permit": "src/model/permit",
        "layer": "src/model/layer",

        // Backbone Collections:
        "permits": "src/model/permits",
        "layers": "src/model/layers",

        // Backbone Views:
        "permits-view": "src/view/permits",
        "permit-view": "src/view/permit",
        "details-view": "src/view/detail",
        "filters-view": "src/view/filters",
        "map-view": "src/view/map",
        "popup-view": "src/view/popup",
        "layers-view": "src/view/layers",

        "collapsible-view": "src/view/collapsible",
        "spga-filter-view": "src/view/spgaFilter",
        "type-filter-view": "src/view/typeFilter",

        "setup": "src/setup"
    },

    shim: {
        "leaflet": {
            exports: "L"
        }
    }
});

require(["setup"], function(setup) {
    setup.start();

    console.log("Setup complete.");
});
