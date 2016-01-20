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

        regionName: "Somerville",

        regionBounds: null,

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
                    weight: 3,
                    color: "#4fb8f7",
                    fillColor: "#4fb8f7",
                    fillOpacity: 0.15
                }
            }
        ],

        layers: [
            {
                source: "/static/scripts/src/layerdata/glx.geojson",
                id: "glx",
                title: "Green Line Extension",
                info: "The Green Line Extension plans to bring light rail services to areas of Somerville and Medford currently underserved by the MBTA.",
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
                info: "The Somerville Community Path is a paved bike and walking path. It begins at Davis Square, where it connects to the Cambridge Linear Path, and ends at Lowell Street. Once extended, it will end at NorthPoint, Cambridge.",
                title: "Community Path Extension",
                color: "orange",
                shown: false,
                features: null
            },
            {
                source: "/static/scripts/src/layerdata/MBTABus88.geojson",
                id: "mbtabus88",
                info: "Somervile bus routes",
                title: "MbtaBus",
                color: "pink",
                shown: false,
                features: null
            },
            {
                source: "https://raw.githubusercontent.com/cityofsomerville/geodata/master/neighborhoods.geojson",
                id: "neighborhoods",
                info: "These neighborhood boundaries are unofficial and approximate.",
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
            },
            {
                source: "https://raw.githubusercontent.com/cityofsomerville/geodata/master/wards.geojson",
                id: "wards",
                title: "Wards",
                color: "purple",
                shown: false,
                features: null,
                template: "<%= title %>"
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
