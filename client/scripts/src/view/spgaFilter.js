define(["backbone"], function(B) {
    return B.View.extend({
        content: '<input type="checkbox" id="pb-filter" checked> ' +
            '<label for="pb-filter"> Planning Board</label> ' +
            '<input type="checkbox" id="zba-filter" checked> ' +
            '<label for="zba-filter"> Zoning Board of Appeals</label>',

        events: {
            "change #pb-filter": "refreshSPGAFilter",
            "change #zba-filter": "refreshSPGAFilter"
        },

        refreshSPGAFilter: function() {
            var spga = [];
            if ($("#pb-filter").prop("checked"))
                spga.push("PB");
            if ($("#zba-filter").prop("checked"))
                spga.push("ZBA");
            this.collection.filterByAuthority(spga);
        },

        render: function() {
            this.$el.html(this.content);
        }
    });
});
