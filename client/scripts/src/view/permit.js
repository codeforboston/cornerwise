/*
 * View representing a permit in the permits list.
 */
define(["backbone", "underscore", "utils"], function(B, _, $u) {
    return B.View.extend({
        initialize: function() {
            this.listenTo(this.model, "change:excluded", this.excludedChanged)
                .listenTo(this.model, "change:selected", this.selectedChanged)
                .listenTo(this.model, "change:hovered", this.hoveredChanged)
                .listenTo(this.model, "change:refDistance", this.distanceChanged);
        },

        tagName: "tr",

        className: "permit-info",

        events: {
            "mouseover": "beginHover",
            "mouseout": "endHover",
            "click": "onClick"
        },

        template: $u.template('<td><b><%= description %></b>' +
                              '<br><%= number %> <%= street %>' +
                              '<br><span class="distance"><%= refDistance %> feet</span></td>' +
                              '<td><%= caseNumber %></td>' +
                              '<td><%= formatDate(submitted) %></td>'
                             ),

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

            var parent = this.$el.parent(),
                topOffset = parent.scrollTop(),
                botOffset = topOffset + parent.height(),
                eltTop = this.el.offsetTop,
                eltBottom = eltTop + this.$el.height();

            if (eltTop > botOffset || eltBottom < topOffset) {
                parent.animate({
                    scrollTop: eltTop - 30
                }, 200);
            }
        },

        distanceChanged: function(permit, refDistance) {
            this.$(".distance").html(refDistance + " feet");
        },

        beginHover: function(){
            this.model.set({"hovered": true});
        },

        endHover: function(){
            this.model.set({"hovered": false});
        }
    });
});
