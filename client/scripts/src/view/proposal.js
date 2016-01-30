/*
 * View representing a proposal in the proposals list.
 */
define(["backbone", "underscore", "utils"], function(B, _, $u) {
    return B.View.extend({
        initialize: function() {
            this.listenTo(this.model, "change:excluded", this.excludedChanged)
                .listenTo(this.model, "change:selected", this.selectedChanged)
                .listenTo(this.model, "change:refDistance", this.distanceChanged);
        },

        tagName: "div",

        className: "proposal-info info-item",

        template: $u.templateWithId("proposal-template",
                                    {variable: "proposal"}),

        render: function() {
            var proposal = this.model;
            this.$el.html(this.template(proposal));

            if (proposal.get("excluded"))
                this.$el.addClass("excluded");

            if (proposal.get("selected"))
                this.$el.addClass("proposal-selected");

            return this;
        },

        excludedChanged: function(proposal, shouldExclude) {
            if (shouldExclude) {
                this.$el.addClass("excluded");
            } else {
                this.$el.removeClass("excluded");
            }
        },

        selectedChanged: function(proposal, selected) {
            this.$el.toggleClass("proposal-selected", selected);
            if (selected) {
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
            }
        },

        distanceChanged: function(proposal, refDistance) {
            this.$(".distance").html($u.commas(refDistance) + " feet");
        }
    });
});
