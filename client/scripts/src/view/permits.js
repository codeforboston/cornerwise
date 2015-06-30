define(["backbone", "permits", "permit-view"], function(B, Permits, PermitView) {
    return B.View.extend({
        initialize: function() {
            //this.listenTo(this.model, "change", this.render);
            this.listenTo(this.collection, "add", this.permitAdded);
            this.listenTo(this.collection, "change", this.permitChanged);
        },

        el: function() {
            return document.getElementById("permit-list");
        },

        tagName: "ul",

        render: function() {
            return this;
        },

        permitAdded: function(permit) {
            var view = new PermitView({model: permit});
            this.$el.append(view.render().el);
        },

        permitChanged: function(change) {

        }
    });
});
