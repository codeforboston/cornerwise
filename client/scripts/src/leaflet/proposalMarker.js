define(["leaflet", "proposal-popup-view", "underscore"],
       function(L, ProposalPopupView, _) {
           function projectTypeIcon(p) {
               var cat = p.category.replace(/[&.]+/g, "")
                       .replace(/[\s-]+/g, "_")
                       .toLowerCase();
               return "/static/images/icon/" + cat + ".png";
           }

           function getBadgeClassName(proposal) {
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

           function getBadgeHTML(proposal) {
               var project = proposal.getProject(),
                   html = "";

               // if (project) {
               //     html =
               //         "<img src='" + projectTypeIcon(project) +
               //         "' class='project-type-badge'/>";
               // }

               return html;
           }

           function getBadge(proposal) {
               return L.divIcon({
                   className: getBadgeClassName(proposal),
                   iconSize: L.point(30, 30),
                   html: getBadgeHTML(proposal)
               });
           }

           return L.Marker.extend({
               initialize: function(proposal, zoom) {
                   var loc = proposal.get("location");

                   if (loc) {
                       L.Marker.prototype.initialize.call(
                           this, loc,
                           {icon: getBadge(proposal),
                            riseOnHover: true,
                            title: proposal.get("address")});
                   }
                   this.proposal = proposal;
                   this.zoomed = zoom;

                   var self = this;
                   proposal
                       .on("change:location", _.bind(this.locationChanged, this))
                       .on("change:_hovered", _.bind(this.updateIcon, this))
                       .on("change:_selected", _.bind(this.onSelected, this));

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
                   if (_.isNumber(this.zoomed))
                       this.setZoomed(this.zoomed);
                   else
                       this.setIcon(getBadge(proposal));
               },

               onSelected: function(proposal) {
                   var loc = proposal.get("location"),
                       view = new ProposalPopupView({ model: proposal });
                   this.updateIcon(proposal);
                   L.popup({className: "proposal-info-popup",
                            minWidth: 300,
                            maxWidth: 300,
                            autoPanPaddingTopLeft: L.point(5, 15)})
                       .setLatLng(loc)
                       .setContent(view.render().el)
                       .openOn(this._map);
               },

               setZoomed: function(n) {
                   var proposal = this.proposal,
                       factor = Math.pow(2, n),
                       size = L.point(100*factor, 75*factor),
                       html = ["<img class='thumb' src='", proposal.getThumb(),  "'/>",
                               "<div class='", getBadgeClassName(proposal),
                               "'>", getBadgeHTML(proposal), "</div>"].join(""),
                       className = proposal.get("_selected") ? " marker-selected" : "";

                   this.setIcon(L.divIcon({
                       className: "zoomed-proposal-marker" + className,
                       iconSize: size,
                       html: html
                   }));

                   this.zoomed = n;
               },

               unsetZoomed: function() {
                   this.setIcon(getBadge(this.proposal));
                   this.zoomed = null;
               }
           });
       });
