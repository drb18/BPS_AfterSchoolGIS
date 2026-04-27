import pandas as pd

eec = pd.read_csv('EEC_Center_Clean.csv',
                  encoding='utf-8-sig', low_memory=False)

def band_label(row):
    prek   = row.get('SERVES_PREK',   False)
    elem   = row.get('SERVES_ELEM',   False)
    middle = row.get('SERVES_MIDDLE', False)

    if elem and middle:
        return 'Elementary and Middle'
    if prek and elem:
        return 'Pre-K and Elementary'
    if prek and middle:
        return 'Pre-K and Middle'
    if prek and elem and middle:
        return 'All Bands'
    if prek:
        return 'Pre-K only'
    if elem:
        return 'Elementary only'
    if middle:
        return 'Middle only'
    return 'Unknown'

eec['BAND_LABEL'] = eec.apply(band_label, axis=1)

print("Updated BAND_LABEL distribution:")
print(eec['BAND_LABEL'].value_counts().to_string())

eec.to_csv('EEC_Center_Clean.csv', index=False, encoding='utf-8-sig')
print("Saved.")
