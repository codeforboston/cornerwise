/*
 * View representing a permit in the permits list.
 */
define(["backbone", "underscore"], function(B, _) {
    return B.View.extend({
        initialize: function() {
            this.listenTo(this.model, "change:excluded", this.excludedChanged)
                .listenTo(this.model, "change:selected", this.selectedChanged)
                .listenTo(this.model, "change:hovered", this.hoveredChanged);
        },

        tagName: "tr",

        className: "permit-info",

        events: {
            "mouseover": "beginHover",
            "mouseout": "endHover",
            "click": "onClick"
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

        onClick: function(e) {
            this.model.set("selected", true);
        },

        hoveredChanged: function(permit, hovered) {
            this.$el.toggleClass("permit-hovered", hovered);
        },

        selectedChanged: function(permit, selected) {
            this.$el.toggleClass("permit-selected", selected);
        },

        beginHover: function(){
            this.model.set({"hovered": true});
        },

        endHover: function(){
            this.model.set({"hovered": false});
        }
    });
});
