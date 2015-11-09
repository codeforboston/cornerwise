App = {
    init: function() {

        var mapElt = document.getElementById("map"),
            map = L.map(mapElt),
            proposals = L.featureGroup();

        window.map = map;

        map.addLayer(L.tileLayer("http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"));
        map.addLayer(proposals);
        map.fitBounds([[42.4190212708995, -71.07150077819824],
                       [42.372305415983895, -71.13570213317871]]);
        $.getJSON("https://raw.githubusercontent.com/cityofsomerville/geodata/master/somerville.geojson")
            .done(function(features) {
                map.addLayer(
                    L.geoJson(features,
                              {style: {
                                  stroke: 0.5,
                                  color: "#EB4E12",
                                  fill: false
                              }}));
            });

        $.getJSON("http://localhost:3000/proposal/list")
            .done(function(response) {
                $(response.proposals).each(function(i, feature) {
                    if (feature.location) {
                        var marker = L.marker(feature.location).addTo(proposals);

                        marker.proposal = feature;
                    }
                });
            });

        function updateMarkers() {
            if (map.getZoom() >= 17) {
                var bounds = map.getBounds();
                proposals.eachLayer(function(marker) {
                    var images = marker.proposal.images;
                    if (!images || !images.length ||
                        !bounds.contains(marker.getLatLng()))
                        return;

                    marker._unzoomedIcon =
                        marker.icon || new L.Icon.Default();
                    marker.setIcon(L.divIcon({
                        className: "zoomed-proposal-marker",
                        iconSize: L.point(100, 75),
                        html: "<img src='http://localhost:3000" +
                            images[0].thumb + "'/>"
                    }));
                });
            } else {
                proposals.eachLayer(function(marker) {
                    if (marker._unzoomedIcon) {
                        marker.setIcon(marker._unzoomedIcon);
                        delete marker._unzoomedIcon;
                    }
                });
            }
        }

        map.on("zoomend", updateMarkers)
            .on("moveend", updateMarkers);

        $("#main_activated").on("change", function(e) {
            if (this.checked) {
                $(document.body).addClass("main");
            } else {
                $(document.body).removeClass("main");
            }
        });

        if ($(document.body).hasClass("main")) {
            $("#main_activated").prop("checked", true);
        }
    }
};
