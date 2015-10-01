define(["backbone", "underscore", "utils", "routes"], function(B, _, $u, routes) {
    return B.View.extend({
        template: $u.templateWithId("popup-template",
                                    {variable: "proposal"}),

        events: {
            "click a._details": "showDetails"
        },

        initialize: function(options) {
            this.popup = options.popup;

            this.listenTo(this.model, "change", this.render);
        },

        setContent: function(html) {
            if (this._content) {
                this._content.remove();
                delete this._content;
            }

            var popup =
                    this.popup ||
                    (this.marker && this.marget.getPopup());

            if (popup) {
                var content = $(html);
                popup.setContent(content[0]);
                this._content = content;
                var self = this;
                content .on("click", "a._details", {id: this.model.get("id")},
                            this.showDetails);
            }

            return this;
        },

        render: function() {
            return this.setContent(this.template(this.model.toJSON()));
        },

        destroy: function() {
            this.setContent("");
            this.remove();
        },

        showDetails: function(e) {
            routes.getDispatcher().trigger("showDetails", e.data.id);
        }
    });
});
