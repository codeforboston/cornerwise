define(["backbone", "underscore", "leaflet",
        "routes", "utils", "config"],
       function(B, _, L, routes, $u, config) {
    return B.View.extend({
        tagName: "div",
        className: "proposal-details",
        template: $u.templateWithId("proposal-details",
                                    {variable: "proposal"}),
        el: "#overlay",
        events: {
            "click a.close": "hide",
            "click": "dismiss"
        },

        initialize: function() {
            this.listenTo(this.collection, "change:selected",
                          this.selectionChanged);

            routes.getDispatcher().on("showDetails", _.bind(this.onShow, this));
        },

        selectionChanged: function(proposal) {
            if (this.model) {
                this.stopListening(this.model);
            }

            this.model = proposal;
            this.listenTo(proposal, "change", this.renderChange);
            proposal.fetchIfNeeded();

            if (this.showing)
                this.render(proposal);
        },

        renderChange: function(proposal) {
            // Don't re-render if the selection/hover status was the
            // only change.
            if (!_.every(_.keys(proposal.changed), function(k) {
                return _.contains(["selected", "hovered"], k);
            })) {
                this.render(proposal);
            }
        },

        render: function() {
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
                           zoomControl: false});
            minimap
                .setView(this.model.get("location"))
                .setZoom(17)
                .addLayer(L.tileLayer(config.tilesURL));

            var parcel = this.model.get("parcel");

            if (parcel) {
                var parcelLayer = L.GeoJSON.geometryToLayer(parcel);
                parcelLayer.setStyle(config.parcelStyle);
                minimap.addLayer(parcelLayer)
                    .setView(parcelLayer.getBounds().getCenter());
            }
        },

        hide: function() {
            this.$el.hide();
            this.showing = false;
        },

        /**
         * If the user clicks on the #overlay element itself (i.e., the
         * grayed-out margins), hide the details view.
         */
        dismiss: function(e) {
            if (e.target == e.currentTarget)
                this.hide();
        },

        onShow: function(id) {
            var proposal = this.collection.get(id);

            if (proposal) {
                this.show(proposal);
            }
        },

        show: function(proposal) {
            if (proposal && this.model &&
                this.model.get("id") !== proposal.get("id"))
            {
                this.selectionChanged(proposal);
            }

            this.render();
            this.$el.show();
            this.showing = true;
        }
    });
});
