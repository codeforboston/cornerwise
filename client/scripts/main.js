require.config({
    paths: {
        // Dependencies:
        "underscore": "lib/underscore-min",
        "backbone": "lib/backbone-min",
        "leaflet": "lib/leaflet",
        "jquery": "lib/jquery-3.1.1.min",
        "chartjs": "lib/Chart.min",

        // Utilities:
        "utils": "src/utils",
        "locale": "src/localization",

        // APIs:
        "arcgis": "src/api/arcgis",
        "places": "src/api/places",

        // Application: //
        "config": "src/config",
        "local-config": "src/localConfig",
        "app-state": "src/appState",
        "ref-location": "src/refLocation",

        // Leaflet stuff:
        "ref-marker": "src/leaflet/refMarker",
        "proposal-marker": "src/leaflet/proposalMarker",
        "info-layer-helper": "src/leaflet/infoLayer",

        // Backbone Models:
        "proposal": "src/model/proposal",
        "layer": "src/model/layer",

        // Backbone Collections:
        "selectable": "src/collection/selectableCollection",
        "proposals": "src/collection/proposals",
        "layers": "src/collection/layers",
        "regions": "src/collection/regions",
        "collection-manager": "src/collection/collectionManager",

        "alerts": "src/view/alerts",

        // Backbone Views:
        // Generic:
        "modal-view": "src/view/modalView",

        // Application-specific:
        "proposal-view": "src/view/proposal",
        "map-view": "src/view/map",
        "proposal-info-view": "src/view/proposalInfo",
        "projects-summary-view": "src/view/projectsSummary",
        "layers-view": "src/view/layers",
        "filters-view": "src/view/filters",
        "subscribe-view": "src/view/subscribe",
        "info-view": "src/view/infoView",
        "list-view": "src/view/list",
        "image-view": "src/view/image",
        "proposal-popup-view": "src/view/proposalPopup",

        // View managers:
        "view-manager": "src/viewManager",

        // Additional features:
        "budget": "src/view/budget",
        "glossary": "src/glossary",
        "legal-notice": "src/legalNotice",

        // Pre-imported templates:
        "templates": "build/templates",

        "setup": "src/setup"
    },

    moduleDefaults: {
        "templates": {}
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
