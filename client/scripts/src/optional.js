define({
    load: function(moduleName, req, onload, config) {
        req([moduleName],
            // If the module loads successfully, proceed as usual:
            onload,
            // If it fails to load, define the unloaded module as null
            // and re-require.
            function(err) {
                var module = err.requireModules[0];
                requirejs.undef(module);

                // Define the unloaded module as null:
                var defaultModule = config.moduleDefaults &&
                    config.moduleDefaults[moduleName];
                define(module, [], function() { return defaultModule; });

                req([module], onload);
            });
    }
});
