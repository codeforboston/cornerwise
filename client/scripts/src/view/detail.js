define(["backbone", "underscore", "leaflet",
        "routes", "utils", "config"],
       function(B, _, L, routes, $u, config) {
           return B.View.extend({
               tagName: "div",
               className: "proposal-details",
               template: $u.templateWithId("proposal-details",
                                           {variable: "proposal"}),
               viewName: "details",

               events: {
                   "click a.close": "hide",
                   "click": "dismiss"
               },

               initialize: function() {
                   this.listenTo(this.collection, "change:selected",
                                 this.selectionChanged);

                   var self = this;
                   routes.onStateChange("view", function(view) {
                       self.setShowing(view === "details");
                   });
               },

               selectionChanged: function(proposal) {
                   if (this.model) {
                       this.stopListening(this.model);
                   }

                   this.model = proposal;
                   this.listenTo(proposal, "change", this.renderChange);
                   proposal.fetchIfNeeded();

                   if (this.showing)
                       this.render();
               },

               renderChange: function(proposal) {
                   // Don't re-render if the selection/hover status was the
                   // only change.
                   if (!_.every(_.keys(proposal.changed), function(k) {
                       return _.contains(["selected", "hovered"], k);
                   })) {
                       this.render();
                   }
               },

               setShowing: function(isShowing) {
                   this.showing = isShowing;
                   return this.render();
               },

               render: function() {
                   if (!this.model)
                       this.showing = false;

                   if (!this.showing) {
                       this.$el.hide();
                       return this;
                   }

                   this.$el.show();

                   if (this.minimap)
                       this.minimap.remove();

                   var html = this.template(this.model.toJSON());

                   this.$el.html(html);

                   var minimap =
                           this.minimap =
                           L.map(this.$(".minimap")[0],
                                 {attributionControl: false,
                                  dragging: false,
                                  touchZoom: false,
                                  scrollWheelZoom: false,
                                  boxZoom: false,
                                  zoomControl: false,
                                  layers: [L.tileLayer(config.tilesURL)],
                                  center: this.model.get("location"),
                                  zoom: 17});

                   var parcel = this.model.get("parcel");

                   if (parcel) {
                       var parcelLayer = L.GeoJSON.geometryToLayer(parcel);
                       parcelLayer.setStyle(config.parcelStyle);
                       minimap.addLayer(parcelLayer)
                           .setView(parcelLayer.getBounds().getCenter());
                   }

                   return this;
               },

               hide: function() {
                   return this.setShowing(false);
               },

               /**
                * If the user clicks on the #overlay element itself (i.e., the
                * grayed-out margins), hide the details view.
                */
               dismiss: function(e) {
                   if (e.target == e.currentTarget)
                       routes.clearHashKey("view");
               },

               onRoute: function(route, _params) {
                   if (route !== "details")
                       this.hide();
               },

               onShow: function(id) {
                   var proposal = this.collection.get(id);

                   if (proposal) {
                       this.show(proposal);
                   }
               },

               show: function(proposal) {
                   this.model = proposal;

                   return this.setShowing(true);
               }
           });
       });
