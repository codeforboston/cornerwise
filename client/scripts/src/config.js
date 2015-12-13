/**
 * config.js
 *
 * Application configuration options
 */

define(["optional!local-config", "underscore"], function(localConfig, _) {
    var config = {
        // String template or function used by Leaflet to generate the
        // image URLs for map files.
        //tilesURL: "http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
        tilesURL: "http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",

        backendURL: "",

        // URL from which to fetch the JSON representing the latest
        // planning and zoning report.
        pzURL: "/proposal/list",

        // Lat/long for the southwest and northeasth corners of the
        // map's initial viewing area.
        bounds:  [[42.37236882604975, -71.14565849304199],
                  [42.41680352972898, -71.04806900024413]],

        maxBounds: [[42.35524578349561, -71.18951797485352],
                    [42.444107964019395, -70.99004745483398]],

        // Default reference location:
        refPointDefault: {lat: 42.387545768736246,
                          lng: -71.09950304031372},
        refMarkerColor: "red",

        defaultProposalThumb: "/static/images/marker-normal@2x.png",

        // Map of { "permit abbreviation": "human readable permit name" }
        permitTypes: {
            "SP": "Special Permit",
            "Ext.": "Extension",
            "SP/V": "Special Permit with Variance",
            "AA": "Administrative Appeal",
            "SPSR": "Special Permit with Site Plan Review",
            "SPD": "Special Permit with Design Review",
            "V": "Variance",
            "R": "Revision",
            "Sub/SP": "Subdivision",
            "SPSR/V": "Special Permit with Site Plan Review"
        },

        // Layers that are always shown
        baseLayers: [
            {
                source: "/static/scripts/src/layerdata/somerville.geojson",
                style: {
                    stroke: 0.1,
                    color: "#397f34",
                    fillColor: "#397f34",
                    fillOpacity: 0.2
                }
            }
        ],

        layers: [
            {
                source: "/static/scripts/src/layerdata/glx.geojson",
                id: "glx",
                title: "Green Line Extension",
                template:
                ('<strong><%= title %></strong>' +
                 '<br>Scheduled Opening: ' +
                 '<%= monthEstimate + "/" + yearEstimate %>' +
                 '<br><a href="<%= factSheet %>" target="_blank">Fact Sheet</a>'),
                color: "green",
                shown: false,
                marker: {
                    type: "circle",
                    color: "green",
                    fillColor: "white",
                    radius: 5,
                    fillOpacity: 1
                },
                features: null
            },
            {
                source: "/static/scripts/src/layerdata/community_path.geojson",
                id: "cp",
                title: "Community Path",
                color: "orange",
                shown: false,
                features: null
            },
            {
                source: "https://raw.githubusercontent.com/cityofsomerville/geodata/master/neighborhoods.geojson",
                id: "neighborhoods",
                title: "Neighborhood Boundaries",
                color: "blue",
                shown: false,
                features: null,
                template: "<%= title %>"
            },
            {
                source: "/static/scripts/src/layerdata/firehydrant.geojson",
                id: "firehydrant",
                title: "Fire Hydrants",
                color: "red",
                shown: false,
                marker: {
                    type: "circle",
                    color: "red",
                    fillColor: "pink",
                    radius: 3,
                    fillOpacity: 1
                },
                features: null
            }
        ],

        // TODO: Respect this value
        showParcelsAboveZoomLevel: 15,

        parcelStyle: {
            stroke: 0.5,
            color: "orange"
        },

        minimapRectStyle: {
            stroke: true,
            weight: 2,
            color: "#ff0000",
            fill: true
        },

        // Esri:
        clientId: "jYLY7AeA1U9xDiWu",
        clientSecret: "64a66909ff724a0a9928838ef4462909"
    };

    if (localConfig) {
        _.extend(config, localConfig);
    }

    return config;
});
