define(["backbone", "underscore", "leaflet",
        "routes", "utils", "config"],
       function(B, _, L, routes, $u, config) {
           return B.View.extend({
               template: $u.templateWithUrl("/static/template/proposalDetail.html",
                                            {variable: "proposal"}),
               viewName: "details",

               initialize: function() {
                   this.collection.on("selectionLoaded",
                                      this.selectionLoaded,
                                      this);
                   this.collection.on("selectionRemoved",
                                      this.selectionRemoved,
                                      this);
                   this.model = this.collection.getSelection()[0];
               },

               selectionLoaded: function(coll, ids) {
                   var proposal = coll.get(ids[0]);
                   proposal.on("change", this.renderChange, this);
                   this.model = proposal;
                   this.render();

                   proposal.fetchIfNeeded();
               },

               selectionRemoved: function(coll, ids) {
                   var proposal = coll.get(ids[0]);
                   proposal.off("change", this.renderChange, this);
               },

               renderChange: function(proposal) {
                   if (!_.every(_.keys(proposal.changed), function(k) {
                       return k === "selected" || k === "hovered";
                   })) {
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
