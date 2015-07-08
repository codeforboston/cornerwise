/*
 * View representing a permit in the permits list.
 */
define(["backbone", "underscore"], function(B, _) {
    return B.View.extend({
        initialize: function() {
            this.listenTo(this.model, "change:excluded", this.excludedChanged);
        },

        tagName: "tr",

        className: "permit-info",

        events: {
            "mouseover": "beginHover",
            "mouseout": "endHover"
        },

        template: _.template('<td><b><%= description %></b><br><%= number %> <%= street %></td>' +
                             '<td><%= caseNumber %></td>'),

        render: function() {
            var permit = this.model;
            this.$el.html(this.template(permit.toJSON()));

            if (permit.get("excluded")) {
                this.$el.addClass("excluded");
            }

            return this;
        },

        excludedChanged: function(permit, shouldExclude) {
            if (shouldExclude) {
                this.$el.addClass("excluded");
            } else {
                this.$el.removeClass("excluded");
            }
        },

        beginHover: function(){
            this.model.set({"hovered": true});
            this.$el.removeClass("permit-info");
            this.$el.addClass("permit-hovered");
        },

        endHover: function(){
            this.model.set({"hovered": false});
            this.$el.removeClass("permit-hovered");
            this.$el.addClass("permit-info");
        }
    });
});
