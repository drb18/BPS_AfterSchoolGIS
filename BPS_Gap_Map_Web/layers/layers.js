var wms_layers = [];


        var lyr_OSMStandard_0 = new ol.layer.Tile({
            'title': 'OSM Standard',
            'opacity': 1.000000,
            
            
            source: new ol.source.XYZ({
            attributions: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, © <a href="https://carto.com/attributions">CARTO</a>',
                url: 'https://a.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png'
            })
        });
var format_BPS_Isochrones_1 = new ol.format.GeoJSON();
var features_BPS_Isochrones_1 = format_BPS_Isochrones_1.readFeatures(json_BPS_Isochrones_1, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_BPS_Isochrones_1 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_BPS_Isochrones_1.addFeatures(features_BPS_Isochrones_1);
var lyr_BPS_Isochrones_1 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_BPS_Isochrones_1, 
                style: style_BPS_Isochrones_1,
                popuplayertitle: 'BPS_Isochrones',
                interactive: false,
    title: 'BPS_Isochrones<br />\
    <img src="styles/legend/BPS_Isochrones_1_0.png" /> 10 min<br />' });
var format_EEC_FCC_Clean_2 = new ol.format.GeoJSON();
var features_EEC_FCC_Clean_2 = format_EEC_FCC_Clean_2.readFeatures(json_EEC_FCC_Clean_2, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_EEC_FCC_Clean_2 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_EEC_FCC_Clean_2.addFeatures(features_EEC_FCC_Clean_2);
var lyr_EEC_FCC_Clean_2 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_EEC_FCC_Clean_2, 
                style: style_EEC_FCC_Clean_2,
                popuplayertitle: 'EEC_FCC_Clean',
                interactive: true,
    title: 'EEC_FCC_Clean<br />\
    <img src="styles/legend/EEC_FCC_Clean_2_0.png" /> Funded and Subsidy<br />\
    <img src="styles/legend/EEC_FCC_Clean_2_1.png" /> Licensed and Subsidy<br />\
    <img src="styles/legend/EEC_FCC_Clean_2_2.png" /> Licensed only<br />\
    <img src="styles/legend/EEC_FCC_Clean_2_3.png" /> Not current<br />' });
var format_EEC_Center_Clean_3 = new ol.format.GeoJSON();
var features_EEC_Center_Clean_3 = format_EEC_Center_Clean_3.readFeatures(json_EEC_Center_Clean_3, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_EEC_Center_Clean_3 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_EEC_Center_Clean_3.addFeatures(features_EEC_Center_Clean_3);
var lyr_EEC_Center_Clean_3 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_EEC_Center_Clean_3, 
                style: style_EEC_Center_Clean_3,
                popuplayertitle: 'EEC_Center_Clean',
                interactive: true,
    title: 'EEC_Center_Clean<br />\
    <img src="styles/legend/EEC_Center_Clean_3_0.png" /> Elementary and Middle<br />\
    <img src="styles/legend/EEC_Center_Clean_3_1.png" /> Pre-K and Elementary<br />\
    <img src="styles/legend/EEC_Center_Clean_3_2.png" /> Pre-K only<br />\
    <img src="styles/legend/EEC_Center_Clean_3_3.png" /> <br />' });
var format_BPS_Schools_Ranked_4 = new ol.format.GeoJSON();
var features_BPS_Schools_Ranked_4 = format_BPS_Schools_Ranked_4.readFeatures(json_BPS_Schools_Ranked_4, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_BPS_Schools_Ranked_4 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_BPS_Schools_Ranked_4.addFeatures(features_BPS_Schools_Ranked_4);
var lyr_BPS_Schools_Ranked_4 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_BPS_Schools_Ranked_4, 
                style: style_BPS_Schools_Ranked_4,
                popuplayertitle: 'BPS_Schools_Ranked',
                interactive: true,
    title: 'BPS_Schools_Ranked<br />\
    <img src="styles/legend/BPS_Schools_Ranked_4_0.png" /> High Concern<br />\
    <img src="styles/legend/BPS_Schools_Ranked_4_1.png" /> High Concern — No Partners<br />\
    <img src="styles/legend/BPS_Schools_Ranked_4_2.png" /> Lower Concern<br />\
    <img src="styles/legend/BPS_Schools_Ranked_4_3.png" /> Lower Concern — No Partners<br />\
    <img src="styles/legend/BPS_Schools_Ranked_4_4.png" /> Moderate Concern<br />\
    <img src="styles/legend/BPS_Schools_Ranked_4_5.png" /> Moderate Concern — No Partners<br />\
    <img src="styles/legend/BPS_Schools_Ranked_4_6.png" /> Moderate-High Concern<br />\
    <img src="styles/legend/BPS_Schools_Ranked_4_7.png" /> Moderate-High Concern — No Partners<br />\
    <img src="styles/legend/BPS_Schools_Ranked_4_8.png" /> Not applicable<br />' });
