// ProjectItemView
define(["backbone", "utils"], function(B, $u) {
    return B.View.extend({
        template: $u.templateWithId("project-template",
                                    {variable: "project"}),

        className: "project-info info-item",

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
        }
    });
});
