define(["backbone", "permits", "permit-view", "jquery"], function(B, Permits, PermitView, $) {
    return B.View.extend({
        title: "Proposals",

        buildHeader: function() {
            var tr = this.$("thead tr");
            _.each([["Address","address"],
                    ["Description", "description"],
                    ["Distance", "refDistance"],
                   // ["Submitted", "submitted"]
                   ],
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

        permitAdded: function(permit) {
            var view = new PermitView({model: permit}).render(),
                collection = this.collection;

            this.$("tbody").append(view.el);
            view.$el.on("click", function() {
                collection.setSelection([permit.id]);
            });
        },

        fetchingBegan: function() {
            // TODO: Display a loading indicator
            this.$el.addClass("loading");
        },

        fetchingComplete: function() {

        },

        sortField: null,

        build: function() {
            this.listenTo(this.collection, "fetching", this.fetchingBegan)
                .listenTo(this.collection, "reset", this.fetchingComplete)
                .listenTo(this.collection, "sort", this.render);

            this.$el.append("<thead><tr></tr></thead>");
            this.$el.append("<tbody/>");

            this.buildHeader();

            this.collection.each(this.permitAdded);
            this._built = true;
        },

        render: function(change) {
            if (!this._built) this.build();

            if (!change) return;

            this.$el.removeClass("loading");
            this.$el.find("tbody").html("");
            var self = this;
            _.each(change.models, function(p) {
                self.permitAdded(p);
            });
        },

        onClickSort: function(e) {
            var th = $(e.target),
                sortField = th.data("sortField"),
                descending = th.hasClass("sort-field") &&
                    !th.hasClass("desc");;

            this.collection.sortByField(sortField, descending);
            // Remove 'sort-field' and 'desc' from all th
            this.$("th").removeClass("sort-field desc");

            this.sortField = sortField;
            th.addClass("sort-field")
                .toggleClass("desc", descending);

            return false;
        }
    });
});
