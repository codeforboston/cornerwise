define(["backbone", "jquery", "underscore"],
       function(B, $, _) {
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
               if (lastMessage && !id || lastMessage.id == id) {
                   alertElement
                       .removeClass("displayed")
                       .removeClass(lastMessage.className);
                   lastMessage = null;
               }

               if (modalMessage && modalMessage.id === id) {
                   modalMessage = null;
               } else {
                   showMessage(modalMessage);
               }

               return alertElement;
           }

           function _doShow(message) {
               alertElement
                   .addClass(message.className)
                   .addClass("displayed")
                   .toggleClass("modal", message.type == AlertType.MODAL)
                   .find(".content").text(message.text).end()
                   .find(".title").text(message.title).toggle(!!message.title);
               lastMessage = message;
               if (message.type == AlertType.MODAL) {
                   modalMessage = message;
               }
           }

           function showMessage(message) {
               if (lastMessage) {
                   dismissMessage().delay(0.2).queue(function() {
                       _doShow(message);
                   });
               } else {
                   _doShow(message);
               }
           }

           alertElement.click(function() {
               if (lastMessage.type !== AlertType.MODAL) {
                   dismissMessage();
               }
           });

           return {
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

                   if (!msg.id) msg.id = alertCount++;
                   if (_.isString(msg.type)) msg.type = AlertType[type.toUpperCase()];

                   showMessage(msg);
                   return id;
               }
           };
       });
