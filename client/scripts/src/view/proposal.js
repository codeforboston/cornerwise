/*
 * View representing a proposal in the proposals list.
 */
define(["backbone", "underscore", "utils", "refLocation", "config"],
       function(B, _, $u, refLocation, config) {
           var proposalHelpers = {
               refLocationButton: function() {
                   var setMethod = refLocation.get("setMethod");

                   return [
                       "<a class='ref-loc' href='#'>",
                       setMethod == "geolocate" ?
                           "Current Location" :
                           setMethod == "address" ?
                           _.escape(refLocation.get("address")) :
                           config.refPointName,
                       "</a>"
                   ].join("");
               }
           };

           var template = $u.templateWithUrl("/static/template/proposal.html",
                                             {variable: "proposal",
                                              helpers: proposalHelpers});

           return B.View.extend({
               initialize: function() {
                   this.listenTo(this.model, "change:refDistance", this.render);
               },

               tagName: "div",

               className: "proposal-info info-item",

               render: function() {
                   var $el = this.$el;

                   template(this.model, function(html) { $el.html(html); });

                   return this;
               }
           });
       });
