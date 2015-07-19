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

            // Render the inner view
            this.subview.setElement(this.$(".collapse-body"));
            this.subview.render();

            return this;
        },

        toggleVisible: function(e) {
            console.log(e);
            this.$(".collapsible").toggleClass("shown");

            return false;
        }
    });
});
