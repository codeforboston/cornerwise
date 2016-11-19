define(["jquery", "backbone", "underscore", "alerts", "app-state", "utils"],
       function($, B, _, alerts, appState, $u) {
           return B.View.extend({
               events: {
                   "click a.subscribe-link": "onClickSubscribe",
                   "click .cancel": "onCancel",
                   "submit form": "onSubmit"
               },

               showSubscriptionForm: function() {
                   this.$(".screen").hide();
                   this.$(".screen2")
                       .show()
                       .find("input").focus();
               },

               onClickSubscribe: function(e) {
                   this.startSubscribe();
                   e.preventDefault();
               },

               startSubscribe: function() {
                   appState.setHashKey("view", "main");
                   this.showSubscriptionForm();
                   $("body").addClass("choosing-bounds");
                   var instructions = ("Move and zoom the map to set the " +
                                       "area you want to receive updates " +
                                       "about.");
                   alerts.show(instructions, "instructions", "modal",
                               "subscription-alert");

               },

               dismiss: function() {
                   this.$(".screen").hide();
                   this.$(".screen1").show();
                   $("body").removeClass("choosing-bounds");
                   alerts.remove("subscription-alert");
               },

               onCancel: function(e) {
                   this.dismiss();
                   e.preventDefault();
               },

               onSubmit: function(e) {
                   var form = e.target,
                       self = this;
                   $.ajax("/user/subscribe",
                          {method: "POST",
                           data: {query: JSON.stringify(this.collection.query),
                                  csrfmiddlewaretoken: $u.getCookie("csrftoken"),
                                  email: form.email.value,
                                  language: navigator.language},
                           dataType: "json"})
                       .done(function(resp) {
                           if (resp.new_user) {
                               alerts.show(
                                   {title: "Please confirm your email",
                                    id: "subscription-alert",
                                    text: ("Thanks for registering! " +
                                           "We've sent an email to " +
                                           resp.email + ". Please use the link " +
                                           "provided to confirm your email " +
                                           "before we can send updates"),
                                    className: "info",
                                    type: "default"});
                           } else if (resp.has_subscriptions) {
                               alerts.show(
                                   {title: "Overwrite existing subscription?",
                                    id: "subscription-alert",
                                    text: ("Looks like you have a subscription " +
                                           "already. We've emailed a link to " +
                                           resp.email + " that will confirm the new " +
                                           "subscription. If you do nothing, your " +
                                           "old subscription will remain intact."),
                                    className: "notice",
                                    type: "default"});
                           } else if (resp.active) {
                               alerts.show(
                                   {title: "You're Subscribed!",
                                    id: "subscription-alert",
                                    text: ("You will now receive updates when the " +
                                           "proposals are updated."),
                                    className: "success"});
                           }
                       })
                       .fail(function(err) {
                           if (err.responseJSON)
                               self.showError(err.responseJSON.error);
                           else if (console)
                               console.warn(
                                   "The server returned an invalid response!",
                                   err);
                       })
                       .always(function() {
                           // Hide the subscription interface.
                           self.dismiss();
                       });

                   e.preventDefault();
               },

               showError: function(message) {
                   if (message) {
                       this._errorId = alerts.show({text: message,
                                                    className: "error"});
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
