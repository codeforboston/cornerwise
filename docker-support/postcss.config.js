module.exports = {
    plugins: [
        require("postcss-import-url"),
        require('cssnano')({
            preset: 'default',
        }),
    ],
};
