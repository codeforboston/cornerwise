define({
    load: function(moduleName, req, onload, _config) {
        req([moduleName],
            // If the module loads successfully, proceed as usual:
            onload,
            // If it fails to load, define the unloaded module as null
            // and re-require.
            function(err) {
                var module = err.requireModules[0];
                requirejs.undef(module);

                // Define the unloaded module as null:
                define(module, [], function() { return null; });

                req([module], onload);
            });
    }
});
