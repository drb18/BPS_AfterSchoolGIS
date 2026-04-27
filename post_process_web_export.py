# post_process_web_export.py
# Run once after every fresh qgis2web export.
# Modifies BPS_Gap_Map_Web/layers/layers.js and index.html.
# Safe to run multiple times on the same export — cleans
# previous runs before applying changes.

import re
from pathlib import Path

WEB_FOLDER = Path('BPS_Gap_Map_Web')
LAYERS_JS  = WEB_FOLDER / 'layers' / 'layers.js'
INDEX_HTML = WEB_FOLDER / 'index.html'

# ==========================================
# FIELD ALIASES
# Human-readable labels for popup display
# ==========================================
SCHOOL_ALIASES = {
    'NAME':               'School Name',
    'ADDRESS':            'Address',
    'ZIPCODE':            'Zip Code',
    'GRADES':             'Grades Served',
    'TYPE_DESC':          'School Type',
    'TOTAL_CNT':          'Total Enrollment',
    'LI_PCT':             'Low Income %',
    'LI_CNT':             'Low Income Students',
    'BPS_OI_SCORE':       'BPS Opportunity Index Score',
    'OST_TOTAL_CNT':      'OST Partners (Total)',
    'OST_PREK_CNT':       'OST Partners (Pre-K)',
    'OST_ELEM_CNT':       'OST Partners (Elementary)',
    'OST_MIDDLE_CNT':     'OST Partners (Middle)',
    'GAP_RANK_PREK':      'Pre-K Gap Rank',
    'GAP_ELIGIBLE_PREK':  'Pre-K Eligible Schools',
    'GAP_TIER_PREK':      'Pre-K Gap Tier',
    'GAP_RANK_ELEM':      'Elementary Gap Rank',
    'GAP_ELIGIBLE_ELEM':  'Elementary Eligible Schools',
    'GAP_TIER_ELEM':      'Elementary Gap Tier',
    'GAP_RANK_MIDDLE':    'Middle Gap Rank',
    'GAP_ELIGIBLE_MIDDLE':'Middle Eligible Schools',
    'GAP_TIER_MIDDLE':    'Middle Gap Tier',
    'PRIMARY_GAP_BAND':   'Primary Gap Band',
    'PRIMARY_GAP_TIER':   'Primary Gap Tier',
    'PRIMARY_GAP_LABEL':  'Gap Summary',
    'ZERO_OST_ANY':       'No OST Partners on Record',
}

EEC_CENTER_ALIASES = {
    'PROGRAM_NAME':             'Program Name',
    'PROGRAM_UMBRELLA':         'Organization',
    'FULL_ADDRESS':             'Address',
    'PROGRAM_PHONE':            'Phone',
    'LICENSED_CAPACITY':        'Licensed Capacity',
    'LICENSED_PROVIDER_STATUS': 'License Status',
    'VOUCHER_CONTRACT':         'Accepts Subsidy Vouchers',
    'C3_ATTESTATION':           'C3 Quality Certified',
    'BAND_LABEL':               'Grade Bands Served',
    'QUALITY_LICENSED':         'Currently Licensed',
}

EEC_FCC_ALIASES = {
    'PROGRAM_NAME':             'Program Name',
    'FULL_ADDRESS':             'Address',
    'PROGRAM_PHONE':            'Phone',
    'LICENSED_CAPACITY':        'Licensed Capacity',
    'LICENSED_PROVIDER_STATUS': 'License Status',
    'VOUCHER_CONTRACT':         'Accepts Subsidy Vouchers',
    'QUALITY_LABEL':            'Quality Status',
}

# ==========================================
# READ FILES
# ==========================================
print(f"Reading {LAYERS_JS}...")
content = LAYERS_JS.read_text(encoding='utf-8')
print(f"  Original size: {len(content)} chars")

print(f"\nReading {INDEX_HTML}...")
html = INDEX_HTML.read_text(encoding='utf-8')
print(f"  Original size: {len(html)} chars")
print(f"  Total lines:   {len(html.splitlines())}")


# ==========================================
# LAYERS.JS — STEP 2B: FIX OSM TILE URL
# OSM blocks tile requests from file:// URLs
# CartoDB Voyager is visually similar and
# works without HTTP referer restrictions
# ==========================================
OSM_URL   = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
CARTO_URL = ('https://a.basemaps.cartocdn.com/'
             'rastertiles/voyager/{z}/{x}/{y}.png')
OSM_ATTR  = ('&nbsp;&middot; <a href="https://www.openstreetmap'
             '.org/copyright">\xa9 OpenStreetMap contributors, '
             'CC-BY-SA</a>')
CARTO_ATTR = ('\xa9 <a href="https://www.openstreetmap.org/'
              'copyright">OpenStreetMap</a> contributors, '
              '\xa9 <a href="https://carto.com/attributions">'
              'CARTO</a>')

if OSM_URL in content:
    content = content.replace(OSM_URL, CARTO_URL)
    content = content.replace(OSM_ATTR, CARTO_ATTR)
    print("  Replaced OSM tiles with CartoDB Voyager")
else:
    print("  Note: OSM tile URL not found — may already be replaced")


# ==========================================
# LAYERS.JS — STEP 1: CLEAN PREVIOUS RUNS
# Remove any previously appended sections
# so script is safe to run multiple times
# ==========================================
POPUP_MARKER = '// BPS_GAP_MAP POPUP FUNCTIONS — DO NOT EDIT MANUALLY'
if POPUP_MARKER in content:
    content = content[:content.index(POPUP_MARKER)]
    print("\n  Removed previous popup functions from layers.js")
else:
    print("\n  No previous popup functions found — clean baseline")

