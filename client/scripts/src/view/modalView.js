define(["backbone", "jquery", "utils"], function(B, $, $u) {
    return B.View.extend({
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
            this.container = options.container || "#modal";
            this.shouldShow = false;
        },

        el: "#modal-contents",

        getContainer: function() {
            return this.$el.closest(this.container);
        },

        getContext: function() {
            return {model: this.model,
                    collection: this.collection};
        },

        _update: function() {
            this.getContainer()
                .toggleClass(this.showingClass, this.shouldShow)
                .toggle(this.shouldShow);

            $(document.body).toggleClass("modal", this.shouldShow);

            if (this.shouldShow && this.wasRendered)
                this.wasRendered();
        },

        render: function() {
            if (this.shouldShow) {
                var self = this;
                this.template(
                    this.getContext(),
                    function(html) {
                        self.$el.html(html);
                        self._update();
                    });
            }

            return this;
        },

        show: function() {
            this.shouldShow = true;
            this.render();
        },

        hide: function() {
            this.shouldShow = false;
            this._update();
        }
    });
});
