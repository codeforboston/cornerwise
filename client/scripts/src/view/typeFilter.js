define(["backbone", "underscore", "config", "utils"], function(B, _, config, $u) {
    return B.View.extend({
        // The template used to construct each checkbox/label pair in
        // the list.
        template: $u.template(
            '<div>'
                + '<input type="checkbox" name="<%= type %>" id="<%= type %>-input"'
                + ' <%= (on) ? "checked" : "" %>/> '
                + '<label for="<%= type %>-input"> <%= name %></label>'
                + '</div>'
        ),

        initialize: function() {
            this.listenTo(this.collection, "update", this.refreshAndRender);
            this.refresh();
        },

        // Map of "type name" => { on: (bool), name: (str) }
        types: {},

        events: {
            "change input": "updateFilter"
        },

        getFilterValue: function() {
            return _.pluck(
                _.filter(this.types, function(t) { return t.on; }),
                "type");
        },

        updateFilter: function(e) {
            var t = e.target.getAttribute("name");
            this.types[t].on = e.target.checked;
            this.collection.filterByTypes(this.getFilterValue());
        },

        refreshAndRender: function() {
            this.refresh();
            this.render();
        },

        refresh: function() {
            var old = this.types,
                names = config.permitTypes;
            this.types = this.collection.reduce(function(m, p) {
                var t = p.get("permit");
                m[t] = old[t] || { on: true,
                                   name: names[t] || t,
                                   type: t };
                return m;
            }, {});
        },

        render: function() {
            this.$el.html(_.map(this.types,
                                function(type) {
                                    return this.template(type);
                                }, this).join(""));

            return this;
        }
    });
});
