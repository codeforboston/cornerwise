/*
 * View representing a permit in the permits list.
 */
define(["backbone", "underscore"], function(B, _) {
    return B.View.extend({
        initialize: function() {
            this.listenTo(this.model, "change", this.changed);
        },

        tagName: "tr",

        template: _.template('<td><%= number %> <%= street %></td>' +
                             '<td><%= description %></td>' +
                             '<td><%= caseNumber %></td>'),

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
