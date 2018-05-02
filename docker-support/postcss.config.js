module.exports = {
    plugins: [
        require("postcss-import-url"),
        require("postcss-css-variables"),
        require('cssnano')({
            preset: 'default',
        }),
    ],
};
