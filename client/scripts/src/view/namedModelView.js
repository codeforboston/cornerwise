define(["named-view", "routes"], function(NamedView, routes) {
    return NamedView.extend({
        initialize: function(options) {
            NamedView.prototype.initialize.call(this, options);

            if (options.viewName) {
                var self = this;
                routes.onStateChange("view", function(view) {
                    self.setShowing(view === options.viewName);
                });
            }

            return this;
        },

        setShowing: function(isShowing) {
            this.showing = isShowing;
            return this.render();
        }
    });
});
