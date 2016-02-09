define(["leaflet", "underscore"],
       function(L, _) {
           function getMarkerPng(isHovered, isSelected) {
               if(isSelected){
                   return "/static/images/marker-active";
               } else if(isHovered){
                   return "/static/images/marker-hover";
               } else {
                   return "/static/images/marker-normal";
               }
           }

           function getIcon(proposal) {
               // Generate an L.icon for a given proposal's parameters
               var isHovered = proposal.get("_hovered"),
                   isSelected = proposal.get("_selected"),

                   png = getMarkerPng(isHovered, isSelected);

               return L.icon({iconUrl: png + "@1x.png",
                              iconRetinaUrl: png + "@2x.png",
                              iconSize: [48, 55]});
           }

           return L.Marker.extend({
               initialize: function(proposal) {
                   var loc = proposal.get("location");

                   if (loc) {
                       L.Marker.prototype.initialize.call(
                           this, loc,
                           {icon: getIcon(proposal),
                            title: proposal.get("address")});
                   }
                   this.proposal = proposal;

                   var self = this;
                   proposal
                       .on("change:location", _.bind(this.locationChanged, this))
                       .on("change:_hovered", _.bind(this.updateIcon, this))
                       .on("change:_selected", _.bind(this.updateIcon, this));

                   return this;
               },

               getModel: function() {
                   return this.proposal;
               },

               locationChanged: function(proposal, loc) {
                   if (loc)
                       this.setLatLng(loc);
               },

               updateIcon: function(proposal) {
                   if (this.zoomed)
                       return;

                   this.setIcon(getIcon(proposal));
               },

               setZoomed: function(n) {
                   var proposal = this.proposal;

                   var images = proposal.get("images");
                   if (!proposal || !images || !images.length)
                       return;

                   var factor = Math.pow(2, n),
                       size = L.point(100*factor, 75*factor);
                   this.setIcon(L.divIcon({
                       className: "zoomed-proposal-marker",
                       iconSize: size,
                       html: "<img src='" + images[0].thumb + "'/>"
                   }));

                   this.zoomed = true;
               },

               unsetZoomed: function() {
                   this.setIcon(getIcon(this.proposal));
                   this.zoomed = false;
               }
           });
       });
