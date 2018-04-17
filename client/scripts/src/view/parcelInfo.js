define(["jquery", "backbone", "utils"],
       function($, B, $u) {
           return B.View.extend({
               template: $u.templateWithUrl("/static/template/parcelInfo.html",
                                            {variable: "parcel"}),

               initialize: function(options) {
                   B.View.prototype.initialize.call(this, options);

                   this.listenTo(this.collection, "selectionLoaded", this.parcelsLoaded);
                   this.listenTo(this.collection, "selection", this.parcelsSelected);
               },

               hide: function() {
                   this.$el.removeClass("show");
               },

               show: function(parcel) {
                   var $el = this.$el;
                   this.template(parcel, function(html) {
                       $el.html(html).addClass("show");
                   });
               },

               parcelsSelected: function() {
                   var self = this;
                   clearTimeout(this._fadeTimeout);
                   this._fadeTimeout = setTimeout(function() {
                       self.hide();
                   }, 500);
               },

               parcelsLoaded: function(parcels, ids) {
                   clearTimeout(this._fadeTimeout);

                   var parcel = (ids.length === 0) ? null : parcels.get(ids[0]);

                   if (!parcel) {
                       this.hide();
                   } else {
                       this.show(parcel);
                   }
               }
           });
       });
