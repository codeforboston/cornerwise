define(["backbone"], function(B) {
    console.log("Creating Permit model.");

    return B.Model.extend({
        idAttribute: "case",

        defaults: function() {
            return {
                hovered: false,
                selected: false
            };
        }
    });
});
