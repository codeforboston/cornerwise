define(["backbone", "permit"], function(B, Permit) {
    console.log("Creating Permits collection.");

    return B.Collection.extend({
        model: Permit,

        sync: function() {
            // Do nothing
        }
    });
});