# ==========================================
# LAYERS.JS — STEP 2: UPDATE FIELD ALIASES
# Replace technical field names with
# readable labels in popup display
# ==========================================
def build_alias_js(layer_var, aliases):
    parts = ', '.join(f"'{k}': '{v}'" for k, v in aliases.items())
    return f"{layer_var}.set('fieldAliases', {{{parts}}});"

replacements = [
    ('lyr_BPS_Schools_Ranked_4', SCHOOL_ALIASES),
    ('lyr_EEC_Center_Clean_3',   EEC_CENTER_ALIASES),
    ('lyr_EEC_FCC_Clean_2',      EEC_FCC_ALIASES),
]

for layer_var, aliases in replacements:
    pattern = (
        rf"{re.escape(layer_var)}\.set\('fieldAliases',"
        r"\s*\{[^}]*\}\s*\);"
    )
    replacement = build_alias_js(layer_var, aliases)
    new_content, count = re.subn(
        pattern, replacement, content, flags=re.DOTALL
    )
    if count > 0:
        content = new_content
        print(f"  Updated fieldAliases for {layer_var}")
    else:
        print(f"  WARNING: fieldAliases not found for {layer_var}")

# ==========================================
# LAYERS.JS — STEP 3: APPEND POPUP FUNCTIONS
# Appended at end of layers.js
# Marker prevents duplication on re-runs
# ==========================================
POPUP_FUNCTIONS = f"""
{POPUP_MARKER}

function formatSchoolPopup(feature) {{
    var p = feature.getProperties();

    var noPartnerWarning = '';
    if (p['ZERO_OST_ANY'] === true  ||
        p['ZERO_OST_ANY'] === 'true' ||
        p['ZERO_OST_ANY'] === 1) {{
        noPartnerWarning =
            '<div style="background:#922B21;color:white;' +
            'padding:5px 8px;border-radius:3px;margin:6px 0;' +
            'font-weight:bold;">&#9888; No vetted OST partners ' +
            'on record</div>';
    }}

    var bandRows = '';
    if (p['SCHOOL_PREK'] === true ||
        p['SCHOOL_PREK'] === 'true' || p['SCHOOL_PREK'] === 1) {{
        bandRows +=
            '<tr style="border-bottom:1px solid #eee;">' +
            '<td style="padding:3px 8px 3px 0;' +
            'white-space:nowrap;"><b>Pre-K:</b></td>' +
            '<td style="padding:3px 0;">Ranked ' +
            p['GAP_RANK_PREK'] + ' of ' +
            p['GAP_ELIGIBLE_PREK'] +
            ' Pre-K schools<br><i>' +
            p['GAP_TIER_PREK'] + '</i></td></tr>';
    }}
    if (p['SCHOOL_ELEM'] === true ||
        p['SCHOOL_ELEM'] === 'true' || p['SCHOOL_ELEM'] === 1) {{
        bandRows +=
            '<tr style="border-bottom:1px solid #eee;">' +
            '<td style="padding:3px 8px 3px 0;' +
            'white-space:nowrap;"><b>Elementary:</b></td>' +
            '<td style="padding:3px 0;">Ranked ' +
            p['GAP_RANK_ELEM'] + ' of ' +
            p['GAP_ELIGIBLE_ELEM'] +
            ' Elementary schools<br><i>' +
            p['GAP_TIER_ELEM'] + '</i></td></tr>';
    }}
    if (p['SCHOOL_MIDDLE'] === true ||
        p['SCHOOL_MIDDLE'] === 'true' || p['SCHOOL_MIDDLE'] === 1) {{
        bandRows +=
            '<tr style="border-bottom:1px solid #eee;">' +
            '<td style="padding:3px 8px 3px 0;' +
            'white-space:nowrap;"><b>Middle:</b></td>' +
            '<td style="padding:3px 0;">Ranked ' +
            p['GAP_RANK_MIDDLE'] + ' of ' +
            p['GAP_ELIGIBLE_MIDDLE'] +
            ' Middle schools<br><i>' +
            p['GAP_TIER_MIDDLE'] + '</i></td></tr>';
    }}

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
}}

function formatEECCenterPopup(feature) {{
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
}}

function formatFCCPopup(feature) {{
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
}}
"""

content += POPUP_FUNCTIONS

LAYERS_JS.write_text(content, encoding='utf-8')
print(f"\n  Saved layers.js — final size: {len(content)} chars")

# ==========================================
# INDEX.HTML — STEP 1: DISABLE OLD POPUP
# Hide qgis2web's ol-popup div via CSS.
# Removing it causes JS errors; hiding it
# prevents it from showing while allowing
# qgis2web's initialization to complete.
# Map overlay scrolling is stopped by
# clearing overlays in our JS handler.
# ==========================================
DISABLE_OLD_POPUP_CSS = """
    /* Disable qgis2web default popup — replaced by custom popup */
    #popup, .ol-popup, #popup-content, #popup-closer {
        display: none !important;
        visibility: hidden !important;
    }
"""

if '<style>' in html:
    html = html.replace('<style>', '<style>\n' + DISABLE_OLD_POPUP_CSS, 1)
    print("\n  Injected disable-popup CSS into existing style block")
else:
    print("\n  WARNING: <style> tag not found")

