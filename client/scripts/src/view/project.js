define(["backbone", "utils"], function(B, $u) {
    return B.View.extend({
        template: $u.templateWithId("project-template",
                                    {variable: "project"}),

        className: "project info-item",

        events: {
            "mouseover": "beginHover",
            "mouseout": "endHover"
        },

        initialize: function() {
            this.listenTo(this.model, "change", this.render)
                .listenTo(this.model, "change:selected", this.selectedChanged);
        },

        render: function() {
            this.$el.html(this.template(this.model));

            return this;
        },

        selectedChanged: function(p, selected) {
            this.$el.toggleClass("selected", selected);
        },

        beginHover: function() {
            this.model.set("hovered", true);
        },

        endHover: function() {
            this.model.set("hovered", false);
        }
    });
});
