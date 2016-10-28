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
                   var instructions = ("Move and zoom the map to set the " +
                                       "area you want to receive updates " +
                                       "about.");
                   alerts.show(instructions, "instructions", "modal", "subscribe-instructions");
               },

               reset: function(e) {
                   this.$(".screen").hide();
                   this.$(".screen1").show();
                   $("body").removeClass("choosing-bounds");
                   alerts.remove("subscribe-instructions");
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
                                   {title: "Please confirm your email",
                                    text: ["Thanks for registering!",
                                           "We've sent an email to ",
                                           resp.email, ". Please use the link ",
                                           "provided to confirm your email ",
                                           "before we can send updates"].join(""),
                                    className: "info",
                                    type: alerts.AlertType.MODAL});
                           } else if (resp.has_subscriptions) {
                               alerts.show(
                                   {title: "Overwrite existing subscription?",
                                    text: ("Looks like you have a subscription " +
                                           "already. We've emailed a link to " +
                                           resp.email + " that will confirm the new " +
                                           "subscription. If you do nothing, your " +
                                           "old subscription will remain intact."),
                                    className: "notice"});
                           } else if (resp.active) {
                               alerts.show(
                                   {title: "You're Subscribed!",
                                    text: ("You will now receive updates when the " +
                                           "proposals are updated."),
                                    className: "success"});
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