# ==========================================
# INDEX.HTML — STEP 2: ADD LEGEND AND
# POPUP CSS, HTML, AND JAVASCRIPT
# Inserted before </body>
# ==========================================
LEGEND_AND_POPUP = """
<!-- BPS Gap Map: Legend, Popup, and Handlers -->
<style>
/* ---- Legend panel ---- */
#bps-legend {
    position: fixed;
    bottom: 50px;
    right: 10px;
    background: rgba(255,255,255,0.97);
    border: 1px solid #bbb;
    border-radius: 6px;
    padding: 12px 16px;
    width: 290px;
    font-family: Arial, sans-serif;
    font-size: 12px;
    line-height: 1.6;
    z-index: 1000;
    max-height: 78vh;
    overflow-y: auto;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
}
#bps-legend h3 {
    margin: 0 0 8px 0;
    font-size: 13px;
    font-family: Arial, sans-serif;
    border-bottom: 2px solid #333;
    padding-bottom: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
#bps-legend h3 button {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 16px;
    color: #555;
    padding: 0;
    line-height: 1;
}
#bps-legend h3 button:hover { color: #000; }
#bps-legend h4 {
    margin: 10px 0 3px 0;
    font-size: 11px;
    font-family: Arial, sans-serif;
    color: #444;
    border-bottom: 1px solid #ddd;
    padding-bottom: 2px;
    letter-spacing: 0.5px;
}
#bps-legend-show {
    position: fixed;
    bottom: 10px;
    right: 10px;
    background: #2C3E50;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
    cursor: pointer;
    font-size: 12px;
    font-family: Arial, sans-serif;
    z-index: 1000;
    display: none;
    box-shadow: 1px 1px 4px rgba(0,0,0,0.3);
}
.leg-circle {
    display: inline-block;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
    border: 1px solid rgba(0,0,0,0.2);
    flex-shrink: 0;
}
.leg-square {
    display: inline-block;
    width: 13px;
    height: 13px;
    margin-right: 6px;
    vertical-align: middle;
    border: 1px solid rgba(0,0,0,0.2);
    flex-shrink: 0;
}
.leg-diamond {
    display: inline-block;
    width: 10px;
    height: 10px;
    margin-right: 8px;
    margin-left: 2px;
    vertical-align: middle;
    border: 1px solid rgba(0,0,0,0.2);
    transform: rotate(45deg);
    flex-shrink: 0;
}
.leg-row {
    display: flex;
    align-items: center;
    margin-bottom: 2px;
}

/* ---- Custom popup ---- */
#bps-popup {
    position: fixed;
    background: #fff;
    border: 1px solid #bbb;
    border-radius: 5px;
    padding: 10px 32px 10px 12px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.25);
    width: 310px;
    max-height: 65vh;
    overflow-y: auto;
    z-index: 2000;
    display: none;
    font-family: Arial, sans-serif;
    font-size: 13px;
    color: #222;
}
#bps-popup-close {
    position: absolute;
    top: 6px;
    right: 10px;
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: #777;
    padding: 0;
    line-height: 1;
}
#bps-popup-close:hover { color: #000; }
</style>

<!-- Custom popup container -->
<div id="bps-popup">
    <button id="bps-popup-close"
            onclick="document.getElementById('bps-popup')
                     .style.display='none';">
        &#10005;
    </button>
    <div id="bps-popup-content"></div>
</div>

<!-- Legend show button (visible when legend is hidden) -->
<button id="bps-legend-show"
        onclick="bpsShowLegend()">
    &#9432; Legend
</button>

<!-- Legend panel -->
<div id="bps-legend">
    <h3>
        BPS OST Gap Analysis
        <button onclick="bpsHideLegend()"
                title="Hide legend">&#10005;</button>
    </h3>

    <h4>SCHOOLS (circles)</h4>
    <div class="leg-row">
        <span class="leg-circle"
              style="width:16px;height:16px;
                     background:#E74C3C;"></span>
        High Concern
    </div>
    <div class="leg-row">
        <span class="leg-circle"
              style="width:16px;height:16px;
                     background:#922B21;"></span>
        High Concern — No Partners
    </div>
    <div class="leg-row">
        <span class="leg-circle"
              style="width:14px;height:14px;
                     background:#E67E22;"></span>
        Moderate-High Concern
    </div>
    <div class="leg-row">
        <span class="leg-circle"
              style="width:14px;height:14px;
                     background:#D35400;"></span>
        Moderate-High — No Partners
    </div>
    <div class="leg-row">
        <span class="leg-circle"
              style="width:12px;height:12px;
                     background:#F4D03F;"></span>
        Moderate Concern
    </div>
    <div class="leg-row">
        <span class="leg-circle"
              style="width:12px;height:12px;
                     background:#B7950B;"></span>
        Moderate — No Partners
    </div>
    <div class="leg-row">
        <span class="leg-circle"
              style="width:10px;height:10px;
                     background:#2ECC71;"></span>
        Lower Concern
    </div>
    <div class="leg-row">
        <span class="leg-circle"
              style="width:10px;height:10px;
                     background:#1E8449;"></span>
        Lower — No Partners
    </div>
    <div class="leg-row">
        <span class="leg-circle"
              style="width:10px;height:10px;
                     background:#BDC3C7;"></span>
        Not applicable (outside Pre-K–8)
    </div>
    <div style="font-size:11px;color:#666;margin-top:3px;">
        Circle size = enrollment in most at-risk grade band
    </div>

    <h4>EEC LICENSED CENTERS (squares)</h4>
    <div class="leg-row">
        <span class="leg-square"
              style="background:#9B59B6;"></span>
        Pre-K only
    </div>
    <div class="leg-row">
        <span class="leg-square"
              style="background:#2980B9;"></span>
        Pre-K and Elementary
    </div>
    <div class="leg-row">
        <span class="leg-square"
              style="background:#17A589;"></span>
        Elementary and Middle
    </div>
    <div style="font-size:11px;color:#666;margin-top:3px;">
        Square size = licensed capacity
        (legal maximum — not confirmed available slots)
    </div>

    <h4>FAMILY CHILD CARE (diamonds)</h4>
    <div class="leg-row">
        <span class="leg-diamond"
              style="background:#1E8449;"></span>
        Licensed and Subsidy
    </div>
    <div class="leg-row">
        <span class="leg-diamond"
              style="background:#A9DFBF;"></span>
        Licensed only
    </div>
    <div class="leg-row">
        <span class="leg-diamond"
              style="background:#2E86C1;"></span>
        Funded and Subsidy
    </div>
    <div class="leg-row">
        <span class="leg-diamond"
              style="background:#BDC3C7;"></span>
        Not current
    </div>
    <div style="font-size:11px;color:#666;margin-top:3px;">
        Age range: birth–13 assumed per MA licensing default.
        Toggle layer on in the layers panel.
    </div>

    <h4>HOW GAPS ARE RANKED</h4>
    <div style="font-size:11px;color:#333;">
        Each school ranked within applicable grade bands
        (Pre-K, Elementary, Middle) on three factors:<br>
        &bull; Enrollment need
            (students &times; % low income)<br>
        &bull; OST partner coverage
            (vetted BPS partners on record)<br>
        &bull; EEC capacity within 10-min walk
            (licensed capacity &divide; schools sharing
            each program)<br>
        <b>Rank 1 = most concerning within band.</b><br>
        Click any school circle for full details.<br><br>
        <i>Rankings are a diagnostic tool — not a precise
        measure of available slots. Licensed capacity is a
        legal maximum. Walk isochrones are estimated and do
        not assess route safety.</i>
    </div>

    <h4>DATA SOURCES</h4>
    <div style="font-size:11px;color:#333;">
        Schools &amp; enrollment: MA DESE, 2026<br>
        EEC programs: MA EEC, March 2026<br>
        OST partners: BPS Partner Programs, 2026<br>
        Walk isochrones: OpenRouteService, 10-min walk<br>
        Analysis prepared March 2026
    </div>
</div>

<script>
// ---- Legend show/hide ----
function bpsHideLegend() {
    document.getElementById('bps-legend').style.display = 'none';
    document.getElementById('bps-legend-show').style.display = 'block';
}
function bpsShowLegend() {
    document.getElementById('bps-legend').style.display = 'block';
    document.getElementById('bps-legend-show').style.display = 'none';
}

// ---- Popup positioning ----
function bpsShowPopup(content, pixelX, pixelY) {
    var popup   = document.getElementById('bps-popup');
    var inner   = document.getElementById('bps-popup-content');
    inner.innerHTML = content;

    // Show first so we can measure dimensions
    popup.style.display = 'block';
    popup.style.left = '-9999px';
    popup.style.top  = '-9999px';

    var pw = popup.offsetWidth  || 320;
    var ph = popup.offsetHeight || 300;
    var vw = window.innerWidth;
    var vh = window.innerHeight;

    var left = pixelX + 15;
    var top  = pixelY - 10;

    if (left + pw > vw - 20) { left = pixelX - pw - 15; }
    if (top  + ph > vh - 20) { top  = vh - ph - 20;     }
    if (top  < 10)           { top  = 10;                }
    if (left < 10)           { left = 10;                }

    popup.style.left = left + 'px';
    popup.style.top  = top  + 'px';
}

// ---- Attach map handlers after map object is ready ----
// qgis2web initializes 'map' asynchronously — poll for it
var bpsMapReady = false;
var bpsInitInterval = setInterval(function () {
    if (typeof map === 'undefined') return;
    if (bpsMapReady) return;
    bpsMapReady = true;
    clearInterval(bpsInitInterval);

    // Remove all OpenLayers overlays (qgis2web adds one
    // for the ol-popup which causes map viewport scrolling)
    map.getOverlays().clear();

    // Single-click handler — use 'singleclick' not 'click'
    // to avoid conflicts with double-click zoom
    map.on('singleclick', function (evt) {
        var hit     = false;
        var content = '';

        map.forEachFeatureAtPixel(
            evt.pixel,
            function (feature, layer) {
                if (hit) return;   // only handle topmost feature
                if (!layer) return;
                var title = layer.get('popuplayertitle');
                if (title === 'BPS_Schools_Ranked') {
                    content = formatSchoolPopup(feature);
                    hit = true;
                } else if (title === 'EEC_Center_Clean') {
                    content = formatEECCenterPopup(feature);
                    hit = true;
                } else if (title === 'EEC_FCC_Clean') {
                    content = formatFCCPopup(feature);
                    hit = true;
                }
            }
        );

        if (hit) {
            bpsShowPopup(content, evt.pixel[0], evt.pixel[1]);
        } else {
            document.getElementById('bps-popup').style.display = 'none';
        }
    });

    // Pointer cursor on hover
    map.on('pointermove', function (evt) {
        if (evt.dragging) return;
        var hit = map.hasFeatureAtPixel(evt.pixel);
        map.getTargetElement().style.cursor = hit ? 'pointer' : '';
    });

}, 100);
</script>
"""

