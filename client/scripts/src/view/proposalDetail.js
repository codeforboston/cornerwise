define(["backbone", "underscore", "leaflet",
        "routes", "utils", "config"],
       function(B, _, L, routes, $u, config) {
           return B.View.extend({
               // template: $u.templateWithId("proposal-details",
               //                             {variable: "proposal"}),
               template: $u.templateWithUrl("/static/template/proposalDetail.html",
                                            {variable: "proposal"}),
               viewName: "details",

               events: {
                   "click a.close": "dismiss",
                   "click": "dismiss"
               },

               initialize: function() {
                   this.collection.on("selectionLoaded",
                                      this.selectionLoaded,
                                      this);
                   this.model = this.collection.getSelection()[0];
               },

               selectionLoaded: function(coll, ids) {
                   var proposal = coll.get(ids[0]);
                   this.model = proposal;
                   this.render();
                   var self = this;
                   proposal.fetchIfNeeded().then(function(model) {
                       self.render();
                   });
               },

               renderChange: function(proposal) {
                   if (!_.every(_.keys(proposal.changed, function(k) {

                       return k === "selected" || k === "hovered";
                   }))) {
                       this.render();
                   }
               },

               setShowing: function(isShowing) {
                   this.showing = isShowing;
                   return this.render();
               },

               render: function() {
                   if (!this.showing || !this.model) {
                       this.$el.hide();
                       return this;
                   }

                   this.$el.show();

                   if (this.minimap)
                       this.minimap.remove();

                   var self = this;
                   this.template(
                       this.model.toJSON(),
                       function(html) {
                           self.$el.html(html);

                           var minimap =
                                   self.minimap =
                                   L.map(self.$(".minimap")[0],
                                         {attributionControl: false,
                                          dragging: false,
                                          touchZoom: false,
                                          scrollWheelZoom: false,
                                          boxZoom: false,
                                          zoomControl: false,
                                          layers: [L.tileLayer(config.tilesURL)],
                                          center: self.model.get("location"),
                                          zoom: 17});

                           var parcel = self.model.get("parcel");

                           if (parcel) {
                               var parcelLayer = L.GeoJSON.geometryToLayer(parcel);
                               parcelLayer.setStyle(config.parcelStyle);
                               minimap.addLayer(parcelLayer)
                                   .setView(parcelLayer.getBounds().getCenter());
                           }
                       });

                   return this;
               },

               /**
                * If the user clicks on the #overlay element itself (i.e., the
                * grayed-out margins), hide the details view.
                */
               dismiss: function(e) {
                   if (e.target == e.currentTarget)
                       routes.setHashKey("view", "main");
                   return false;
               },

               onShow: function(id) {
                   var proposal = this.collection.get(id);

                   if (proposal) {
                       this.show(proposal);
                   }
               },

               hide: function() {
                   return this.setShowing(false);
               },

               show: function() {
                   return this.setShowing(true);
               }
           });
       });
