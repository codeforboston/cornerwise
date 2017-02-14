// This file is probably no longer necessary
define(["lib/leaflet", "config", "underscore"],
       function(L, config, _) {
           return L.FeatureGroup.extend({
               initialize: function(refLoc) {
                   var fg = L.FeatureGroup.prototype.initialize.call(this, []);
                   var icon = L.icon({iconUrl: "/static/images/cornerwise-owl.png",
                                      iconRetinaUrl: "/static/images/cornerwise-owl.png",
                                      iconSize: [51, 68]});
                   this.marker = L.marker(refLoc.getPoint(),
                                          {icon: icon}).addTo(this);
                   this.marker.bindPopup("")
                       .on("popupopen", _.bind(this.onPopup, this, refLoc));

                   refLoc.on("change", this.locationChange, this);

                   return fg;
               },

               locationChange: function(refLoc) {
                   this.marker.setLatLng(refLoc.getPoint());
               },

               onPopup: function(refLoc, e) {
                   // Show the current address:
                   var html = ["Centered on:<br/>"],
                       address = refLoc.get("address");

                   if (address)
                       html.push(_.escape(address));
                   else
                       html.push(refLoc.get("lat"), ", ", refLoc.get("lng"));

                   e.popup.setContent(html.join(""));
               }
           });
       });