if '</body>' in html:
    html = html.replace('</body>', LEGEND_AND_POPUP + '\n</body>')
    print("  Inserted legend, popup, and handlers before </body>")
else:
    print("  WARNING: </body> not found — content not inserted")

# ==========================================
# STEP 6: ADD CHART.JS TO HEAD
# ==========================================
CHARTJS = ('<script src="https://cdn.jsdelivr.net/npm/'
           'chart.js@4.4.0/dist/chart.umd.min.js">'
           '</script>\n')
if '</head>' in html:
    html = html.replace('</head>', CHARTJS + '</head>')
    print("  Inserted Chart.js CDN")
else:
    print("  WARNING: </head> not found for Chart.js")

# ==========================================
# STEP 7: ADD SEARCH, BAND FILTERS,
#          AND ANALYTICS DRAWER
# ==========================================
SEARCH_AND_ANALYTICS = """
<style>
/* ========== SEARCH BAR ========== */
#bps-search-wrap {
    position: fixed;
    top: 10px;
    left: 55px;
    z-index: 1000;
    display: flex;
    gap: 4px;
    align-items: center;
}
#bps-search-input {
    width: 220px;
    padding: 6px 10px;
    border: 1px solid #bbb;
    border-radius: 4px;
    font-size: 13px;
    font-family: Arial, sans-serif;
    box-shadow: 1px 1px 4px rgba(0,0,0,0.15);
    outline: none;
    background: white;
}
#bps-search-input:focus { border-color: #2C3E50; }
#bps-search-clear {
    background: #777;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    cursor: pointer;
    font-size: 12px;
    font-family: Arial, sans-serif;
    display: none;
}
#bps-search-results {
    position: fixed;
    top: 40px;
    left: 55px;
    background: white;
    border: 1px solid #bbb;
    border-radius: 0 0 4px 4px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.15);
    z-index: 1001;
    max-height: 200px;
    overflow-y: auto;
    width: 260px;
    display: none;
    font-family: Arial, sans-serif;
    font-size: 12px;
}
.bps-search-result-item {
    padding: 6px 10px;
    cursor: pointer;
    border-bottom: 1px solid #eee;
}
.bps-search-result-item:hover { background: #f0f4f8; }
.bps-search-result-type {
    font-size: 10px;
    color: #888;
    float: right;
}

/* ========== BAND FILTER BUTTONS ========== */
#bps-band-wrap {
    position: fixed;
    top: 44px;
    left: 55px;
    z-index: 1000;
    display: flex;
    gap: 4px;
}
.bps-band-btn {
    padding: 4px 12px;
    border: 1px solid #999;
    border-radius: 12px;
    font-size: 11px;
    font-family: Arial, sans-serif;
    cursor: pointer;
    background: white;
    color: #444;
}
.bps-band-btn.active {
    background: #2C3E50;
    color: white;
    border-color: #2C3E50;
}

/* ========== ANALYTICS DRAWER ========== */
#bps-drawer-tab {
    position: fixed;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    background: #2C3E50;
    color: white;
    border: none;
    border-radius: 6px 6px 0 0;
    padding: 5px 22px;
    cursor: pointer;
    font-size: 12px;
    font-family: Arial, sans-serif;
    z-index: 1001;
    white-space: nowrap;
}
#bps-drawer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 320px;
    background: white;
    border-top: 2px solid #2C3E50;
    z-index: 1000;
    display: none;
    flex-direction: column;
    padding: 8px 16px 10px 16px;
    box-shadow: 0 -3px 10px rgba(0,0,0,0.15);
}
#bps-drawer-controls {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
    flex-shrink: 0;
    flex-wrap: wrap;
}
#bps-metric-select {
    padding: 5px 8px;
    font-size: 12px;
    font-family: Arial, sans-serif;
    border: 1px solid #bbb;
    border-radius: 4px;
    background: white;
}
#bps-sort-btn {
    padding: 5px 12px;
    font-size: 12px;
    font-family: Arial, sans-serif;
    border: 1px solid #bbb;
    border-radius: 4px;
    cursor: pointer;
    background: white;
    white-space: nowrap;
}
#bps-band-note {
    font-size: 11px;
    color: #888;
    font-family: Arial, sans-serif;
    font-style: italic;
}
#bps-school-count {
    font-size: 11px;
    color: #555;
    font-family: Arial, sans-serif;
}
#bps-drawer-close {
    margin-left: auto;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 18px;
    color: #666;
    padding: 0;
    line-height: 1;
}
/* Scrollable chart container */
#bps-chart-wrap {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    position: relative;
    width: 100%;
    box-sizing: border-box;
    min-height: 0;
}
#bps-chart-canvas {
    display: block;
    width: 100% !important;
    box-sizing: border-box;
}
/* Hint text */
#bps-chart-hint {
    font-size: 10px;
    color: #aaa;
    font-family: Arial, sans-serif;
    font-style: italic;
    flex-shrink: 0;
    padding-top: 2px;
}
</style>

<!-- Search bar -->
<div id="bps-search-wrap">
    <input id="bps-search-input"
           type="text"
           placeholder="&#128269; Search school or program..."
           oninput="bpsSearchInput(this.value)"
           onkeydown="bpsSearchKey(event)"
           autocomplete="off">
    <button id="bps-search-clear"
            onclick="bpsClearSearch()">&#10005; Clear</button>
</div>
<div id="bps-search-results"></div>

<!-- Band filter buttons -->
<div id="bps-band-wrap">
    <button class="bps-band-btn active" id="btn-ALL"
            onclick="bpsSetBand(null)">All Bands</button>
    <button class="bps-band-btn" id="btn-PREK"
            onclick="bpsSetBand('PREK')">Pre-K</button>
    <button class="bps-band-btn" id="btn-ELEM"
            onclick="bpsSetBand('ELEM')">Elementary</button>
    <button class="bps-band-btn" id="btn-MIDDLE"
            onclick="bpsSetBand('MIDDLE')">Middle</button>
</div>

<!-- Analytics drawer tab -->
<button id="bps-drawer-tab" onclick="bpsToggleDrawer()">
    &#9650; Analytics
</button>

<!-- Analytics drawer -->
<div id="bps-drawer">
    <div id="bps-drawer-controls">
        <select id="bps-metric-select" onchange="bpsUpdateChart()">
            <option value="OVERALL">Overall Gap Score</option>
            <option value="PARTNERS">OST Partner Coverage</option>
            <option value="CHILDCARE">Local EEC Capacity</option>
            <option value="NEED">Low Income Enrollment</option>
            <option value="OI">BPS Opportunity Index</option>
        </select>
        <button id="bps-sort-btn" onclick="bpsToggleSort()">
            Sort: Highest First
        </button>
        <span id="bps-band-note"></span>
        <span id="bps-school-count"></span>
        <button id="bps-drawer-close"
                onclick="bpsToggleDrawer()"
                title="Close">&#10005;</button>
    </div>
    <div id="bps-chart-hint">
        Scroll to see all schools &nbsp;|&nbsp;
        Click any bar or school name to zoom map
    </div>
    <div id="bps-chart-wrap">
        <canvas id="bps-chart-canvas"></canvas>
    </div>
</div>

<script>
// ==========================================
// UTILITIES
// ==========================================
function bpsIsTrue(val) {
    return val === true || val === 1 ||
           val === 'true' || val === 'True';
}
function bpsTruncate(str, n) {
    return str && str.length > n ?
           str.substring(0, n - 2) + '\\u2026' : (str || '');
}

// ==========================================
// SEARCH
// ==========================================
var bpsSearchData = [];

function bpsSearchInput(query) {
    var clearBtn  = document.getElementById('bps-search-clear');
    var resultsEl = document.getElementById('bps-search-results');
    if (!query || query.length < 2) {
        clearBtn.style.display  = 'none';
        resultsEl.style.display = 'none';
        return;
    }
    clearBtn.style.display = 'block';
    if (!bpsMapReady) return;

    var q       = query.toLowerCase();
    var matches = bpsSearchData.filter(function(d) {
        return d.name.toLowerCase().indexOf(q) >= 0;
    }).slice(0, 10);

    if (matches.length === 0) {
        resultsEl.style.display = 'none';
        return;
    }
    resultsEl.innerHTML = matches.map(function(d, i) {
        return '<div class="bps-search-result-item"'
            + ' onclick="bpsSelectSearchResult(' + i + ')">'
            + '<span class="bps-search-result-type">'
            + d.type + '</span>'
            + bpsTruncate(d.name, 45)
            + '</div>';
    }).join('');
    resultsEl._matches  = matches;
    resultsEl.style.display = 'block';
}

function bpsSelectSearchResult(i) {
    var resultsEl = document.getElementById('bps-search-results');
    var matches   = resultsEl._matches;
    if (!matches || i >= matches.length) return;
    var d       = matches[i];
    var geom    = d.feature.getGeometry();
    var coords  = geom.getCoordinates
        ? geom.getCoordinates()
        : ol.extent.getCenter(geom.getExtent());
    map.getView().animate({ center: coords, zoom: 15, duration: 600 });
    var content = '';
    if (d.type === 'School')      content = formatSchoolPopup(d.feature);
    else if (d.type === 'EEC Center') content = formatEECCenterPopup(d.feature);
    if (content) bpsShowPopup(content,
        map.getSize()[0] / 2, map.getSize()[1] / 3);
    document.getElementById('bps-search-input').value = d.name;
    resultsEl.style.display = 'none';
}

function bpsSearchKey(evt) {
    if (evt.key === 'Escape') bpsClearSearch();
}
function bpsClearSearch() {
    document.getElementById('bps-search-input').value = '';
    document.getElementById('bps-search-clear').style.display = 'none';
    document.getElementById('bps-search-results').style.display = 'none';
}
document.addEventListener('click', function(e) {
    var wrap = document.getElementById('bps-search-wrap');
    var res  = document.getElementById('bps-search-results');
    if (wrap && res &&
        !wrap.contains(e.target) && !res.contains(e.target)) {
        res.style.display = 'none';
    }
});

// ==========================================
// BAND FILTER
// ==========================================
var bpsBandFilter = null;

function bpsSetBand(band) {
    bpsBandFilter = band;
    ['btn-ALL','btn-PREK','btn-ELEM','btn-MIDDLE']
        .forEach(function(id) {
            var el = document.getElementById(id);
            if (el) el.classList.remove('active');
        });
    var activeId = band ? 'btn-' + band : 'btn-ALL';
    var activeEl = document.getElementById(activeId);
    if (activeEl) activeEl.classList.add('active');
    bpsApplyBandFilter();
    if (bpsDrawerOpen) bpsUpdateChart();
}

function bpsApplyBandFilter() {
    if (!bpsMapReady) return;
    lyr_BPS_Schools_Ranked_4.setStyle(function(f, res) {
        if (bpsBandFilter !== null) {
            if (!bpsIsTrue(f.get('SCHOOL_' + bpsBandFilter)))
                return null;
        }
        return style_BPS_Schools_Ranked_4(f, res);
    });
    lyr_EEC_Center_Clean_3.setStyle(function(f, res) {
        if (bpsBandFilter !== null) {
            if (!bpsIsTrue(f.get('SERVES_' + bpsBandFilter)))
                return null;
        }
        return style_EEC_Center_Clean_3(f, res);
    });
}

// ==========================================
// ANALYTICS DRAWER
// ==========================================
var bpsDrawerOpen = false;
var bpsSortWorst  = true;   // true = highest first (descending)
var bpsChart      = null;
var bpsChartData  = [];     // current chart data — used by click handler

// Metrics where band filter does not apply
var BPS_NO_BAND_METRICS = ['NEED', 'OI'];

var METRIC_LABELS = {
    'OVERALL':  'Overall Gap Score',
    'PARTNERS': 'OST Partner Coverage',
    'CHILDCARE':'Local EEC Capacity (adjusted)',
    'NEED':     'Low Income Enrollment',
    'OI':       'BPS Opportunity Index Score'
};
var BAND_LABELS = {
    'PREK':'Pre-K', 'ELEM':'Elementary', 'MIDDLE':'Middle'
};
var METRIC_COLORS = {
    'OVERALL':  'rgba(192,57,43,0.75)',
    'PARTNERS': 'rgba(41,128,185,0.75)',
    'CHILDCARE':'rgba(23,165,137,0.75)',
    'NEED':     'rgba(155,89,182,0.75)',
    'OI':       'rgba(39,174,96,0.75)'
};

function bpsGetVal(props, metric, band) {
    var v;
    switch (metric) {
        case 'OVERALL':
            if (band) {
                // Band selected — use that band's composite
                if (!bpsIsTrue(props['SCHOOL_' + band])) return null;
                v = parseFloat(props['COMPOSITE_' + band]);
            } else {
                // All Bands — use the school's primary gap band composite
                var pgb = props['PRIMARY_GAP_BAND'];
                if (!pgb || pgb === 'Not applicable' ||
                    pgb === 'null' || pgb === '') return null;
                v = parseFloat(props['COMPOSITE_' + pgb]);
            }
            return isNaN(v) ? null : v;

        case 'PARTNERS':
            if (band) {
                if (!bpsIsTrue(props['SCHOOL_' + band])) return null;
                v = parseFloat(props['OST_' + band + '_CNT']);
            } else {
                v = parseFloat(props['OST_TOTAL_CNT']);
            }
            return isNaN(v) ? 0 : v;

        case 'CHILDCARE':
            if (band) {
                if (!bpsIsTrue(props['SCHOOL_' + band])) return null;
                v = parseFloat(props['EEC_ADJ_CAP_' + band]);
            } else {
                v = (parseFloat(props['EEC_ADJ_CAP_PREK'])   || 0)
                  + (parseFloat(props['EEC_ADJ_CAP_ELEM'])   || 0)
                  + (parseFloat(props['EEC_ADJ_CAP_MIDDLE']) || 0);
            }
            return isNaN(v) ? 0 : v;

        case 'NEED':
            v = parseFloat(props['NEED_SCORE']);
            return isNaN(v) ? null : v;

        case 'OI':
            v = parseFloat(props['BPS_OI_SCORE']);
            return isNaN(v) ? null : v;

        default: return null;
    }
}

function bpsToggleDrawer() {
    bpsDrawerOpen = !bpsDrawerOpen;
    var drawer = document.getElementById('bps-drawer');
    var tab    = document.getElementById('bps-drawer-tab');
    if (bpsDrawerOpen) {
        drawer.style.display = 'flex';
        tab.innerHTML        = '&#9660; Analytics';
        tab.style.bottom     = '320px';
        bpsUpdateChart();
    } else {
        drawer.style.display = 'none';
        tab.innerHTML        = '&#9650; Analytics';
        tab.style.bottom     = '0';
    }
}

function bpsToggleSort() {
    bpsSortWorst = !bpsSortWorst;
    document.getElementById('bps-sort-btn').textContent =
        bpsSortWorst ? 'Sort: Highest First' : 'Sort: Lowest First';
    bpsUpdateChart();
}

// Navigate to school feature on map
function bpsZoomToFeature(feature) {
    if (!feature) return;
    var geom   = feature.getGeometry();
    var coords = geom.getCoordinates
        ? geom.getCoordinates()
        : ol.extent.getCenter(geom.getExtent());
    map.getView().animate({ center: coords, zoom: 15, duration: 600 });
    bpsShowPopup(
        formatSchoolPopup(feature),
        map.getSize()[0] / 2,
        map.getSize()[1] / 3
    );
}

function bpsUpdateChart() {
    if (!bpsMapReady || !bpsDrawerOpen) return;
    if (typeof Chart === 'undefined') return;

    var metric = document.getElementById('bps-metric-select').value;
    var noBand = BPS_NO_BAND_METRICS.indexOf(metric) >= 0;
    var band   = noBand ? null : bpsBandFilter;

    // Band note
    var note = document.getElementById('bps-band-note');
    if (noBand) {
        note.textContent = 'Band filter not applicable for this metric';
    } else if (band) {
        note.textContent = BAND_LABELS[band] + ' schools only';
    } else {
        note.textContent = 'All applicable schools';
    }

    // Collect and sort data
    var raw = [];
    lyr_BPS_Schools_Ranked_4.getSource().forEachFeature(function(f) {
        var p   = f.getProperties();
        var val = bpsGetVal(p, metric, band);
        if (val === null) return;
        raw.push({
            name:    p['NAME'] || 'Unknown',
            value:   Math.round(val * 100) / 100,
            feature: f
        });
    });

    raw.sort(function(a, b) {
        return bpsSortWorst ? b.value - a.value : a.value - b.value;
    });

    bpsChartData = raw;
    document.getElementById('bps-school-count').textContent =
        raw.length + ' schools';

    // Destroy existing chart instance
    if (bpsChart) { bpsChart.destroy(); bpsChart = null; }

    // ---- Recreate canvas element entirely ----
    // Prevents Chart.js responsive resize listener
    // from squashing bars after filter interactions
    var wrap = document.getElementById('bps-chart-wrap');
    var oldCanvas = document.getElementById('bps-chart-canvas');
    if (oldCanvas) { oldCanvas.remove(); }

    var canvas   = document.createElement('canvas');
    canvas.id    = 'bps-chart-canvas';
    wrap.appendChild(canvas);

    // Calculate dimensions
    // 30px per bar ensures 10pt font is readable at all school counts
    var barH    = 30;
    var canvasH = Math.max(320, raw.length * barH + 80);
    var canvasW = wrap.clientWidth || 800;

    // Set both CSS and canvas buffer dimensions to same values
    // responsive:false means Chart.js uses buffer dimensions directly
    canvas.width        = canvasW;
    canvas.height       = canvasH;
    canvas.style.width  = canvasW + 'px';
    canvas.style.height = canvasH + 'px';
    canvas.style.display = 'block';

    var col        = METRIC_COLORS[metric] || 'rgba(100,100,100,0.75)';
    var bandSuffix = band ? ' — ' + BAND_LABELS[band] : '';
    var ctx        = canvas.getContext('2d');

    bpsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: raw.map(function(d) {
                return bpsTruncate(d.name, 40);
            }),
            datasets: [{
                label:           METRIC_LABELS[metric] + bandSuffix,
                data:            raw.map(function(d) { return d.value; }),
                backgroundColor: col,
                borderColor:     col.replace('0.75', '1'),
                borderWidth:     1,
                borderRadius:    3,
                minBarLength:    8,
                barThickness:    18
            }]
        },
        options: {
            indexAxis:           'y',
            responsive:          false,
            maintainAspectRatio: false,
            animation:           { duration: 200 },
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text:  METRIC_LABELS[metric] + bandSuffix
                            + '  ('
                            + (bpsSortWorst ? 'highest first' : 'lowest first')
                            + ')  |  Click bar or name to zoom to school',
                    font:  { size: 11, family: 'Arial' },
                    color: '#555',
                    padding: { bottom: 4 }
                },
                tooltip: {
                    callbacks: {
                        title: function(items) {
                            return bpsChartData[items[0].dataIndex].name;
                        },
                        label: function(item) {
                            return ' ' + item.parsed.x;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { font: { size: 10, family: 'Arial' } },
                    grid:  { color: 'rgba(0,0,0,0.05)' }
                },
                y: {
                    ticks: {
                        font:     { size: 10, family: 'Arial' },
                        autoSkip: false,
                        padding:  4
                    },
                    grid: { display: false }
                }
            },
            onClick: function(evt, elements, chart) {
                var idx = null;
                if (elements && elements.length > 0) {
                    idx = elements[0].index;
                } else {
                    try {
                        var ca       = chart.chartArea;
                        var offX     = evt.native.offsetX;
                        var offY     = evt.native.offsetY;
                        var inLabel  = offX < ca.left;
                        var inChart  = offX >= ca.left && offX <= ca.right;
                        var inYRange = offY >= ca.top  && offY <= ca.bottom;
                        if ((inLabel || inChart) && inYRange) {
                            var pct = (offY - ca.top) /
                                      (ca.bottom - ca.top);
                            idx = Math.floor(pct * bpsChartData.length);
                            if (idx < 0) idx = 0;
                            if (idx >= bpsChartData.length)
                                idx = bpsChartData.length - 1;
                        }
                    } catch(e) { idx = null; }
                }
                if (idx === null || idx < 0 ||
                    idx >= bpsChartData.length) return;
                bpsZoomToFeature(bpsChartData[idx].feature);
            }
        }
    });
}

// ==========================================
// INITIALIZATION
// ==========================================
var bpsMapReady    = false;
var bpsExtrasReady = false;

var bpsInitInterval = setInterval(function() {
    if (typeof map === 'undefined') return;
    if (bpsMapReady) return;
    bpsMapReady = true;
    map.getOverlays().clear();

    map.on('singleclick', function(evt) {
        var hit     = false;
        var content = '';
        map.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
            if (hit) return;
            if (!layer) return;
            var title = layer.get('popuplayertitle');
            if (title === 'BPS_Schools_Ranked') {
                content = formatSchoolPopup(feature);  hit = true;
            } else if (title === 'EEC_Center_Clean') {
                content = formatEECCenterPopup(feature); hit = true;
            } else if (title === 'EEC_FCC_Clean') {
                content = formatFCCPopup(feature);      hit = true;
            }
        });
        if (hit) bpsShowPopup(content, evt.pixel[0], evt.pixel[1]);
        else document.getElementById('bps-popup').style.display = 'none';
    });

    map.on('pointermove', function(evt) {
        if (evt.dragging) return;
        var hit = map.hasFeatureAtPixel(evt.pixel);
        map.getTargetElement().style.cursor = hit ? 'pointer' : '';
    });
}, 100);

var bpsFeatureInterval = setInterval(function() {
    if (!bpsMapReady) return;
    if (bpsExtrasReady) return;
    if (typeof lyr_BPS_Schools_Ranked_4 === 'undefined') return;
    if (typeof lyr_EEC_Center_Clean_3   === 'undefined') return;

    var sf = lyr_BPS_Schools_Ranked_4.getSource().getFeatures();
    var ef = lyr_EEC_Center_Clean_3.getSource().getFeatures();
    if (sf.length === 0) return;

    clearInterval(bpsFeatureInterval);
    bpsExtrasReady = true;

    // Build search index
    bpsSearchData = [];
    sf.forEach(function(f) {
        var name = f.get('NAME');
        if (name) bpsSearchData.push({
            name: name, type: 'School', feature: f
        });
    });
    ef.forEach(function(f) {
        var name = f.get('PROGRAM_NAME');
        if (name) bpsSearchData.push({
            name: name, type: 'EEC Center', feature: f
        });
    });
    bpsSearchData.sort(function(a, b) {
        return a.name.localeCompare(b.name);
    });

    bpsApplyBandFilter();
    console.log('BPS extras ready. Search: '
                + bpsSearchData.length + ' items.');
}, 200);
</script>
"""


if '</body>' in html:
    html = html.replace('</body>',
                        SEARCH_AND_ANALYTICS + '\n</body>')
    print("  Inserted search bar, band filters, "
          "and analytics drawer")
else:
    print("  WARNING: </body> not found for analytics")

# ==========================================
# SAVE INDEX.HTML
# ==========================================
INDEX_HTML.write_text(html, encoding='utf-8')
print(f"  Saved index.html — final size: {len(html)} chars")

print("\nPost-processing complete.")
print(f"Open {WEB_FOLDER / 'index.html'} in a browser to review.")