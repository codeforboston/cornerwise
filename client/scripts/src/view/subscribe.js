define(["jquery", "backbone", "underscore", "alerts", "utils"],
       function($, B, _, alerts, $u) {
           return B.View.extend({
               events: {
                   "click a.subscribe-link": "onClickSubscribe",
                   "click .cancel": "reset",
                   "submit form": "onSubmit"
               },

               showSubscriptionForm: function() {
                   this.$(".screen").hide();
                   this.$(".screen2")
                       .show()
                       .find("input").focus();
               },

               onClickSubscribe: function() {
                   this.showSubscriptionForm();
                   $("body").addClass("choosing-bounds");
                   alerts.show("Move and zoom the map to set the " +
                               "area you want to receive updates " +
                               "about.", "instructional");
               },

               reset: function(e) {
                   this.$(".screen").hide();
                   this.$(".screen1").show();
                   $("body").removeClass("choosing-bounds");
                   e.preventDefault();
               },

               onSubmit: function(e) {
                   var form = e.target,
                       self = this;
                   $.ajax("/user/subscribe",
                          {method: "POST",
                           data: {query: JSON.stringify(this.collection.query),
                                  csrfmiddlewaretoken: $u.getCookie("csrftoken"),
                                  email: form.email.value},
                           dataType: "json"})
                       .done(function(resp) {
                           if (resp.new_user) {
                               alerts.show(
                                   ["Thanks for registering!<br>",
                                    "We're sending an email to <b>",
                                    _.escape(resp.email), "</b> with ",
                                    "instructions on how to complete the ",
                                    "process"].join(""),
                                   "info");
                           } else if (resp.active) {
                               alerts.show(
                                   "You will now receive notifications for " +
                                       "proposals matching the current filters.",
                                   "info");
                           } else {
                               alerts.show(
                                   ["You will receive notifications for proposals",
                                    "matching the current filters once you",
                                    "confirm your email address."].join(""),
                                   "info");
                                    //    <br/>",
                                    // "<form action='/user/resend' method='post'>",
                                    // "<input type='hidden' name='email' ",
                                    // "value='", 
                           }
                       })
                       .fail(function(err) {
                           self.showError(err.error);
                       });

                   e.preventDefault();
               },

               showError: function(message) {
                   if (message) {
                       this._errorId = alerts.show(_.escape(message), "error");
                   } else {
                       this.hideError();
                   }
               },

               hideError: function() {
                   if (this._errorId !== undefined) {
                       alerts.remove(this._errorId);
                       delete this._errorId;
                   }
               }
           });
       });
