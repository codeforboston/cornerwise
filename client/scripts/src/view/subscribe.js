define(["jquery", "backbone", "underscore", "lib/leaflet", "view/alerts", "appState", "utils", "config"],
       function($, B, _, L, alerts, appState, $u, config) {
           return B.View.extend({
               initialize: function(options) {
                   this.options = options;
                   this.mapView = options.mapView;

                   this.listenTo(options.refLocation, "change", this.onRefChanged);

                   if (options.distanceSubscription)
                       $("#subscribe").hide();

                   $(document).on("click", "a.subscribe-link",
                                  _.bind(this.onClickSubscribe, this));
               },

               events: {
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
                   if (this.options.distanceSubscription &&
                       refLocation.changed.setMethod &&
                       refLocation.changed.setMethod !== "auto") {
                       $("#subscribe").show();
                   }
                   if (this._radiusCircle) {
                       this._radiusCircle.setLatLng(refLocation.getPoint());
                       this._radiusCircle.setRadius(refLocation.getRadiusMeters());
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

                   if (opts.distanceSubscription) {
                       var radius = opts.refLocation.getRadiusMeters(),
                           c =  L.circle(opts.refLocation.getPoint(),
                                         _.extend({ radius: radius },
                                                  opts.circleStyle))
                           .addTo(this.mapView.getMap());
                       this.mapView.getMap().fitBounds(c.getBounds());
                       this._radiusCircle = c;
                       this._currentRadius = radius;

                       if (opts.refLocation.radiusConfigurable())
                           this.showRadiusInput();
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
                   this.hideRadiusInput();
                   appState.trigger("subscribeEnd");
               },

               setRadius: function(m, unit) {
                   if (unit && unit.match(/^f(ee)?t$/i))
                       m *= 0.3048;

                   if (this._radiusCircle) {
                       this._radiusCircle.setRadius(m);
                       this._currentRadius = m;
                   }
               },

               showRadiusInput: function() {
                   // Implement if needed
                   throw new Error("showRadiusInput is not implemented.");
               },

               hideRadiusInput: function() {
                   // Implement if needed
               },

               removeCircle: function() {
                   if (this._radiusCircle) {
                       this._radiusCircle.remove();
                       this._currentRadius = this._radiusCircle = null;
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
                       query = _.clone(this.collection.query),
                       refLoc = this.options.refLocation,
                       address = "";

                   if (this._currentRadius) {
                       query.center = $u.llToString(refLoc.getLatLng());
                       query.r = ""+this._currentRadius;
                       address = refLoc.get("address");
                   } else {
                       query.box = $u.boundsToBoxString(this.mapView.getBounds());
                   }

                   $.ajax("/user/subscribe",
                          {method: "POST",
                           data: {query: JSON.stringify(query),
                                  address: address,
                                  csrfmiddlewaretoken: $u.getCsrfToken(),
                                  email: form.email.value,
                                  language: navigator.language},
                           dataType: "json"})
                       .done(function(resp) {
                           form.email.value = "";
                           var messageOptions = {};
                           if (resp.has_subscriptions) {
                               if (resp.allows_multiple) {
                                   messageOptions = config.messages.confirmNewSubscription;
                               } else {
                                   messageOptions = config.messages.overwriteExistingSubscription;
                                   messageOptions.className = "notice";
                               }
                           } else if (resp.active) {
                               messageOptions = config.messages.subscriptionCreated;
                               messageOptions.className = "success";
                           } else {
                               messageOptions = resp.new_user ?
                                   config.messages.confirmSubscription :
                                   config.messages.confirmSubscriptionRepeat;
                               messageOptions.className = "info";
                           }

                           messageOptions.id = "subscription-alert";
                           messageOptions.type = "default";
                           messageOptions.title = $u.substitute(
                               messageOptions.title, { response: resp });
                           messageOptions.text = $u.substitute(
                               messageOptions.text, { response: resp });
                           alerts.show(messageOptions);
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
