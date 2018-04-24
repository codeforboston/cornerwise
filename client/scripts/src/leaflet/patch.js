define(["lib/leaflet"], function(L) {

    var setPosition = L.Tooltip.prototype._setPosition;
    L.Tooltip.prototype._setPosition = function (pos) {
        var map = this._map,
            centerPoint = map.latLngToContainerPoint(map.getCenter()),
            tooltipPoint = map.layerPointToContainerPoint(pos),
            direction = this.options.direction,
            offset = this.options.offset,
            adjustedOffset = offset;

        if (offset) {
            if (direction === 'bottom') {
                adjustedOffset = L.point(offset.x, -offset.y);
            } if (direction === 'left' || direction === 'auto' && tooltipPoint.x >= centerPoint.x) {
                adjustedOffset = L.point(-offset.x, offset.y);
            }
        }

        this.options.offset = adjustedOffset;
        setPosition.call(this, pos);
        this.options.offset = offset;
	  };
});