var group_EECPrograms = new ol.layer.Group({
                                layers: [lyr_EEC_FCC_Clean_2,lyr_EEC_Center_Clean_3,],
                                fold: 'open',
                                title: 'EEC Programs'});

lyr_OSMStandard_0.setVisible(true);lyr_BPS_Isochrones_1.setVisible(false);lyr_EEC_FCC_Clean_2.setVisible(true);lyr_EEC_Center_Clean_3.setVisible(true);lyr_BPS_Schools_Ranked_4.setVisible(true);
var layersList = [lyr_OSMStandard_0,lyr_BPS_Isochrones_1,group_EECPrograms,lyr_BPS_Schools_Ranked_4];
lyr_BPS_Isochrones_1.set('fieldAliases', {'fid': 'fid', 'SCHID': 'SCHID', 'CENTER_LON': 'CENTER_LON', 'CENTER_LAT': 'CENTER_LAT', 'AA_MINS': 'AA_MINS', 'AA_MODE': 'AA_MODE', 'TOTAL_POP': 'TOTAL_POP', });
lyr_EEC_FCC_Clean_2.set('fieldAliases', {'PROGRAM_NAME': 'Program Name', 'FULL_ADDRESS': 'Address', 'PROGRAM_PHONE': 'Phone', 'LICENSED_CAPACITY': 'Licensed Capacity', 'LICENSED_PROVIDER_STATUS': 'License Status', 'VOUCHER_CONTRACT': 'Accepts Subsidy Vouchers', 'QUALITY_LABEL': 'Quality Status'});
lyr_EEC_Center_Clean_3.set('fieldAliases', {'PROGRAM_NAME': 'Program Name', 'PROGRAM_UMBRELLA': 'Organization', 'FULL_ADDRESS': 'Address', 'PROGRAM_PHONE': 'Phone', 'LICENSED_CAPACITY': 'Licensed Capacity', 'LICENSED_PROVIDER_STATUS': 'License Status', 'VOUCHER_CONTRACT': 'Accepts Subsidy Vouchers', 'C3_ATTESTATION': 'C3 Quality Certified', 'BAND_LABEL': 'Grade Bands Served', 'QUALITY_LICENSED': 'Currently Licensed'});
lyr_BPS_Schools_Ranked_4.set('fieldAliases', {'NAME': 'School Name', 'ADDRESS': 'Address', 'ZIPCODE': 'Zip Code', 'GRADES': 'Grades Served', 'TYPE_DESC': 'School Type', 'TOTAL_CNT': 'Total Enrollment', 'LI_PCT': 'Low Income %', 'LI_CNT': 'Low Income Students', 'BPS_OI_SCORE': 'BPS Opportunity Index Score', 'OST_TOTAL_CNT': 'OST Partners (Total)', 'OST_PREK_CNT': 'OST Partners (Pre-K)', 'OST_ELEM_CNT': 'OST Partners (Elementary)', 'OST_MIDDLE_CNT': 'OST Partners (Middle)', 'GAP_RANK_PREK': 'Pre-K Gap Rank', 'GAP_ELIGIBLE_PREK': 'Pre-K Eligible Schools', 'GAP_TIER_PREK': 'Pre-K Gap Tier', 'GAP_RANK_ELEM': 'Elementary Gap Rank', 'GAP_ELIGIBLE_ELEM': 'Elementary Eligible Schools', 'GAP_TIER_ELEM': 'Elementary Gap Tier', 'GAP_RANK_MIDDLE': 'Middle Gap Rank', 'GAP_ELIGIBLE_MIDDLE': 'Middle Eligible Schools', 'GAP_TIER_MIDDLE': 'Middle Gap Tier', 'PRIMARY_GAP_BAND': 'Primary Gap Band', 'PRIMARY_GAP_TIER': 'Primary Gap Tier', 'PRIMARY_GAP_LABEL': 'Gap Summary', 'ZERO_OST_ANY': 'No OST Partners on Record'});
lyr_BPS_Isochrones_1.set('fieldImages', {'fid': 'TextEdit', 'SCHID': 'TextEdit', 'CENTER_LON': 'TextEdit', 'CENTER_LAT': 'TextEdit', 'AA_MINS': 'Range', 'AA_MODE': 'TextEdit', 'TOTAL_POP': 'TextEdit', });
lyr_EEC_FCC_Clean_2.set('fieldImages', {'PROVIDER_NUMBER': 'TextEdit', 'PROGRAM_NAME': 'TextEdit', 'PROGRAM_UMBRELLA': 'TextEdit', 'PROGRAM_STREET_ADDRESS1': 'TextEdit', 'PROGRAM_STREET_ADDRESS2': 'TextEdit', 'PROGRAM_CITY': 'TextEdit', 'PROGRAM_ZIPCODE': 'TextEdit', 'PROGRAM_PHONE': 'TextEdit', 'LICENSING_REGION': 'TextEdit', 'SUBSIDY_REGION': 'TextEdit', 'PROGRAM_TYPE': 'TextEdit', 'LICENSED_FUNDED': 'TextEdit', 'LICENSED_PROVIDER_STATUS': 'TextEdit', 'FUNDED_PROVIDER_STATUS': 'TextEdit', 'REGULATORY_STATUS': 'TextEdit', 'FIRST_ISSUED_DATE': 'DateTime', 'LICENSED_CAPACITY': 'Range', 'INFANT_BIRTH15MO': 'TextEdit', 'INFANTTODDLER_BIRTH33MO': 'TextEdit', 'TODDLER_15MO33MO': 'TextEdit', 'TODDLERPRESCHOOL_15MOK': 'TextEdit', 'PRESCHOOL_33MOK': 'TextEdit', 'PRESCHOOLSA_33MO8YR': 'TextEdit', 'KINDERGARTEN': 'TextEdit', 'KINDERGARTEN_SCHOOLAGE': 'TextEdit', 'SCHOOLAGE_5YR14YR': 'TextEdit', 'MULTIAGEGROUP_BIRTH14YR': 'TextEdit', 'VOUCHER_CONTRACT': 'CheckBox', 'C3_ATTESTATION': 'TextEdit', 'COI_CAT': 'TextEdit', 'SNAPSHOT_DATE': 'DateTime', 'FULL_ADDRESS': 'TextEdit', 'Latitude': 'TextEdit', 'Longitude': 'TextEdit', 'QUALITY_LICENSED': 'CheckBox', 'QUALITY_VOUCHER': 'CheckBox', 'QUALITY_C3': 'CheckBox', 'QUALITY_LABEL': 'TextEdit', });
lyr_EEC_Center_Clean_3.set('fieldImages', {'PROVIDER_NUMBER': 'TextEdit', 'PROGRAM_NAME': 'TextEdit', 'PROGRAM_UMBRELLA': 'TextEdit', 'PROGRAM_STREET_ADDRESS1': 'TextEdit', 'PROGRAM_STREET_ADDRESS2': 'TextEdit', 'PROGRAM_CITY': 'TextEdit', 'PROGRAM_ZIPCODE': 'TextEdit', 'PROGRAM_PHONE': 'TextEdit', 'LICENSING_REGION': 'TextEdit', 'SUBSIDY_REGION': 'TextEdit', 'PROGRAM_TYPE': 'TextEdit', 'LICENSED_FUNDED': 'TextEdit', 'LICENSED_PROVIDER_STATUS': 'TextEdit', 'FUNDED_PROVIDER_STATUS': 'TextEdit', 'REGULATORY_STATUS': 'TextEdit', 'FIRST_ISSUED_DATE': 'DateTime', 'LICENSED_CAPACITY': 'Range', 'INFANT_BIRTH15MO': 'TextEdit', 'INFANTTODDLER_BIRTH33MO': 'TextEdit', 'TODDLER_15MO33MO': 'TextEdit', 'TODDLERPRESCHOOL_15MOK': 'TextEdit', 'PRESCHOOL_33MOK': 'TextEdit', 'PRESCHOOLSA_33MO8YR': 'TextEdit', 'KINDERGARTEN': 'TextEdit', 'KINDERGARTEN_SCHOOLAGE': 'TextEdit', 'SCHOOLAGE_5YR14YR': 'TextEdit', 'MULTIAGEGROUP_BIRTH14YR': 'TextEdit', 'VOUCHER_CONTRACT': 'CheckBox', 'C3_ATTESTATION': 'TextEdit', 'COI_CAT': 'TextEdit', 'SNAPSHOT_DATE': 'DateTime', 'FULL_ADDRESS': 'TextEdit', 'Latitude': 'TextEdit', 'Longitude': 'TextEdit', 'SERVES_PREK': 'CheckBox', 'SERVES_ELEM': 'CheckBox', 'SERVES_MIDDLE': 'CheckBox', 'QUALITY_LICENSED': 'CheckBox', 'QUALITY_VOUCHER': 'CheckBox', 'QUALITY_C3': 'CheckBox', 'BAND_LABEL': 'TextEdit', 'CAP_CAT': 'TextEdit', });
lyr_BPS_Schools_Ranked_4.set('fieldImages', {'fid': 'TextEdit', 'SCHID': 'TextEdit', 'NAME': 'TextEdit', 'ADDRESS': 'TextEdit', 'TOWN': 'TextEdit', 'ZIPCODE': 'TextEdit', 'GRADES': 'TextEdit', 'TYPE_DESC': 'TextEdit', 'TOTAL_CNT': 'TextEdit', 'ENR_PREK': 'TextEdit', 'ENR_ELEM': 'TextEdit', 'ENR_MIDDLE': 'TextEdit', 'EL_PCT': 'TextEdit', 'LI_PCT': 'TextEdit', 'LI_CNT': 'TextEdit', 'SWD_PCT': 'TextEdit', 'HL_PCT': 'TextEdit', 'BAA_PCT': 'TextEdit', 'RC_CODE': 'TextEdit', 'BPS_OI_SCORE': 'TextEdit', 'OI_NAME_MATCHED': 'TextEdit', 'SCHOOL_PREK': 'CheckBox', 'SCHOOL_ELEM': 'CheckBox', 'SCHOOL_MIDDLE': 'CheckBox', 'EEC_ADJ_CAP_PREK': 'TextEdit', 'EEC_RAW_CNT_PREK': 'TextEdit', 'EEC_ADJ_CAP_ELEM': 'TextEdit', 'EEC_RAW_CNT_ELEM': 'TextEdit', 'EEC_ADJ_CAP_MIDDLE': 'TextEdit', 'EEC_RAW_CNT_MIDDLE': 'TextEdit', 'OST_TOTAL_CNT': 'TextEdit', 'OST_PREK_CNT': 'TextEdit', 'OST_ELEM_CNT': 'TextEdit', 'OST_MIDDLE_CNT': 'TextEdit', 'NEED_SCORE': 'TextEdit', 'RANK_NEED_PREK': 'TextEdit', 'RANK_OST_PREK': 'TextEdit', 'RANK_EEC_PREK': 'TextEdit', 'COMPOSITE_PREK': 'TextEdit', 'GAP_SEVERITY_PREK': 'TextEdit', 'GAP_RANK_PREK': 'TextEdit', 'GAP_ELIGIBLE_PREK': 'TextEdit', 'GAP_TIER_PREK': 'TextEdit', 'RANK_NEED_ELEM': 'TextEdit', 'RANK_OST_ELEM': 'TextEdit', 'RANK_EEC_ELEM': 'TextEdit', 'COMPOSITE_ELEM': 'TextEdit', 'GAP_SEVERITY_ELEM': 'TextEdit', 'GAP_RANK_ELEM': 'TextEdit', 'GAP_ELIGIBLE_ELEM': 'TextEdit', 'GAP_TIER_ELEM': 'TextEdit', 'RANK_NEED_MIDDLE': 'TextEdit', 'RANK_OST_MIDDLE': 'TextEdit', 'RANK_EEC_MIDDLE': 'TextEdit', 'COMPOSITE_MIDDLE': 'TextEdit', 'GAP_SEVERITY_MIDDLE': 'TextEdit', 'GAP_RANK_MIDDLE': 'TextEdit', 'GAP_ELIGIBLE_MIDDLE': 'TextEdit', 'GAP_TIER_MIDDLE': 'TextEdit', 'PRIMARY_GAP_BAND': 'TextEdit', 'PRIMARY_GAP_TIER': 'TextEdit', 'PRIMARY_GAP_LABEL': 'TextEdit', 'ZERO_EEC_PREK': 'CheckBox', 'ZERO_EEC_ELEM': 'CheckBox', 'ZERO_EEC_MIDDLE': 'CheckBox', 'ZERO_OST_ANY': 'CheckBox', 'SIZE_CAT': 'TextEdit', 'SYMBOL_TYPE': 'TextEdit', });
lyr_BPS_Isochrones_1.set('fieldLabels', {'fid': 'no label', 'SCHID': 'no label', 'CENTER_LON': 'no label', 'CENTER_LAT': 'no label', 'AA_MINS': 'no label', 'AA_MODE': 'no label', 'TOTAL_POP': 'no label', });
lyr_EEC_FCC_Clean_2.set('fieldLabels', {'PROVIDER_NUMBER': 'no label', 'PROGRAM_NAME': 'no label', 'PROGRAM_UMBRELLA': 'no label', 'PROGRAM_STREET_ADDRESS1': 'no label', 'PROGRAM_STREET_ADDRESS2': 'no label', 'PROGRAM_CITY': 'no label', 'PROGRAM_ZIPCODE': 'no label', 'PROGRAM_PHONE': 'no label', 'LICENSING_REGION': 'no label', 'SUBSIDY_REGION': 'no label', 'PROGRAM_TYPE': 'no label', 'LICENSED_FUNDED': 'no label', 'LICENSED_PROVIDER_STATUS': 'no label', 'FUNDED_PROVIDER_STATUS': 'no label', 'REGULATORY_STATUS': 'no label', 'FIRST_ISSUED_DATE': 'no label', 'LICENSED_CAPACITY': 'no label', 'INFANT_BIRTH15MO': 'no label', 'INFANTTODDLER_BIRTH33MO': 'no label', 'TODDLER_15MO33MO': 'no label', 'TODDLERPRESCHOOL_15MOK': 'no label', 'PRESCHOOL_33MOK': 'no label', 'PRESCHOOLSA_33MO8YR': 'no label', 'KINDERGARTEN': 'no label', 'KINDERGARTEN_SCHOOLAGE': 'no label', 'SCHOOLAGE_5YR14YR': 'no label', 'MULTIAGEGROUP_BIRTH14YR': 'no label', 'VOUCHER_CONTRACT': 'no label', 'C3_ATTESTATION': 'no label', 'COI_CAT': 'no label', 'SNAPSHOT_DATE': 'no label', 'FULL_ADDRESS': 'no label', 'Latitude': 'no label', 'Longitude': 'no label', 'QUALITY_LICENSED': 'no label', 'QUALITY_VOUCHER': 'no label', 'QUALITY_C3': 'no label', 'QUALITY_LABEL': 'no label', });
lyr_EEC_Center_Clean_3.set('fieldLabels', {'PROVIDER_NUMBER': 'no label', 'PROGRAM_NAME': 'no label', 'PROGRAM_UMBRELLA': 'no label', 'PROGRAM_STREET_ADDRESS1': 'no label', 'PROGRAM_STREET_ADDRESS2': 'no label', 'PROGRAM_CITY': 'no label', 'PROGRAM_ZIPCODE': 'no label', 'PROGRAM_PHONE': 'no label', 'LICENSING_REGION': 'no label', 'SUBSIDY_REGION': 'no label', 'PROGRAM_TYPE': 'no label', 'LICENSED_FUNDED': 'no label', 'LICENSED_PROVIDER_STATUS': 'no label', 'FUNDED_PROVIDER_STATUS': 'no label', 'REGULATORY_STATUS': 'no label', 'FIRST_ISSUED_DATE': 'no label', 'LICENSED_CAPACITY': 'no label', 'INFANT_BIRTH15MO': 'no label', 'INFANTTODDLER_BIRTH33MO': 'no label', 'TODDLER_15MO33MO': 'no label', 'TODDLERPRESCHOOL_15MOK': 'no label', 'PRESCHOOL_33MOK': 'no label', 'PRESCHOOLSA_33MO8YR': 'no label', 'KINDERGARTEN': 'no label', 'KINDERGARTEN_SCHOOLAGE': 'no label', 'SCHOOLAGE_5YR14YR': 'no label', 'MULTIAGEGROUP_BIRTH14YR': 'no label', 'VOUCHER_CONTRACT': 'no label', 'C3_ATTESTATION': 'no label', 'COI_CAT': 'no label', 'SNAPSHOT_DATE': 'no label', 'FULL_ADDRESS': 'no label', 'Latitude': 'no label', 'Longitude': 'no label', 'SERVES_PREK': 'no label', 'SERVES_ELEM': 'no label', 'SERVES_MIDDLE': 'no label', 'QUALITY_LICENSED': 'no label', 'QUALITY_VOUCHER': 'no label', 'QUALITY_C3': 'no label', 'BAND_LABEL': 'no label', 'CAP_CAT': 'no label', });
lyr_BPS_Schools_Ranked_4.set('fieldLabels', {'fid': 'no label', 'SCHID': 'no label', 'NAME': 'inline label - visible with data', 'ADDRESS': 'inline label - visible with data', 'TOWN': 'no label', 'ZIPCODE': 'inline label - visible with data', 'GRADES': 'inline label - visible with data', 'TYPE_DESC': 'inline label - visible with data', 'TOTAL_CNT': 'inline label - visible with data', 'ENR_PREK': 'no label', 'ENR_ELEM': 'no label', 'ENR_MIDDLE': 'no label', 'EL_PCT': 'no label', 'LI_PCT': 'inline label - visible with data', 'LI_CNT': 'inline label - visible with data', 'SWD_PCT': 'no label', 'HL_PCT': 'no label', 'BAA_PCT': 'no label', 'RC_CODE': 'no label', 'BPS_OI_SCORE': 'inline label - visible with data', 'OI_NAME_MATCHED': 'no label', 'SCHOOL_PREK': 'no label', 'SCHOOL_ELEM': 'no label', 'SCHOOL_MIDDLE': 'no label', 'EEC_ADJ_CAP_PREK': 'no label', 'EEC_RAW_CNT_PREK': 'no label', 'EEC_ADJ_CAP_ELEM': 'no label', 'EEC_RAW_CNT_ELEM': 'no label', 'EEC_ADJ_CAP_MIDDLE': 'no label', 'EEC_RAW_CNT_MIDDLE': 'no label', 'OST_TOTAL_CNT': 'inline label - visible with data', 'OST_PREK_CNT': 'inline label - visible with data', 'OST_ELEM_CNT': 'inline label - visible with data', 'OST_MIDDLE_CNT': 'inline label - visible with data', 'NEED_SCORE': 'no label', 'RANK_NEED_PREK': 'no label', 'RANK_OST_PREK': 'no label', 'RANK_EEC_PREK': 'no label', 'COMPOSITE_PREK': 'no label', 'GAP_SEVERITY_PREK': 'no label', 'GAP_RANK_PREK': 'inline label - visible with data', 'GAP_ELIGIBLE_PREK': 'inline label - visible with data', 'GAP_TIER_PREK': 'inline label - visible with data', 'RANK_NEED_ELEM': 'no label', 'RANK_OST_ELEM': 'no label', 'RANK_EEC_ELEM': 'no label', 'COMPOSITE_ELEM': 'no label', 'GAP_SEVERITY_ELEM': 'no label', 'GAP_RANK_ELEM': 'inline label - visible with data', 'GAP_ELIGIBLE_ELEM': 'inline label - visible with data', 'GAP_TIER_ELEM': 'inline label - visible with data', 'RANK_NEED_MIDDLE': 'no label', 'RANK_OST_MIDDLE': 'no label', 'RANK_EEC_MIDDLE': 'no label', 'COMPOSITE_MIDDLE': 'no label', 'GAP_SEVERITY_MIDDLE': 'no label', 'GAP_RANK_MIDDLE': 'inline label - visible with data', 'GAP_ELIGIBLE_MIDDLE': 'inline label - visible with data', 'GAP_TIER_MIDDLE': 'inline label - visible with data', 'PRIMARY_GAP_BAND': 'inline label - visible with data', 'PRIMARY_GAP_TIER': 'inline label - visible with data', 'PRIMARY_GAP_LABEL': 'inline label - visible with data', 'ZERO_EEC_PREK': 'no label', 'ZERO_EEC_ELEM': 'no label', 'ZERO_EEC_MIDDLE': 'no label', 'ZERO_OST_ANY': 'inline label - visible with data', 'SIZE_CAT': 'no label', 'SYMBOL_TYPE': 'no label', });
lyr_BPS_Schools_Ranked_4.on('precompose', function(evt) {
    evt.context.globalCompositeOperation = 'normal';
});
// BPS_GAP_MAP POPUP FUNCTIONS — DO NOT EDIT MANUALLY

