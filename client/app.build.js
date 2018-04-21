({
    baseUrl: "scripts/src",
    // fileExclusionRegExp: /^(site)\.js$/,
    mainConfigFile: "./scripts/src/main.js",
    name: "main",
    removeCombined: true,
    paths: {
        requireLib: "lib/require"
    },
    include: ["requireLib"],
    out: "app.js"
})
