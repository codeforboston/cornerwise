App = {
    init: function() {

        var mapElt = document.getElementById("map"),
            map = L.map(mapElt);

        window.map = map;

        map.addLayer(L.tileLayer("http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"));
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
        $("#main_activated").on("change", function(e) {
            if (this.checked) {
                $(document.body).addClass("main");
            } else {
                $(document.body).removeClass("main");
            }
        });
    }
};
