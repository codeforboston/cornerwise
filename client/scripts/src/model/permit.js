define(["backbone"], function(B) {
    console.log("Creating Permit model.");

    return B.Model.extend({
        idAttribute: "case",

        defaults: function() {
            return {
                hovered: false,
                selected: false,

                // excluded will change to true when the permit fails
                // the currently applied filter(s).
                excluded: false
            };
        },

        parse: function(attrs) {
            attrs.submitted = new Date(attrs.submitted);
            return attrs;
        }
    });
});
