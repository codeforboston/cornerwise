define(["backbone", "utils"], function(B, $u) {
    return B.View.extend({
        template: '<div class="collapsible">' +
            '<div class="collapse-title">' +
            '<a href="#" class="toggle"><span></span>' +
            '</a></div>' +
            '<div class="collapse-body"></div>',

        initialize: function(options) {
            this.subview = options.view;
            this.title = options.title;
            this.shown = options.shown || false;
        },

        events: {
            "click a.toggle": "toggleVisible"
        },

        renderTitle: function(title) {
            this.$(".toggle span").text(title);
        },

        render: function() {
            this.$el.html(this.template);
            this.renderTitle(this.title);

            if (this.subview) {
                // Render the inner view
                this.subview.setElement(this.$(".collapse-body"));
                this.subview.render();
                this.toggle(this.shown);
            }

            return this;
        },

        toggle: function(show) {
            if (typeof show === "undefined")
                show = !this.shown;

            this.$(".collapsible").toggleClass("shown", show);
            this.shown = show;
        },

        toggleVisible: function(e) {
            this.toggle();

            return false;
        }
    });
});
