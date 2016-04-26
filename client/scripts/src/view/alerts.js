define(["backbone", "jquery", "underscore"],
       function(B, $, _) {
           var alertElement = $("#alert"),
               messages = [],
               lastMessage;

           function showMessage(message) {
               if (_.isString(message)) {
                   message = {text: message,
                              className: ""};
               }

               alertElement.html(message.text)
                   .addClass("displayed " + message.className);
           }

           function advance() {
               if (lastMessage && lastMessage.className)
                   alertElement.removeClass(lastMessage.className);

               if (messages.length) {
                   lastMessage = messages.shift();
                   showMessage(lastMessage);
               } else {
                   alertElement.removeClass("displayed");
                   lastMessage = null;
               }
           }

           function start() {
               if (!lastMessage) advance();
           }

           alertElement.click(function() {
               advance();
           });

           return {
               show: function(message, className) {
                   messages.push({text: message,
                                  className: className || ""});
                   start();

                   return alertElement;
               }
           };
       });