function formatSchoolPopup(feature) {
    var p = feature.getProperties();

    var noPartnerWarning = '';
    if (p['ZERO_OST_ANY'] === true  ||
        p['ZERO_OST_ANY'] === 'true' ||
        p['ZERO_OST_ANY'] === 1) {
        noPartnerWarning =
            '<div style="background:#922B21;color:white;' +
            'padding:5px 8px;border-radius:3px;margin:6px 0;' +
            'font-weight:bold;">&#9888; No vetted OST partners ' +
            'on record</div>';
    }

    var bandRows = '';
    if (p['SCHOOL_PREK'] === true ||
        p['SCHOOL_PREK'] === 'true' || p['SCHOOL_PREK'] === 1) {
        bandRows +=
            '<tr style="border-bottom:1px solid #eee;">' +
            '<td style="padding:3px 8px 3px 0;' +
            'white-space:nowrap;"><b>Pre-K:</b></td>' +
            '<td style="padding:3px 0;">Ranked ' +
            p['GAP_RANK_PREK'] + ' of ' +
            p['GAP_ELIGIBLE_PREK'] +
            ' Pre-K schools<br><i>' +
            p['GAP_TIER_PREK'] + '</i></td></tr>';
    }
    if (p['SCHOOL_ELEM'] === true ||
        p['SCHOOL_ELEM'] === 'true' || p['SCHOOL_ELEM'] === 1) {
        bandRows +=
            '<tr style="border-bottom:1px solid #eee;">' +
            '<td style="padding:3px 8px 3px 0;' +
            'white-space:nowrap;"><b>Elementary:</b></td>' +
            '<td style="padding:3px 0;">Ranked ' +
            p['GAP_RANK_ELEM'] + ' of ' +
            p['GAP_ELIGIBLE_ELEM'] +
            ' Elementary schools<br><i>' +
            p['GAP_TIER_ELEM'] + '</i></td></tr>';
    }
    if (p['SCHOOL_MIDDLE'] === true ||
        p['SCHOOL_MIDDLE'] === 'true' || p['SCHOOL_MIDDLE'] === 1) {
        bandRows +=
            '<tr style="border-bottom:1px solid #eee;">' +
            '<td style="padding:3px 8px 3px 0;' +
            'white-space:nowrap;"><b>Middle:</b></td>' +
            '<td style="padding:3px 0;">Ranked ' +
            p['GAP_RANK_MIDDLE'] + ' of ' +
            p['GAP_ELIGIBLE_MIDDLE'] +
            ' Middle schools<br><i>' +
            p['GAP_TIER_MIDDLE'] + '</i></td></tr>';
    }

    return '<div style="font-family:Arial,sans-serif;' +
        'font-size:13px;color:#222;line-height:1.5;">' +
        '<b style="font-size:15px;">' + p['NAME'] + '</b><br>' +
        '<span style="color:#555;">' + p['ADDRESS'] +
        ', Boston MA ' + p['ZIPCODE'] + '</span><br>' +
        '<hr style="margin:6px 0;border:none;' +
        'border-top:1px solid #ddd;">' +
        '<b>School Type:</b> ' + p['TYPE_DESC'] + '<br>' +
        '<b>Grades:</b> ' + p['GRADES'] + '<br>' +
        '<b>Total Enrollment:</b> ' + p['TOTAL_CNT'] +
        ' students<br>' +
        '<b>Low Income:</b> ' + p['LI_PCT'] + '% (' +
        p['LI_CNT'] + ' students)<br>' +
        '<hr style="margin:6px 0;border:none;' +
        'border-top:1px solid #ddd;">' +
        noPartnerWarning +
        '<b>OST Partners on record:</b> ' +
        p['OST_TOTAL_CNT'] + '<br>' +
        '<hr style="margin:6px 0;border:none;' +
        'border-top:1px solid #ddd;">' +
        '<b>Gap Analysis by Band:</b><br>' +
        '<table style="width:100%;border-collapse:collapse;' +
        'margin-top:4px;">' + bandRows + '</table>' +
        '<hr style="margin:6px 0;border:none;' +
        'border-top:1px solid #ddd;">' +
        '<b>BPS Opportunity Index:</b> ' +
        p['BPS_OI_SCORE'] + '<br>' +
        '<div style="margin-top:8px;padding:6px;' +
        'background:#f9f9f9;border-radius:3px;' +
        'font-size:11px;color:#666;">' +
        'Rank 1 = most concerning within band.<br>' +
        'Based on: enrollment need &times; low income %, ' +
        'OST partner count, and licensed EEC capacity ' +
        'within 10-min walk.</div>' +
        '</div>';
}

