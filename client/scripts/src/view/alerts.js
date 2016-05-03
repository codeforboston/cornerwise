define(["backbone", "jquery", "underscore"],
       function(B, $, _) {
           var alertElement = $("#alert"),
               alertCount = 0,
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
               remove: function(id) {
                   if (lastMessage && lastMessage.id === id) {
                       var m = lastMessage;
                       advance();
                       return m;
                   } else {
                       var idx = _.findIndex(messages,
                                             function(m) { return m.id === id; });
                       if (idx !== -1) {
                           return messages.splice(idx, 1)[0];
                       }

                       return null;
                   }
               },

               show: function(message, className) {
                   var id = alertCount++;
                   messages.push({text: message,
                                  id: id,
                                  className: className || ""});
                   start();

                   return id;
               }
           };
       });
