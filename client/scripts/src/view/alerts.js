define(["backbone", "jquery", "underscore", "utils", "config"],
       function(B, $, _, $u, config) {
           var alertElement = $("#alert"),
               alertCount = 0,
               modalMessage,
               lastMessage;

           /**
            * @enum {number}
            */
           var AlertType = {
               DEFAULT: 0,
               // Must be dismissed explicitly by id.
               MODAL: 1
           };

           /**
            * @param {string} [id] If supplied, dismisses the displayed message
            * only if its id matches this string.
            *
            * @return {jQuery} The alert container element
            */
           function dismissMessage(id) {
               if (lastMessage && (!id || lastMessage.id == id)) {
                   alertElement
                       .removeClass("displayed")
                       .removeClass(lastMessage.className);

                   if (lastMessage.onDismiss) {
                       lastMessage.onDismiss(lastMessage);
                   }

                   lastMessage = null;
               }

               if (modalMessage) {
                   if (modalMessage.id === id) {
                       modalMessage = null;
                   } else {
                       showMessage(modalMessage);
                   }
               }

               return alertElement;
           }

           function _makeButtons(config) {
               return $.map(config, function(button, name) {
                   return [
                       "<button name='", name, "' class='button'>",
                       button.label || $u.fromUnder(name),
                       "</button>"
                   ].join("");
               }).join("\n");
           }

           function _doShow(message) {
               alertElement
                   .addClass(message.className)
                   .addClass("displayed")
                   .toggleClass("modal", message.type == AlertType.MODAL)
                   .find(".content")
                        .text(message.text)
                        .toggleClass("displayed", !!message.text)
                        .end()
                   .find(".title")
                        .text(message.title)
                        .toggleClass("displayed", !!message.title)
                        .end()
                   .find(".buttons")
                        .html(_makeButtons(message.buttons))
                        .toggleClass("displayed", !!message.buttons);
               lastMessage = message;
               if (message.type == AlertType.MODAL) {
                   modalMessage = message;
               } else if (modalMessage && modalMessage.id === message.id) {
                   modalMessage = null;
               }
           }

           function showMessage(message) {
               if (lastMessage) {
                   dismissMessage().delay(0.2, "alerts").queue("alerts", function(next) {
                       _doShow(message);
                       next();
                   })
                       .dequeue("alerts");
               } else {
                   _doShow(message);
               }
           }

           alertElement.click(function(e) {
               var button = $(e.target).closest(".buttons button");
               if (button.length) {
                   var buttonName = button.attr("name"),
                       buttonConfig = lastMessage.buttons && lastMessage.buttons[buttonName];

                   if (buttonConfig) {
                       e.preventDefault();
                       if (!buttonConfig.handler(e, lastMessage, dismissMessage))
                           return;
                   }
               }

               if (lastMessage.type !== AlertType.MODAL) {
                   dismissMessage();
               } else if (lastMessage.onClick) {
                   lastMessage.onClick(lastMessage);
               }
               e.preventDefault();
           });

           var alerts = {
               AlertType: AlertType,

               remove: dismissMessage,
               dismissMessage: dismissMessage,

               /**
                * @param {string} message
                * @param {string} className
                * @param {AlertType} [type=AlertType.DEFAULT]
                * @param {string} [id]
                *
                * @return id
                */
               show: function(message, className, type, id) {
                   var msg =
                       _.isObject(message) ? message : {text: message,
                                                        id: id,
                                                        className: className || "",
                                                        type: type || AlertType.DEFAULT};

                   if (id) msg.id = id;
                   else if (!msg.id) msg.id = alertCount++;

                   if (_.isString(msg.type)) msg.type = AlertType[msg.type.toUpperCase()];

                   showMessage(msg);
                   return id;
               },

               showNamed: function(namedMessage, id, context) {
                   var message = config.messages[namedMessage];

                   if (message) {
                       message = _.extend({id: id}, message);
                       if (context)
                           $u.substitute(message, context, ["text", "title"]);
                       alerts.show(_.extend({id: id}, message));
                   }
               },

               /**
                * @param {} messages
                *
                * @returns {null}
                */
               showResponses: function(messages) {
                   var m = messages[0];
                   if (/\bjson\b/.exec(m.tags)) {
                       var json = JSON.parse(m.message);
                       json.className = m.tags;
                       this.show(json);
                   } else {
                       this.show(m.message, m.tags);
                   }
               }
           };

           return alerts;
       });
