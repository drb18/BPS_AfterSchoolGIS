import pandas as pd

fcc = pd.read_csv('EEC_FCC_Clean.csv',
                  encoding='utf-8-sig', low_memory=False)

def quality_label(row):
    licensed = row.get('QUALITY_LICENSED', False)
    voucher  = row.get('QUALITY_VOUCHER',  False)
    if licensed and voucher:
        return 'Licensed and Subsidy'
    if licensed and not voucher:
        return 'Licensed only'
    if not licensed and voucher:
        return 'Funded and Subsidy'
    return 'Not current'

fcc['QUALITY_LABEL'] = fcc.apply(quality_label, axis=1)

print("QUALITY_LABEL distribution:")
print(fcc['QUALITY_LABEL'].value_counts().to_string())

fcc.to_csv('EEC_FCC_Clean.csv', index=False, encoding='utf-8-sig')
print("Saved.")
