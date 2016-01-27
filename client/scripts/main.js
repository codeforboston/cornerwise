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
        "collapsible": "src/collapsible",
        "ref-location": "src/refLocation",

        // Leaflet stuff:
        "ref-marker": "src/leaflet/refMarker",
        "proposal-marker": "src/leaflet/proposalMarker",
        "info-layer-helper": "src/leaflet/infoLayer",

        // Backbone Models:
        "proposal": "src/model/proposal",
        "layer": "src/model/layer",
        "project": "src/model/project",

        // Backbone Collections:
        "selectable": "src/model/selectableCollection",
        "proposals": "src/model/proposals",
        "layers": "src/model/layers",
        "projects": "src/model/projects",

        "alerts": "src/view/alerts",

        // Backbone Views:
        // Generic:
        "modal-view": "src/view/modalView",

        // Application-specific:
        "proposals-view": "src/view/proposals",
        "proposal-view": "src/view/proposal",
        "map-view": "src/view/map",
        "minimap-view": "src/view/minimap",
        "proposal-info-view": "src/view/proposalInfo",
        "project-info-view": "src/view/projectInfo",
        "projects-summary-view": "src/view/projectsSummary",
        "budget": "src/view/budget",
        "projects-view": "src/view/projects",
        "project-view": "src/view/project",
        "layers-view": "src/view/layers",
        "filters-view": "src/view/filters",
        "info-view": "src/view/infoView",
        "list-view": "src/view/list",

        // View managers:
        "collapsible-view": "src/view/collapsible",
        "tab-view": "src/view/tabs",
        "view-manager": "src/viewManager",

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
