'use strict';
require.config({
    paths: {
        // Dependencies:
        "underscore": "lib/underscore-min",
        "backbone": "lib/backbone",
        "leaflet": "http://cdn.leafletjs.com/leaflet-0.7.5/leaflet",
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
        "recentered-map": "src/leaflet/recenteredMap",

        // Backbone Models:
        "permit": "src/model/permit",
        "layer": "src/model/layer",
        "project": "src/model/project",

        // Backbone Collections:
        "permits": "src/model/permits",
        "layers": "src/model/layers",
        "projects": "src/model/projects",

        // Backbone Views:
        "permits-view": "src/view/permits",
        "permit-view": "src/view/permit",
        "details-view": "src/view/detail",
        "filters-view": "src/view/filters",
        "map-view": "src/view/map",
        "minimap-view": "src/view/minimap",
        "preview-view": "src/view/preview",
        "projects-view": "src/view/projects",
        "project-view": "src/view/project",
        "project-preview-view": "src/view/projectPreview",
        // TODO: Remove
        "popup-view": "src/view/popup",
        "layers-view": "src/view/layers",

        // View managers:
        "collapsible-view": "src/view/collapsible",
        "tab-view": "src/view/tabs",

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
    window.app = setup.start();
});
