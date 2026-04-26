var size = 0;
var placement = 'point';
function categories_EEC_Center_Clean_3(feature, value, size, resolution, labelText,
                       labelFont, labelFill, bufferColor, bufferWidth,
                       placement) {
                var valueStr = (value !== null && value !== undefined) ? value.toString() : 'default';
                switch(valueStr) {case 'Elementary and Middle':
                    return [ new ol.style.Style({
        image: new ol.style.RegularShape({radius: 12.0 + size, points: 4,
            angle: Math.PI/4, displacement: [0, 0], stroke: new ol.style.Stroke({color: 'rgba(35,35,35,0.796)', lineDash: null, lineCap: 'butt', lineJoin: 'miter', width: 0.0}), fill: new ol.style.Fill({color: 'rgba(23,165,137,0.796)'})}),
        text: createTextStyle(feature, resolution, labelText, labelFont,
                              labelFill, placement, bufferColor,
                              bufferWidth)
    })];
                    break;
case 'Pre-K and Elementary':
                    return [ new ol.style.Style({
        image: new ol.style.RegularShape({radius: 12.0 + size, points: 4,
            angle: Math.PI/4, displacement: [0, 0], stroke: new ol.style.Stroke({color: 'rgba(35,35,35,0.796)', lineDash: null, lineCap: 'butt', lineJoin: 'miter', width: 0.0}), fill: new ol.style.Fill({color: 'rgba(41,128,185,0.796)'})}),
        text: createTextStyle(feature, resolution, labelText, labelFont,
                              labelFill, placement, bufferColor,
                              bufferWidth)
    })];
                    break;
case 'Pre-K only':
                    return [ new ol.style.Style({
        image: new ol.style.RegularShape({radius: 12.0 + size, points: 4,
            angle: Math.PI/4, displacement: [0, 0], stroke: new ol.style.Stroke({color: 'rgba(35,35,35,0.796)', lineDash: null, lineCap: 'butt', lineJoin: 'miter', width: 0.0}), fill: new ol.style.Fill({color: 'rgba(155,89,182,0.796)'})}),
        text: createTextStyle(feature, resolution, labelText, labelFont,
                              labelFill, placement, bufferColor,
                              bufferWidth)
    })];
                    break;
default:
                    return [ new ol.style.Style({
        image: new ol.style.Circle({radius: 4.0 + size,
            displacement: [0, 0], stroke: new ol.style.Stroke({color: 'rgba(35,35,35,0.796)', lineDash: null, lineCap: 'butt', lineJoin: 'miter', width: 0.0}), fill: new ol.style.Fill({color: 'rgba(239,53,186,0.796)'})}),
        text: createTextStyle(feature, resolution, labelText, labelFont,
                              labelFill, placement, bufferColor,
                              bufferWidth)
    })];
                    break;}};

var style_EEC_Center_Clean_3 = function(feature, resolution){
    var context = {
        feature: feature,
        variables: {}
    };
    
    var labelText = ""; 
    var value = feature.get("BAND_LABEL");
    var labelFont = "10px, sans-serif";
    var labelFill = "#000000";
    var bufferColor = "";
    var bufferWidth = 0;
    var textAlign = "left";
    var offsetX = 0;
    var offsetY = 0;
    var placement = 'point';
    if ("" !== null) {
        labelText = String("");
    }
    
    var style = categories_EEC_Center_Clean_3(feature, value, size, resolution, labelText,
                            labelFont, labelFill, bufferColor,
                            bufferWidth, placement);

    return style;
};
