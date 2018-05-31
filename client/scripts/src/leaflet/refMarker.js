define(["lib/leaflet", "config", "underscore", "utils", "appState"],
       function(L, config, _, $u, appState) {
           var template = $u.templateWithUrl("/static/template/refMarkerPopup.html");

           return L.FeatureGroup.extend({
               initialize: function(refLoc) {
                   var fg = L.FeatureGroup.prototype.initialize.call(this, []);
                   var icon = L.icon({iconUrl: "/static/images/cornerwise-owl.png",
                                      iconRetinaUrl: "/static/images/cornerwise-owl.png",
                                      iconSize: [51, 68],
                                      iconAnchor: [25.5, 68],
                                      popupAnchor: [0, -70],
                                      className: "ref-marker"});
                   var marker = this.marker = L.marker(refLoc.getPoint(),
                                          {icon: icon}).addTo(this);

                   var popup = L.popup({className: "subscribe-popup",
                                        closeButton: false});
                   marker.bindPopup(popup);

                   refLoc.on("change", this.locationChange, this);
                   appState.on("subscribeStart", this.subscribeStarted, this);
                   this.on("add", function() {
                       template(null, function(html) {
                           popup.setContent(html);
                           marker.openPopup();
                       });
                   });

                   return fg;
               },

               locationChange: function(refLoc) {
                   this.marker.setLatLng(refLoc.getPoint());
               },

               subscribeStarted: function() {
                   this.marker.closePopup();
               },

               _add: function() {
                   console.log(arguments);
               }
           });
       });
