/**
 *  A very simple
 */
define(["leaflet"], function(L) {
    return L.Map.extend({
        initialize: function(c, opts) {
            var offset = opts && opts.offset || [200, 0];
            this.setOffset(offset);
            return L.Map.prototype.initialize.apply(this, arguments);
        },

        setOffset: function(offset) {
            this.offset = L.point(offset[0], offset[1]);
        },

        applyOffset: function(llng) {
            var projPoint = this.project(llng),
                dx = this.offset.x,
                dy = this.offset.y,
                newCenterPoint = L.point(projPoint.x + dx,
                                         projPoint.y + dy);

            return this.unproject(newCenterPoint);
        },

        setView: function(center, zoom, options) {
            center = this.applyOffset(center);

            console.log(center);

            return L.Map.prototype.setView.call(this, center, zoom, options);
        }
    });
});
