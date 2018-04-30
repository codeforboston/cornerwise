define(["lib/leaflet", "view/proposalPopup", "underscore", "utils"],
       function(L, ProposalPopupView, _, $u) {
           function projectTypeIcon(p) {
               var cat = p.category.replace(/[&.]+/g, "")
                       .replace(/[\s-]+/g, "_")
                       .toLowerCase();
               return "/static/images/icon/" + cat + ".png";
           }

           function getBadgeClassName(proposal) {
               var attrs = proposal.attributes,
                   approved = (attrs.status||"").match(/^approved$/i);

               return $u.classNames({
                   "marker-hovered": attrs._hovered,
                   "marker-selected": attrs._selected,
                   "proposal-complete": attrs.complete,
                   "proposal-approved": approved,
                   "project-marker": proposal.getProject()
               }, "proposal-marker");
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
                       this.bindTooltip(text, {offset: L.point(10, 0),
                                               permanent: true});
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
                                        autoPan: false});
                           popup.setContent(view.render().el);

                           this._autoClosedPopup = false;
                           this.bindPopup(popup);
                       }
                       this.openPopup();
                   } else {
                       this._autoClosedPopup = true;
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
                               "'>", "</div>"].join("");

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
