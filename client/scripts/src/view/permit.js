/*
 * View representing a permit in the permits list.
 */
define(["backbone", "underscore"], function(B, _) {
    return B.View.extend({
        initialize: function() {
            this.listenTo(this.model, "change", this.changed);
        },

        tagName: "li",

        template: _.template('<div class="permit-name"><%= number %> <%= street %></div>' +
                             '<div class="permit-desc"><%= description %></div>' +
                             '<div class="permit-details"><%= caseNumber %></div>'),

        render: function() {
            var permit = this.model;
            this.$el.html(this.template(permit.toJSON()));
            this.$el.addClass("permit-info");

            if (permit.get("excluded")) {
                this.$el.addClass("excluded");
            }

            return this;
        },

        changed: function(permit) {
            if (permit.changed.hasOwnProperty("excluded")) {
                if (permit.changed.excluded) {
                    this.$el.addClass("excluded");
                } else {
                    this.$el.removeClass("excluded");
                }
            }
        }
    });
});
