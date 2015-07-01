/**
 * View responsible for exposing the permit filters to the user.
 */
define(["backbone"], function(B) {
    return B.View.extend({
        el: function() {
            return document.getElementById("permit-filters");
        },

        events: {
            "change #desc-filter": "refreshDescriptionFilter",
            "keyup #desc-filter": "descFilterChanged",
            "change #pb-filter": "refreshSPGAFilter",
            "change #zba-filter": "refreshSPGAFilter"
        },

        refreshDescriptionFilter: function() {
            var s = ($("#desc-filter").val() || "").trim();
            this.collection.filterByDescriptionString(s);
        },


        descFilterChanged: function(e) {
            var self = this;
            clearTimeout(this._descTimeout);
            this._descTimeout = setTimeout(function() {
                self.refreshDescriptionFilter();
            }, 200);
        },

        refreshSPGAFilter: function() {
            var spga = [];
            if ($("#pb-filter").prop("checked"))
                spga.push("PB");
            if ($("#zba-filter").prop("checked"))
                spga.push("ZBA");
            this.collection.filterByAuthority(spga);
        }
    });
});
