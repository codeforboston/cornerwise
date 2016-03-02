define(["leaflet", "underscore"],
       function(L, _) {
           function projectTypeIcon(p) {
               var cat = p.category.replace(/[&.]+/g, "").replace(/[\s-]+/g, "_");
               return "/static/images/icon/" + cat + ".png";
           }

           function getIcon(proposal) {
               var isHovered = proposal.get("_hovered"),
                   isSelected = proposal.get("_selected"),
                   project = proposal.getProject(),
                   className = [
                       "proposal-marker",
                       isHovered ? "marker-hovered" : "",
                       isSelected ? "marker-selected" : "",
                       project ? "project-marker" : ""
                   ].join(" "),
                   html = "";

               if (project) {
                   html = ["<div class='project-type-badge'>",
                           "<img src='", projectTypeIcon(project),
                          "'/></div>"].join("");
               }

               return L.divIcon({
                   className: className,
                   iconSize: L.point(30, 30),
                   html: html
               });
           }

           return L.Marker.extend({
               initialize: function(proposal) {
                   var loc = proposal.get("location");

                   if (loc) {
                       L.Marker.prototype.initialize.call(
                           this, loc,
                           {icon: getIcon(proposal),
                            riseOnHover: true,
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
                       html: "<img src='" + proposal.getThumb() + "'/>"
                   }));

                   this.zoomed = true;
               },

               unsetZoomed: function() {
                   this.setIcon(getIcon(this.proposal));
                   this.zoomed = false;
               }
           });
       });
