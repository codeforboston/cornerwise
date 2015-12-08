"use strict";

define(["jquery", "underscore", "utils"], function($, _, $u) {
    var definitions = {
        "CBD": "Central Business District zone",
        "CCD": "Central Commercial District zone (??)",
        "RA": "Residential zone",
        "RB": "Residential zone",
        // "Special Permit": "Explanation and link",
        "FAR": "Floor-area ratio measures the ratio of the structure's floor area to the area of the plot on which it stands.",
        "SZO": "Somerville Zoning Ordinance"
    };

    var reStr = _.map(definitions,
                      function(_, key) {
                          return $u.escapeRegex(''+key);
                      }).join("|");

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
         */
        addMarkup: function(html, escape) {
            var re = new RegExp(reStr, "g"), m,
                pieces = [], lastPosition = 0,
                escapeFn =
                    escape ? (_.isFunction(escape) ? escape : _.escape) : _.identity;

            while ((m = re.exec(html))) {
                pieces.push(escapeFn(html.substring(lastPosition, m.index)),
                            "<a class='glossary'>", m[0], "</a>");
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

            var html = ["<span class='term'>", _.escape(term), "</span> ",
                        _.escape(definition)].join("");

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
