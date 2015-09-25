define(["backbone", "utils"], function(B, $u) {
    return B.View.extend({
        tagName: "div",
        className: "proposal-details",
        template: $u.templateWithId("proposal-details"),

        initialize: function() {
            this.listenTo(this.model, "change", this.render);
        },

        render: function() {
            this.$el.html(this.template(this.model.toJSON()));
        }
    });
});
