"use strict";
define(["jquery", "underscore", "utils", "config"], function($, _, $u, config) {
    var definitions = {
        "CBD": "Central Business District zone",
        "CCD": "Central Commercial District zone (??)",
        "RA": "Residential zone",
        "RB": "Residential zone",
        "LEED": "Leadership in Energy and Environmental Design is a certification program that recognizes environmentally responsible building practices.",
        "waiver": "",
        "Site Plan Review": "",
        "Special Permit": "A special permit is required for certain allowed uses that are subject to review by the zoning authority.",
        "variance": "A variance is required for uses that are not permitted by the local zoning law.",
        "FAR": "Floor-area ratio measures the ratio of the structure's floor area to the area of the plot. High-density buildings like apartment complexes have a high FAR.",
        "SZO": "Somerville Zoning Ordinance",
        "Stretch Code": "The Board of Building Regulations and Standards Stretch Code requires new construction to meet a 20% higher energy efficiency standard."
    };

    window.$u = $u;
    var reStr = "\\b(" + $u.wordsRegexString(_.keys(definitions)) + ")\\b";

    function makeRegionRegex(region) {
        var codeConfig = config.codeReference[region];

        if (codeConfig) {
            return new RegExp(reStr + "|" + codeConfig.pattern + "", "gi");
        } else {
            return new RegExp(reStr, "gi");
        }
    }

    function makeCodeLinkFn(region) {
        var codeConfig = config.codeReference[region];

        if (!codeConfig) return null;

        return function(section) {
            return codeConfig.url.replace("{section}", section);
        };
    }

    return {
        definitions: definitions,

        reStr: reStr,

        /**
         * Given an HTML string, replace occurrences of glossary terms
         * with anchor tags that will display a definition on hover.
         *
         * @param {String} html
         * @param {boolean|Function} escape When a function is
         * specified, use that as the escape function. If a truthy
         * non-function, escape HTML tags. Otherwise, do not escape.
         * @param {String} region_name
         *
         */
        addMarkup: function(html, escape, region_name) {
            var re = makeRegionRegex(region_name),
                codeLink = makeCodeLinkFn(region_name),
                pieces = [], lastPosition = 0, replacement,
                seen = {},
                escapeFn = escape ? (_.isFunction(escape) ? escape : _.escape) : _.identity,
                m;

            while ((m = re.exec(html))) {
                if (m[1]) {
                    if (seen[m[0]]) continue;
                    seen[m[0]] = 1;
                    replacement = "<a class='glossary'>" + m[0] + "</a>";
                } else if (m[2]) {
                    replacement = "<a href='" + codeLink(m[2]) + "' target='_blank'>" + m[0] + "</a>";
                }

                pieces.push(escapeFn(html.substring(lastPosition, m.index)),
                            replacement);
                lastPosition = m.index + m[0].length;
            }

            pieces.push(escapeFn(html.substring(lastPosition, html.length)));

            return pieces.join("");
        },

        onMouseEnter: function(e) {
            var a = $(e.target),
                term = a.text().trim(),
                definition = definitions[term];

            if (!definition) {
                this.onMouseLeave(e);
                return;
            }

            if (!this.definitionContainer)
                this.definitionContainer = $("<div class='definition'/>");

            var html = _.escape(definition);

            this.definitionContainer.html(html).appendTo(a);
        },

        onMouseLeave: function(e) {
            if (this.definitionContainer) {
                if (this.definitionContainer.parent().is(e.currentTarget)) {
                    this.definitionContainer.remove();
                }
            }
        },

        init: function() {
            $(document)
                .on("mouseenter", "a.glossary", _.bind(this.onMouseEnter, this))
                .on("mouseleave", "a.glossary", _.bind(this.onMouseLeave, this));

            $u.registerHelper("gloss", this.addMarkup);
        }
    };
});
