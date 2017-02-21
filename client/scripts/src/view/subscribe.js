define(["jquery", "backbone", "underscore", "view/alerts", "appState", "utils"],
       function($, B, _, alerts, appState, $u) {
           return B.View.extend({
               initialize: function(options) {
                   this.mapView = options.mapView;
               },

               events: {
                   "click a.subscribe-link": "onClickSubscribe",
                   "click .cancel": "onCancel",
                   "keyup input[name=email]": "onKeyUp",
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
                                       "about. Your filter settings will " +
                                       "apply.");
                   alerts.show(instructions, "instructions", "modal",
                               "subscription-alert");

               },

               dismiss: function() {
                   this.$(".screen").hide();
                   this.$(".screen1").show();
                   $("body").removeClass("choosing-bounds");
                   alerts.remove("subscription-alert");
               },

               onKeyUp: function(e) {
                   if (e.keyCode === 27) {
                       this.dismiss();
                       e.preventDefault();
                   }
               },

               onCancel: function(e) {
                   this.dismiss();
                   e.preventDefault();
               },

               onSubmit: function(e) {
                   var form = e.target,
                       self = this,
                       query = _.clone(this.collection.query);
                   query.box = $u.boundsToBoxString(this.mapView.getBounds());
                   $.ajax("/user/subscribe",
                          {method: "POST",
                           data: {query: JSON.stringify(query),
                                  csrfmiddlewaretoken: $u.getCsrfToken(),
                                  email: form.email.value,
                                  language: navigator.language},
                           dataType: "json"})
                       .done(function(resp) {
                           form.email.value = "";
                           if (resp.has_subscriptions) {
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
                           } else {
                               var text = resp.new_user ?
                                   ("Thanks for registering! We've sent an email to " + resp.email +
                                    ". Please use the link provided to confirm your email " +
                                    "before we can send updates.") :
                                   ("Looks like you've tried to register more than once! " +
                                    "We've sent you another email. Please use the link there " +
                                    "to confirm your account.");
                               alerts.show(
                                   {title: "Please confirm your email",
                                    id: "subscription-alert",
                                    text: text,
                                    className: "info",
                                    type: "default"});
                           }
                       })
                       .fail(function(err) {
                           if (err.responseJSON)
                               self.showError(err.responseJSON.error);
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
                                                    title: "Whoops!",
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