function formatEECCenterPopup(feature) {
    var p = feature.getProperties();
    return '<div style="font-family:Arial,sans-serif;' +
        'font-size:13px;color:#222;line-height:1.5;">' +
        '<b style="font-size:14px;">' + p['PROGRAM_NAME'] +
        '</b><br>' +
        '<span style="color:#555;font-style:italic;">' +
        p['PROGRAM_UMBRELLA'] + '</span><br>' +
        '<hr style="margin:6px 0;border:none;' +
        'border-top:1px solid #ddd;">' +
        '<b>Address:</b> ' + p['FULL_ADDRESS'] + '<br>' +
        '<b>Phone:</b> ' + p['PROGRAM_PHONE'] + '<br>' +
        '<hr style="margin:6px 0;border:none;' +
        'border-top:1px solid #ddd;">' +
        '<b>Grade Bands Served:</b> ' + p['BAND_LABEL'] + '<br>' +
        '<b>Licensed Capacity:</b> ' + p['LICENSED_CAPACITY'] +
        ' slots<br>' +
        '<div style="font-size:11px;color:#888;margin-top:2px;">' +
        'Licensed capacity is a legal maximum — actual ' +
        'available slots may differ.</div>' +
        '<hr style="margin:6px 0;border:none;' +
        'border-top:1px solid #ddd;">' +
        '<b>License Status:</b> ' +
        p['LICENSED_PROVIDER_STATUS'] + '<br>' +
        '<b>Accepts Subsidy Vouchers:</b> ' +
        p['VOUCHER_CONTRACT'] + '<br>' +
        '<b>C3 Quality Certified:</b> ' +
        p['C3_ATTESTATION'] + '<br>' +
        '</div>';
}

