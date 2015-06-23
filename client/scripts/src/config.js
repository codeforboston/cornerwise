/**
 * config.js
 *
 * Application configuration options
 */

define([], function() {
    return {
        // String template or function used by Leaflet to generate the
        // image URLs for map files.
        tilesURL: "http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",

        // URL from which to fetch the JSON representing the latest
        // planning and zoning report.
        pzURL: "https://script.googleusercontent.com/macros/echo?user_content_key=6Z3f1XSpWyYssGr5idEfe4-lQ1f2d7k5hM0NqxpXTJjJB8x-haXW2QX4KlK11p7xhIY2wfQr8tCbRrpAdsXNdN6VVNpyexbgm5_BxDlH2jW0nuo2oDemN9CCS2h10ox_1xSncGQajx_ryfhECjZEnL1ZZYoa9JwTHPBTepzpS2C5x6v6YAclnWRtW82fAGBtP4tsS0dXuD1ahV_8UnQdEcE07ZagFwwH&lib=MmfdTzokCuniRZzbLnSp5WJLnyY9KPRk1"
    };
});
