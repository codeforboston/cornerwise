define(["jquery", "backbone", "underscore", "lib/leaflet", "view/alerts", "appState", "utils"],
       function($, B, _, L, alerts, appState, $u) {
           return B.View.extend({
               initialize: function(options) {
                   this.options = options;
                   this.mapView = options.mapView;

                   this.listenTo(options.refLocation, "change", this.onRefChanged);
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

               onRefChanged: function(refLocation) {
                   if (this._radiusCircle) {
                       this._radiusCircle.setLatLng(refLocation.getPoint());
                   }
               },

               onClickSubscribe: function(e) {
                   this.startSubscribe();
                   e.preventDefault();
               },

               startSubscribe: function() {
                   var opts = this.options;

                   appState.trigger("subscribeStart");
                   appState.setHashKey("view", "main");
                   this.showSubscriptionForm();
                   this.removeCircle();

                   if (opts.maxRadius) {
                       if (!opts.minRadius ||
                           opts.minRadius === opts.maxRadius) {
                           var radius = opts.minRadius * 0.3048,
                               c =  L.circle(opts.refLocation.getPoint(),
                                             _.extend({ radius: radius },
                                                      opts.circleStyle))
                               .addTo(this.mapView.getMap());
                           this._radiusCircle = c;
                       }
                       $("body").addClass("subscribe-mode choosing-radius");
                   } else {
                       $("body").addClass("subscribe-mode choosing-bounds");
                   }
                   var instructions = opts.instructions;
                   alerts.show(instructions, "instructions", "modal",
                               "subscription-alert");

               },

               dismiss: function() {
                   this.$(".screen").hide();
                   this.$(".screen1").show();
                   $("body").removeClass("choosing-bounds subscribe-mode choosing-radius");
                   alerts.remove("subscription-alert");
                   this.removeCircle();
                   appState.trigger("subscribeEnd");
               },

               removeCircle: function() {
                   if (this._radiusCircle) {
                       this._radiusCircle.remove();
                       this._radiusCircle = null;
                   }
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
