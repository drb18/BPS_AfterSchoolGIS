#!/usr/bin/env node
/**
 * test_analytics_coverage.js
 *
 * Verifies that every PK–Grade 8 school in the map layer appears in the
 * analytics drawer for each applicable metric / band combination.
 *
 * High-school-only schools (PRIMARY_GAP_BAND = 'Not applicable') are
 * intentionally excluded from gap analysis — this test treats their
 * absence as expected and documents them as such.
 *
 * Run:   node test_analytics_coverage.js
 *
 * Exit codes
 *   0  All tests passed (only expected exclusions found)
 *   1  Unexpected missing schools detected (data gaps requiring a fix)
 */

'use strict';

const fs   = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// 1. Load school data from the layer JS file
// ---------------------------------------------------------------------------
const layerPath = path.join(__dirname, 'layers', 'BPS_Schools_Ranked_4.js');
let   raw       = fs.readFileSync(layerPath, 'utf8');
// Strip the JS variable wrapper to get plain JSON
raw = raw.replace(/^\s*var\s+json_BPS_Schools_Ranked_4\s*=\s*/, '').replace(/;\s*$/, '');
const geojson  = JSON.parse(raw);
const features = geojson.features;

// ---------------------------------------------------------------------------
// 2. Mirror the exact JS helpers from index.html
// ---------------------------------------------------------------------------

/** Matches bpsIsTrue() in index.html */
function isTrue(val) {
    return val === true || val === 1 || val === 'true' || val === 'True';
}

/**
 * Matches bpsGetVal() in index.html.
 * Returns a numeric value, 0, or null (null = school excluded from chart).
 */
