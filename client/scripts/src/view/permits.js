define(["backbone", "permits", "permit"], function(B, Permits) {
    return B.View.extend({
        initialize: function() {
            this.listenTo(this.model, "change", this.render);
        },

        render: function() {

        }
    });
});
