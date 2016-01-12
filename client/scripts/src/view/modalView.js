define(["backbone", "utils"], function(B, $u) {
    return new B.View.extend({
        initialize: function(options) {
            if (options.url)
                this.template = $u.templateWithUrl(options.url);
            else if (options.template)
                this.template = function(_, cb) {
                    cb(options.template());
                };

            if (!this.template)
                throw new Error("You must initialize a modal view with a URL or template.");

            this.showingClass = options.showingClass || "showing";
            this.container = options.container || ".modal-container";
            this.shouldShow = false;
        },

        el: "#modal-contents",

        getContainer: function() {
            this.$el.closest(this.container);
        },

        _update: function() {
            this.getContainer()
                .toggleClass(this.showingClass, this.shouldShow)
                .toggle(this.shouldShow);
        },

        show: function() {
            this.showShould = true;

            var self = this;
            this.template(function(html) {
                self.$el.html(html);
                // If the template was loaded asynchronously,
                // 'shouldShow' may have changed.
                self._update();
            });
        },

        hide: function() {
            this.shouldShow = false;
            this._update();
        }
    });
});
