define(["backbone", "permits", "permit-view", "jquery"], function(B, Permits, PermitView, $) {
    return B.View.extend({
        initialize: function() {
            //this.listenTo(this.model, "change", this.render);
            this.listenTo(this.collection, "change", this.permitChanged)
                .listenTo(this.collection, "fetching", this.fetchingBegan)
                .listenTo(this.collection, "reset", this.fetchingComplete)
                .listenTo(this.collection, "sort", this.render);

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

        permitAdded: function(permit) {
            var view = new PermitView({model: permit});
            this.$("tbody").append(view.render().el);
        },

        permitChanged: function(change) {

        },

        fetchingBegan: function() {
            // TODO: Display a loading indicator
            this.$el.addClass("loading");
        },

        fetchingComplete: function() {

        },

        sortField: null,

        render: function(change) {
            this.$el.removeClass("loading");
            this.$el.find("tbody").html("");
            var self = this;
            _.each(change.models, function(p) {
                self.permitAdded(p);
            });
        },

        onClickSort: function(e) {
            var th = $(e.target),
                sortField = th.data("sortField");
            this.collection.sortByField(sortField);
            this.$("th").removeClass("sort-field");
            this.sortField = sortField;
            th.addClass("sort-field");
        }
    });
});
