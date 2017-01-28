define(["lib/leaflet", "view/proposalPopup", "underscore"],
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

           function getBadge(proposal) {
               return L.divIcon({
                   className: getBadgeClassName(proposal),
                   iconSize: L.point(30, 30)
               });
           }

           return L.Marker.extend({
               initialize: function(proposal) {
                   this.proposal = proposal;

                   var loc = proposal.get("location");

                   if (loc) {
                       L.Marker.prototype.initialize.call(
                           this, loc,
                           {icon: getBadge(proposal),
                            riseOnHover: true});
                       var self = this;
                       proposal
                           .on("change:location", _.bind(this.locationChanged, this))
                           .on("change:_hovered", _.bind(this.updateIcon, this))
                           .on("change:_selected", _.bind(this.onSelected, this));
                   }

                   return this;
               },

               onAdd: function(l) {
                   L.Marker.prototype.onAdd.call(this, l);
                   if (this.proposal.get("_selected"))
                       this.onSelected(this.proposal, true);
               },

               getModel: function() {
                   return this.proposal;
               },

               locationChanged: function(proposal, loc) {
                   if (loc)
                       this.setLatLng(loc);
               },

               updateIcon: function(proposal) {
                   if (_.isNumber(this.zoomed) && !proposal.get("_selected"))
                       this._renderZoomed(proposal, this.zoomed);
                   else
                       this.setIcon(getBadge(proposal));

                   if (proposal.changed._hovered && !proposal.get("_selected")) {
                       var text = proposal.get("address"),
                           others = proposal.get("other_addresses");

                       if (others) {
                           text += "<br/>" + others.split(";").join("<br/>");
                       }
                       this.bindTooltip(text, {permanent: true});
                   } else if (proposal.changed._hovered === false) {
                       this.unbindTooltip();
                   }
               },

               onSelected: function(proposal, isSelected) {
                   this.updateIcon(proposal);

                   this.unbindTooltip();

                   if (isSelected) {
                       var loc = proposal.get("location"),
                       view = new ProposalPopupView({ model: proposal }),
                       popup = this.getPopup();

                       if (!popup) {
                           popup =
                               L.popup({className: "proposal-info-popup",
                                        minWidth: 300,
                                        maxWidth: 300,
                                        autoPanPaddingTopLeft: L.point(5, 15)});
                           popup.setContent(view.render().el);

                           this.bindPopup(popup);
                       }
                       this.openPopup();
                   } else {
                       this.closePopup().unbindPopup();
                   }
               },

               setZoomed: function(n) {
                   if (this.zoomed === n) return;

                   this.zoomed = n;

                   var proposal = this.proposal;

                   if (proposal.get("_selected")) return;

                   this._renderZoomed(proposal, n);
               },

               _renderZoomed: function(proposal, n) {
                   var factor = Math.pow(2, n),
                       size = L.point(100*factor, 75*factor),
                       html = ["<img class='thumb' src='", proposal.getThumb(),  "'/>",
                               "<div class='", getBadgeClassName(proposal),
                               "'>", getBadgeHTML(proposal), "</div>"].join("");

                   this.setIcon(L.divIcon({
                       className: "zoomed-proposal-marker",
                       iconSize: size,
                       html: html
                   }));
               },

               unsetZoomed: function() {
                   this.setIcon(getBadge(this.proposal));
                   this.zoomed = null;
               }
           });
       });
