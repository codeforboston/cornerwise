define(["backbone", "underscore", "utils", "routes"], function(B, _, $u, routes) {
    return B.View.extend({
        template: $u.templateWithId("popup-template"),

        events: {
            "click ._details": "showDetails"
        },

        initialize: function(options) {
            this.popup = options.popup;

            this.listenTo(this.model, "change", this.render);
        },

        setContent: function(html) {
            if (this.popup)
                this.popup.setContent(html);
            else if (this.marker)
                this.marker.setPopupContent(html);
            else if (this.$el)
                this.$el.html(html);
        },

        render: function() {
            this.setContent(this.template(this.model.toJSON()));

            return this;
        },

        destroy: function() {
            this.undelegateEvents();
            this.remove();
        },

        showDetails: function(e) {
            var proposalId = this.model.get("id");
            routes.getRouter().navigate("details/" + proposalId,
                                        {trigger: true});
        }
    });
});