function formatFCCPopup(feature) {
    var p = feature.getProperties();
    return '<div style="font-family:Arial,sans-serif;' +
        'font-size:13px;color:#222;line-height:1.5;">' +
        '<b style="font-size:14px;">' + p['PROGRAM_NAME'] +
        '</b><br>' +
        '<span style="color:#555;font-style:italic;">' +
        'Family Child Care</span><br>' +
        '<hr style="margin:6px 0;border:none;' +
        'border-top:1px solid #ddd;">' +
        '<b>Address:</b> ' + p['FULL_ADDRESS'] + '<br>' +
        '<b>Phone:</b> ' + p['PROGRAM_PHONE'] + '<br>' +
        '<hr style="margin:6px 0;border:none;' +
        'border-top:1px solid #ddd;">' +
        '<b>Quality Status:</b> ' + p['QUALITY_LABEL'] + '<br>' +
        '<b>Licensed Capacity:</b> ' + p['LICENSED_CAPACITY'] +
        ' slots<br>' +
        '<b>License Status:</b> ' +
        p['LICENSED_PROVIDER_STATUS'] + '<br>' +
        '<b>Accepts Subsidy Vouchers:</b> ' +
        p['VOUCHER_CONTRACT'] + '<br>' +
        '<div style="margin-top:8px;padding:6px;' +
        'background:#f9f9f9;border-radius:3px;' +
        'font-size:11px;color:#666;">' +
        'Age range: birth–13 assumed per MA licensing default. ' +
        'Age breakdown not reported for Family Child Care ' +
        'providers.</div>' +
        '</div>';
}
