/**
 * config.js
 *
 * Application configuration options
 */

define([], function() {
    return {
        // String template or function used by Leaflet to generate the
        // image URLs for map files.
        tilesURL: "http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
        //tilesURL: "http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",

        // URL from which to fetch the JSON representing the latest
        // planning and zoning report.
        pzURL: "https://script.google.com/macros/s/AKfycbxdNiXwOYTAxEZE4LuGcCFsOW-JpQr9bQl6hx3NZIF4oc19UoBT/exec",
        mapId: "zoning-map",

        // Lat/long for the southwest
        bounds: [[42.371861543730496, -71.13338470458984],
                 [42.40393908425197, -71.0679817199707]],

        // Default reference location:
        refPointDefault: {lat: 42.387545768736246,
                          lng: -71.09950304031372},
        refMarkerColor: "red",

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
                source: "/scripts/src/layerdata/somerville.geojson",
                style: {
                    stroke: 0,
                    fillColor: "#397f34",
                    fillOpacity: 0.2
                }
            }
        ],

        layers: [
            {
                id: "glx",
                title: "Green Line Extension",
                template:
                ('<strong><%= title %></strong>' +
                 '<br>Scheduled Opening: ' +
                 '<%= monthEstimate + "/" + yearEstimate %>' +
                 '<br><a href="<%= factSheet %>" target="_blank">Fact Sheet</a>'),
                source: "/scripts/src/layerdata/glx.geojson",
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
                id: "cp",
                title: "Community Path",
                source: "/scripts/src/layerdata/community_path.geojson",
                color: "orange",
                shown: false,
                features: null
            }
        ],

        // Esri:
        clientId: "jYLY7AeA1U9xDiWu",
        clientSecret: "64a66909ff724a0a9928838ef4462909"
    };
});
