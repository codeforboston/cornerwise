"use strict";

define(["backbone", "jquery", "underscore"], function(B, $, _) {
    return B.View.extend({
        initialize: function(options) {
            this.previewMap = options.previewMap;
            this.collections = options.collections;

            var el = this.el;
            _.each(options.previewMap, function(view) {
                view.setElement(el);
            });

            var self = this;
            _.each(options.collections, function(coll) {
                self.listenTo(coll, "change:selected",
                              self.onSelection);
            });
        },

        onSelection: function(model, selected) {
            if (this.model && this.model.id == model.id && !selected) {
                this.$el.hide();
                this.model = null;
                return;
            }

            this.model = model;

            var view = this.previewMap[model.getType()];
            view.setModel(model);
            this.$el.show();
            view.render();
        }
    });
});
