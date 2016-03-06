define(["leaflet", "underscore"],
       function(L, _) {
           function projectTypeIcon(p) {
               var cat = p.category.replace(/[&.]+/g, "").replace(/[\s-]+/g, "_");
               return "/static/images/icon/" + cat + ".png";
           }

           function getIconClassName(proposal) {
               var isHovered = proposal.get("_hovered"),
                   isSelected = proposal.get("_selected"),
                   project = proposal.getProject();

               return [
                   "proposal-marker",
                   isHovered ? "marker-hovered" : "",
                   isSelected ? "marker-selected" : "",
                   project ? "project-marker" : ""
               ].join(" ");
           }

           function getIconHTML(proposal) {
               var project = proposal.getProject(),
                   html = "";

               if (project) {
                   html = ["<div class='project-type-badge'>",
                           "<img src='", projectTypeIcon(project),
                           "'/></div>"].join("");
               }

               return html;
           }

           function getIcon(proposal) {
               return L.divIcon({
                   className: getIconClassName(proposal),
                   iconSize: L.point(30, 30),
                   html: getIconHTML(proposal)
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
                   this.zoomed = null;

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
                   if (this.zoomed !== null)
                       return;

                   this.setIcon(getIcon(proposal));
               },

               setZoomed: function(n) {
                   var proposal = this.proposal,
                       factor = Math.pow(2, n),
                       size = L.point(100*factor, 75*factor),
                       html = ["<img class='thumb' src='", proposal.getThumb(),  "'/>",
                               "<div class='", getIconClassName(proposal),
                               "'>", getIconHTML(proposal), "</div>"].join("");
                   console.log(html);

                   this.setIcon(L.divIcon({
                       className: "zoomed-proposal-marker",
                       iconSize: size,
                       html: html
                   }));

                   this.zoomed = n;
               },

               unsetZoomed: function() {
                   this.setIcon(getIcon(this.proposal));
                   this.zoomed = null;
               }
           });
       });
