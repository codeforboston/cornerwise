define(["backbone", "permit", "config"], function(B, Permit, config) {
    console.log("Creating Permits collection.");

    return B.Collection.extend({
        model: Permit,

        url: config.pzURL,

        comparator: false
    });
});
