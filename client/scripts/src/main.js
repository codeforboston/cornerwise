require.config({
    baseUrl: "/static/scripts/src",
    paths: {
        // Dependencies:
        "underscore": "lib/underscore-min",
        "backbone": "lib/backbone-master",
        "jquery": "lib/jquery-3.1.1.min",
        "chartjs": "lib/Chart.min"
    },

    moduleDefaults: {
        "build/templates": {}
    },

    shim: {
        chartjs: {exports: "Chart"},
        leaflet: {exports: "L"},
        underscore: {exports: "_"},
        backbone: {deps: ["underscore", "jquery"],
                   exports: "Backbone"}
    }
});

require(["setup"], function(setup) {
    window.app = setup.start();
});
