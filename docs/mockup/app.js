App = {
    init: function() {

        var mapElt = document.getElementById("map"),
            map = L.map(mapElt);

        window.map = map;

        map.addLayer(L.tileLayer("http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"));
        map.fitBounds([[42.42009843116784, -71.05768203735352],
                       [42.370720143531976, -71.14445686340332]]);
        $.getJSON("https://raw.githubusercontent.com/cityofsomerville/geodata/master/somerville.geojson")
            .done(function(features) {
                map.addLayer(
                    L.geoJson(features,
                              {style: {
                                  stroke: 0.5,
                                  color: "orange",
                                  fill: false
                              }}));
            });
    }
}
