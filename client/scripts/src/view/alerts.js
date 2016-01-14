define(["backbone", "jquery", "underscore"],
       function(B, $, _) {
           var alertElement = $("#alert");

           return {
               show: function(message, className) {
                   if (_.isString(message)) {
                       message = {text: message,
                                  className: className || ''};
                   }

                   alertElement
                       .text(message.text)
                       .addClass("displayed " + message.className)
                       .delay(message.delay || 2000)
                       .queue(function(next) {
                           $(this)
                               .removeClass("displayed " + message.className);

                           next();
                       });
               }
           };
       });
