'use strict';
require.config({
    paths: {
        // Dependencies:
        "underscore": "lib/underscore-min",
        "backbone": "lib/backbone",
        "leaflet": "http://cdn.leafletjs.com/leaflet-0.7.5/leaflet",
        "jquery": "http://code.jquery.com/jquery-1.11.3.min",
        "chartjs": "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/1.0.2/Chart.min",

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
        "proposal-marker": "src/leaflet/proposalMarker",
        "info-layer-helper": "src/leaflet/infoLayer",
        "recentered-map": "src/leaflet/recenteredMap",

        // Backbone Models:
        "proposal": "src/model/proposal",
        "layer": "src/model/layer",
        "project": "src/model/project",

        // Backbone Collections:
        "selectable": "src/model/selectableCollection",
        "proposals": "src/model/proposals",
        "layers": "src/model/layers",
        "projects": "src/model/projects",

        // Backbone Views:
        "proposals-view": "src/view/proposals",
        "proposal-view": "src/view/proposal",
        "details-view": "src/view/detail",
        "map-view": "src/view/map",
        "minimap-view": "src/view/minimap",
        "preview-manager": "src/view/previewManager",
        "preview-view": "src/view/preview",
        "project-preview-view": "src/view/projectPreview",
        "projects-view": "src/view/projects",
        "project-view": "src/view/project",
        "layers-view": "src/view/layers",
        "filters-view": "src/view/filters",

        // View managers:
        "collapsible-view": "src/view/collapsible",
        "tab-view": "src/view/tabs",

        // Additional features:
        "glossary": "src/glossary",
        "legal-notice": "src/legalNotice",

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