function getVal(props, metric, band) {
    let v;
    switch (metric) {
        case 'OVERALL':
            if (band) {
                if (!isTrue(props['SCHOOL_' + band])) return null;
                v = parseFloat(props['COMPOSITE_' + band]);
            } else {
                const pgb = props['PRIMARY_GAP_BAND'];
                if (!pgb || pgb === 'Not applicable' ||
                    pgb === 'null' || pgb === '') return null;
                v = parseFloat(props['COMPOSITE_' + pgb]);
            }
            return isNaN(v) ? null : v;

        case 'PARTNERS':
            if (band) {
                if (!isTrue(props['SCHOOL_' + band])) return null;
                v = parseFloat(props['OST_' + band + '_CNT']);
            } else {
                v = parseFloat(props['OST_TOTAL_CNT']);
            }
            return isNaN(v) ? 0 : v;

        case 'CHILDCARE':
            if (band) {
                if (!isTrue(props['SCHOOL_' + band])) return null;
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

// ---------------------------------------------------------------------------
// 3. Classify schools
// ---------------------------------------------------------------------------

/**
 * Returns true for schools whose focus is high school / adult only.
 * The map targets PK–Grade 8 before/after care, so these schools having
 * PRIMARY_GAP_BAND = 'Not applicable' is correct and expected.
 */
function isHighSchoolOnly(props) {
    return props['PRIMARY_GAP_BAND'] === 'Not applicable';
}

// ---------------------------------------------------------------------------
// 4. Run checks for every metric × band combination
// ---------------------------------------------------------------------------

const METRICS = ['OVERALL', 'PARTNERS', 'CHILDCARE', 'NEED', 'OI'];
// null = "All Bands" view; NEED and OI ignore band filter, so only test null
const BANDS_BY_METRIC = {
    OVERALL:   [null, 'PREK', 'ELEM', 'MIDDLE'],
    PARTNERS:  [null, 'PREK', 'ELEM', 'MIDDLE'],
    CHILDCARE: [null, 'PREK', 'ELEM', 'MIDDLE'],
    NEED:      [null],
    OI:        [null],
};

let   totalTests = 0;
let   failures   = 0;
const report     = [];

function bandLabel(b) { return b || 'All Bands'; }

for (const metric of METRICS) {
    for (const band of BANDS_BY_METRIC[metric]) {
        totalTests++;
        const shown  = [];
        const hidden = [];

        for (const f of features) {
            const p   = f.properties;
            const val = getVal(p, metric, band);
            (val === null ? hidden : shown).push(p['NAME'] || 'Unknown');
        }

        // Categorise each hidden school as expected or unexpected
        const unexpected = [];
        const expected   = [];

        for (const f of features) {
            const p = f.properties;
            if (getVal(p, metric, band) !== null) continue;  // visible, skip
            const name = p['NAME'] || 'Unknown';

            // Band filter hiding a school that doesn't serve that grade — correct
            if (band && !isTrue(p['SCHOOL_' + band])) {
                expected.push({ name, reason: `Does not serve ${band} grade band` });
                continue;
            }

            // High-school-only schools absent from OVERALL — by design
            if (metric === 'OVERALL' && isHighSchoolOnly(p)) {
                expected.push({
                    name,
                    reason: 'High-school / adult focus — outside PK–8 scope (PRIMARY_GAP_BAND = Not applicable)',
                });
                continue;
            }

            // Anything else is an unexpected data gap
            const reasons = [];
            if (metric === 'OI' && (p['BPS_OI_SCORE'] == null || p['BPS_OI_SCORE'] === '')) {
                reasons.push('BPS_OI_SCORE is null/missing in the layer data');
            }
            if (metric === 'NEED' && (p['NEED_SCORE'] == null || p['NEED_SCORE'] === '')) {
                reasons.push('NEED_SCORE is null/missing in the layer data');
            }
            if (metric === 'OVERALL' && !isHighSchoolOnly(p)) {
                const pgb = p['PRIMARY_GAP_BAND'];
                reasons.push(`PRIMARY_GAP_BAND is ${JSON.stringify(pgb)} but school is not high-school-only`);
            }
            unexpected.push({
                name,
                reason: reasons.length ? reasons.join('; ') : 'Unexpected null from getVal()',
            });
        }

        const passed = unexpected.length === 0;
        if (!passed) failures++;

        report.push({
            metric,
            band: bandLabel(band),
            shown:      shown.length,
            hidden:     hidden.length,
            expected,
            unexpected,
            passed,
        });
    }
}

// ---------------------------------------------------------------------------
// 5. Print report
// ---------------------------------------------------------------------------

const COL = {
    green:  s => `\x1b[32m${s}\x1b[0m`,
    red:    s => `\x1b[31m${s}\x1b[0m`,
    yellow: s => `\x1b[33m${s}\x1b[0m`,
    bold:   s => `\x1b[1m${s}\x1b[0m`,
};

console.log('');
console.log('='.repeat(72));
console.log(COL.bold(' BPS Analytics Coverage Test  —  PK through Grade 8 schools'));
console.log(`  Schools in layer file: ${features.length} total`);
console.log('='.repeat(72));

for (const r of report) {
    const statusTag = r.passed ? COL.green('PASS') : COL.red('FAIL');
    const label     = `${r.metric} / ${r.band}`;
    console.log(`\n[${statusTag}] ${label.padEnd(30)} shown=${r.shown}  hidden=${r.hidden}`);

    if (r.unexpected.length > 0) {
        console.log(COL.red(`       ▶ ${r.unexpected.length} UNEXPECTED missing school(s):`));
        for (const u of r.unexpected) {
            console.log(`       ${COL.red('✗')} ${u.name}`);
            console.log(`         Fix: ${u.reason}`);
        }
    }

    if (r.expected.length > 0 && r.band === 'All Bands') {
        // Only summarise expected exclusions for the "All Bands" view to keep
        // per-band output concise (per-band exclusions are grade-level filtering)
        console.log(`       ${r.expected.length} school(s) correctly excluded (see below)`);
    }
}

// Print the expected-exclusion detail once, not once per metric
console.log('');
console.log('-'.repeat(72));
console.log(COL.bold(' Expected exclusions (PK–8 scope)'));
console.log('-'.repeat(72));
const allExpected = new Map();
for (const r of report) {
    for (const e of r.expected) {
        if (!allExpected.has(e.name)) allExpected.set(e.name, e.reason);
    }
}
// Only list high-school-only schools once (the reason is always the same)
const highSchoolOnly = [...allExpected.entries()].filter(
    ([, r]) => r.startsWith('High-school')
);
const gradeFiltered  = [...allExpected.entries()].filter(
    ([, r]) => r.startsWith('Does not')
);
if (highSchoolOnly.length) {
    console.log(`\n  ${highSchoolOnly.length} high-school / adult-focus school(s) — no PK–8 gap ranking computed:`);
    for (const [name] of highSchoolOnly) {
        console.log(`    ${COL.yellow('○')} ${name}`);
    }
}
if (gradeFiltered.length) {
    console.log(`\n  ${gradeFiltered.length} school(s) hidden only because of a band filter`);
    console.log('  (they appear correctly when no band filter is applied)');
}

// ---------------------------------------------------------------------------
// 6. Summary
// ---------------------------------------------------------------------------
console.log('');
console.log('='.repeat(72));
console.log(COL.bold(` Results: ${totalTests - failures}/${totalTests} tests passed`));

if (failures > 0) {
    console.log(COL.red(` ${failures} test(s) FAILED — data gap(s) detected.`));
    console.log('');
    console.log(' How to fix:');
    console.log('   1. Supply the missing field values in BPS_Schools_Ranked.gpkg');
    console.log('   2. Re-run add_symbology_to_schools.py and the QGIS web export');
    console.log('   3. Re-run this test to confirm 0 failures');
} else {
    console.log(COL.green(' All tests passed.'));
    console.log(' Every PK–8 school is represented in the analytics for each metric.');
}
console.log('='.repeat(72));
console.log('');

process.exit(failures > 0 ? 1 : 0);
