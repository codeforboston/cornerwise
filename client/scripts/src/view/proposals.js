define(["backbone", "proposal-view", "routes", "jquery"],
       function(B, ProposalView, routes, $) {
           return B.View.extend({
               title: "Proposals",

               initialize: function() {
                   routes.getRouter().on("route:details",
                                         function(_) {

                                         });
               },

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

               proposalAdded: function(proposal) {
                   var view = new ProposalView({model: proposal}).render(),
                       collection = this.collection;

                   this.$(".proposal-list").append(view.el);
                   view.$el.on("click", function() {
                       collection.setSelection([proposal.id]);
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

                   this.$el.append("<div class='proposal-list'/>");

                   this.buildHeader();

                   this.collection.each(this.proposalAdded);
                   this._built = true;
               },

               render: function(change) {
                   if (!this._built) this.build();

                   if (!change) return;

                   this.$el
                       .removeClass("loading")
                       .find(".proposal-list").html("")
                       .on("focus", _.bind(this.onFocus, this));
                   var self = this;
                   _.each(change.models, function(p) {
                       self.proposalAdded(p);
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
               },

               onFocus: function(e) {
                   var callback = _.bind(this.onKeyDown, this);
                   $(document).on("keydown", callback);
                   this.$el.on("blur", function() {
                       $(document).off("keydown", callback);
                   });
               },

               onKeyDown: function(e) {
                   if (e.which == 38) {
                       this.collection.selectPrev();
                   } else if (e.which == 40) {
                       this.collection.selectNext();
                   } else {
                       return true;
                   }
                   return false;
               }
           });
       });
