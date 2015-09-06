define(["backbone", "underscore"], function(B, _) {
    return B.View.extend({
        template: _.template('<div class="property"><strong>Case:</strong> <%= caseNumber %></div>'
                             + '<div class="property"><strong>Address:</strong> '
                             + '<%= address %></div>'
                             + '<div class="property"><strong>Description:</strong> '
                             + '<%= description %></div>'
                             + '<% if (documents.length) { %>'
                             + '<div class="property">'
                             + '<ul class="document-list">'
                             + '<% _.each(documents, function(document) { %>'
                             + '<li><a href="<%= document.url %>" target="_blank">'
                             + '<%= document.title %></a></li>'
                             + '<% }) %>'
                             + '</ul></div>'
                             + '<% } %>'
                             + '</div>'),

        initialize: function(options) {
            this.popup = options.popup;

            this.listenTo(this.model, "change", this.render);
        },

        setContent: function(html) {
            if (this.popup)
                this.popup.setContent(html);
            else if (this.marker)
                this.marker.setPopupContent(html);
            else if (this.$el)
                this.$el.html(html);
        },

        render: function() {
            this.setContent(this.template(this.model.toJSON()));

            return this;
        },

        destroy: function() {
            this.undelegateEvents();
            this.remove();
        }
    });
});
