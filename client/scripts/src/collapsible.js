define(["jquery", "underscore", "routes"], function($, _, routes) {
    return {
        init: function() {
            routes.onStateChange("expand",
                                 function(newExp, oldExp) {
                                     _.each(oldExp, function(v, k) {
                                         if (!newExp || !newExp[k]) {
                                             // Collapse:
                                             $("#" + k)
                                                 .addClass("collapsed")
                                                 .removeClass("expanded")
                                                 .trigger("collapsed");
                                         }
                                     });
                                     _.each(newExp, function(v, k) {
                                         if (!oldExp || !oldExp[k]) {
                                             $("#" + k)
                                                 .addClass("expanded")
                                                 .removeClass("collapsed")
                                                 .trigger("expanded");
                                         }
                                     });
                                 });
            $(document)
                .on("click", "a._collapse",
                    function() {
                        var id = $(this).closest("._collapsible").attr("id");
                        routes.clearHashKey("expand." + id);

                        return false;
                    })
                .on("click", "a._expand",
                    function() {
                        var id = $(this).closest("._collapsible").attr("id");
                        routes.setHashKey("expand." + id, "1");

                        return false;
                    });
        }
    };
});
