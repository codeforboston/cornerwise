define(["backbone", "permits", "permit-view", "jquery"], function(B, Permits, PermitView, $) {
    return B.View.extend({
        initialize: function() {
            //this.listenTo(this.model, "change", this.render);
            this.listenTo(this.collection, "change", this.permitChanged)
                .listenTo(this.collection, "fetching", this.fetchingBegan)
                .listenTo(this.collection, "reset", this.fetchingComplete)
                .listenTo(this.collection, "sort", this.sorted);

            this.$el.append("<thead><tr></tr></thead>");
            this.$el.append("<tbody/>");

            this.buildHeader();
        },

        buildHeader: function() {
            var tr = this.$("thead tr");
            _.each([["Description", "description"],
                    ["Case Number", "caseNumber"]],
                   function(p) {
                       $("<th>").text(p[0])
                           .data("sortField", p[1])
                           .addClass("sort")
                           .appendTo(tr);
                   });
        },

        events: {
            "click th.sort": "onClickSort"
        },

        el: function() {
            return document.getElementById("permit-list");
        },

        tagName: "table",

        render: function() {
            return this;
        },

        permitAdded: function(permit) {
            var view = new PermitView({model: permit});
            this.$("tbody").append(view.render().el);
        },

        permitChanged: function(change) {
        },

        fetchingBegan: function() {
            // TODO: Display a loading indicator
        },

        fetchingComplete: function() {
            // TODO: Hide loading indicator
        },

        sorted: function(change) {
            this.$el.find("tbody").html("");
            var self = this;
            _.each(change.models, function(p) {
                self.permitAdded(p);
            });
        },

        onClickSort: function(e) {
            this.collection.sortByField($(e.target).data("sortField"));
        }
    });
});
