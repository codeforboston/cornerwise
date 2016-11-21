/**
 * config.js
 *
 * Application configuration options
 */

define(["optional!localConfig", "underscore"], function(localConfig, _) {
    var config = {
        // String template or function used by Leaflet to generate the
        // image URLs for map files.
        tilesURL: "https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png",
        tilesCredit: "Map tiles by CartoDB, under CC BY 3.0. Data by OpenStreetMap, under ODbL",

        backendURL: "",

        // URL from which to fetch the JSON representing the latest
        // planning and zoning report.
        pzURL: "/proposal/list",

        // Lat/long for the southwest and northeasth corners of the
        // map's initial viewing area.
        bounds:  [[42.37236882604975, -71.14565849304199],
                  [42.41680352972898, -71.04806900024413]],

        regionBounds: null,

        // Default reference location:
        refPointDefault: {lat: 42.387545768736246,
                          lng: -71.09950304031372},
        refMarkerColor: "red",
        refPointName: "City Hall",

        // The style that will be applied to the rectangle representing the
        // bounds of the current area filter:
        filterBoundsStyle: {
            weight: 2,
            color: "red",
            fillColor: "red",
            fillOpacity: "0"
        },

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

        regions: [
            {
                id: "somerville",
                regionName: "Somerville, MA",
                source: "/static/scripts/src/layerdata/somerville.geojson"
            },
            {
                id: "cambridge",
                regionName: "Cambridge, MA",
                source: "/static/scripts/src/layerdata/cambridge.geojson"
            }
        ],

        regionStyle: {
            weight: 3,
            color: "#4fb8f7",
            fillColor: "#4fb8f7",
            fillOpacity: 0.15
        },


        layers: [
            {
                source: "/static/scripts/src/layerdata/glx.geojson",
                id: "glx",
                icon: "glx",
                iconCredit: "Scott de Jonge",
                title: "Train - Green Line Extension",
                short: "Train",
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
            // {
            //     source: "/static/scripts/src/layerdata/community_path.geojson",
            //     id: "cp",
            //     info: "The Somerville Community Path is a paved bike and walking path. It begins at Davis Square, where it connects to the Cambridge Linear Path, and ends at Lowell Street. Once extended, it will end at NorthPoint, Cambridge.",
            //     title: "Community Path Extension",
            //     color: "orange",
            //     shown: false,
            //     features: null
            // },
            {
                source: "/static/scripts/src/layerdata/MBTABus88.geojson",
                id: "mbtabus",
                icon: "mbta",
                iconCredit: "Freepik",
                info: "Major MBTA bus routes",
                title: "Major Bus Routes",
                short: "Bus",
                color: "black",
                shown: false,
                marker: {
                    type: "circle",
                    color: "black",
                    fillColor: "blue",
                    radius: 5,
                    fillOpacity: 1
                },
                features: null
            },
            {
                source: "https://raw.githubusercontent.com/cityofsomerville/geodata/master/neighborhoods.geojson",
                id: "neighborhoods",
                icon: "home",
                info: "Approximate and unofficial neighborhood boundaries",
                iconCredit: "Freepik",
                title: "Neighborhood Boundaries",
                short: "Neighborhoods",
                color: "blue",
                shown: false,
                features: null,
                template: "<%= title %>"
            },
            {
                source: "https://raw.githubusercontent.com/cityofsomerville/geodata/master/wards.geojson",
                id: "wards",
                icon: "wards",
                iconCredit: "Scott de Jonge",
                info: "Somerville is divided into seven wards, each represented by an alderman.",
                title: "Wards",
                short: "Wards",
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

        // Esri:
        clientId: "jYLY7AeA1U9xDiWu",
        clientSecret: "64a66909ff724a0a9928838ef4462909",

        // Map of handles to names
        attributeNames: {

        }
    };

    if (localConfig) {
        _.extend(config, localConfig);
    }

    return config;
});
