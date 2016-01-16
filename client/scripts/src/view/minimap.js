define(["backbone", "leaflet", "underscore", "config"],
       function(B, L, _, config) {
           return B.View.extend({
               markerStyle: {
                   color: "black",
                   fillColor: "#4FB8F7",
                   fillOpacity: 1,
                   radius: 2
               },
               initialize: function(options) {
                   var linked = options.linkedMap,
                       selection = options.selection,
                       resetButton = this.$el.siblings(".reset");

                   if (!linked) return;

                   var map = L.map(this.el,
                                   {attributionControl: false,
                                    dragging: false,
                                    touchZoom: false,
                                    scrollWheelZoom: false,
                                    boxZoom: false,
                                    zoomControl: false,
                                    minZoom: 11,
                                    maxZoom: 11,
                                    layers: [
                                        L.tileLayer(config.tilesURL)
                                    ]}),
                       rectLayer = L.rectangle(linked.getBounds(),
                                               config.minimapRectStyle);
                   map.addLayer(rectLayer)
                       .setZoom(11)
                       .setView(linked.getCenter());

                   this.rect = rectLayer;

                   linked.on("drag moveend resize zoomend",
                             function(e) {
                                 rectLayer.setBounds(linked.getBounds());

                                 resetButton.toggle(linked.getZoom() > 14);
                             });
                   map.on("click",
                          function(e) {
                              linked.setView(e.latlng);
                          });
                   resetButton.on("click",
                                  function(e) {
                                      linked.fitBounds(config.bounds);

                                      return false;
                                  });

                   if (selection) {
                       var markers = [], style = this.markerStyle;
                       selection.on("selectionLoaded",
                                    function(_sel, ids) {
                                        _.each(markers,
                                               map.removeLayer,
                                               map);
                                        _.each(ids, function(id) {
                                            var model = selection.get(id),
                                                loc = model.get("location");

                                            if (loc) {
                                                markers.push(
                                                    L.circleMarker(
                                                        loc, style)
                                                        .addTo(map));
                                            }
                                        });
                                    });
                   }

                   $.getJSON("/static/scripts/src/layerdata/somerville.geojson")
                       .done(function(features) {
                           map.addLayer(
                               L.geoJson(features,
                                         {style: {
                                             stroke: true,
                                             weight: 2,
                                             fill: false
                                         }}));
                       });
               }
           });
       });
