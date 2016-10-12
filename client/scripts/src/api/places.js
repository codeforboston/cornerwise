define(["jquery"], function($) {
    var places = $.Deferred();
    if (window.google && google.maps) {
        places.resolve(google.maps.places);
    } else {
        window._onPlacesReady = function() {
            places.resolve(google.maps.places);
        };
    }

    var module = {
        /**
         * @param {HTMLElement} input
         * @param {google.maps.places.AutocompleteOptions} options
         */
        setup: function(input, options) {
            var autocomplete = $.Deferred();
            places.done(function(api) {
                autocomplete.resolve(new api.Autocomplete(input, options));
            });

            return autocomplete;
        }
    };

    return module;
});
