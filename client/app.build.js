({
    appDir: "./scripts",
    baseUrl: "src",
    dir: "./dist",
    fileExclusionRegExp: /^(site|require)\.js$/,
    mainConfigFile: "./scripts/main.js",
    modules: [
        {
            name: "../main"
        }
    ],
    removeCombined: true
})
