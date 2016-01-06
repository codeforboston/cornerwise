define(["backbone", "routes"], function(B, routes) {
    return B.View.extend({
        render: function() {
            this.showing = this.model && this.showing;

            if (!this.showing) {
                this.$el.hide();
                return this;
            }

            this.$el.show();

            var html = this.template(this.model.toJSON());
            this.$el.html(html);

            return this;
        },

        show: function(model) {
            this.model = model;

            return this.setShowing(true);
        },

        hide: function() {
            this.setShowing(false);
        }
    });
});
