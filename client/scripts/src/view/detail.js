define(["backbone", "routes", "utils"], function(B, routes, $u) {
    return B.View.extend({
        tagName: "div",
        className: "proposal-details",
        template: $u.templateWithId("proposal-details"),
        el: "#overlay",

        initialize: function() {
            this.listenTo(this.model, "change", this.render);

            routes.getRouter().on("route", this.route);
        },

        render: function() {
            var html = this.template(this.model.toJSON());
            console.log(html);
            this.$el.html(html);
        },

        hide: function() {
            this.$el.hide();
        },

        show: function(proposal) {
            this.model = proposal;
            this.render();
            this.$el.show();
        }
    });
});
