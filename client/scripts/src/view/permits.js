define(["backbone", "permits", "permit-view"], function(B, Permits, PermitView) {
    return B.View.extend({
        initialize: function() {
            //this.listenTo(this.model, "change", this.render);
            this.listenTo(this.collection, "add", this.permitAdded);
            this.listenTo(this.collection, "change", this.permitChanged);
            this.listenTo(this.collection, "fetching", this.fetchingBegan);
            this.listenTo(this.collection, "reset", this.fetchingComplete);
        },

        el: function() {
            return document.getElementById("permit-list");
        },

        tagName: "table",

        render: function() {
            return this;
        },

        permitAdded: function(permit) {
            var view = new PermitView({model: permit});
            this.$el.append(view.render().el);
        },

        permitChanged: function(change) {
        },

        fetchingBegan: function() {
            // TODO: Display a loading indicator
        },

        fetchingComplete: function() {
            // TODO: Hide loading indicator
        }
    });
});
