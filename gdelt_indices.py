# GDELT INDEX GENERATOR V3.0 - Sentiment-Weighted
# Formul: Sigma(NumMentions x |AvgTone|/100 x |Goldstein|/10) / Sigma(NumMentions)
# Calistirmak icin CMD: python gdelt_indices.py

import pandas as pd
import numpy as np
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import urllib.error
import datetime
import os
import time
import concurrent.futures

# ============================================================
# AYARLAR
# ============================================================
OUTPUT_FILE  = './indices.csv'
MAX_WORKERS  = 8
RETRY_COUNT  = 3
RETRY_DELAY  = 3

# ============================================================
# GDELT SÜTUN TANIMLARI
# ============================================================
V2HEADERS = [
    'GLOBALEVENTID','Date','MonthYear','Year','FractionDate','Source',
    'Actor1Name','Actor1CountryCode','Actor1KnownGroupCode','Actor1EthnicCode',
    'Actor1Religion1Code','Actor1Religion2Code','Actor1Type1Code','Actor1Type2Code',
    'Actor1Type3Code','Target','Actor2Name','Actor2CountryCode','Actor2KnownGroupCode',
    'Actor2EthnicCode','Actor2Religion1Code','Actor2Religion2Code','Actor2Type1Code',
    'Actor2Type2Code','Actor2Type3Code','IsRootEvent','CAMEOCode','EventBaseCode',
    'EventRootCode','QuadClass','Goldstein','NumMentions','NumEvents','NumArts',
    'AvgTone','SourceGeoType','Actor1Geo_FullName','Actor1Geo_CountryCode',
    'Actor1Geo_ADM1Code','SourceGeoLat','SourceGeoLong','Actor1Geo_FeatureID',
    'TargetGeoType','Actor2Geo_FullName','Actor2Geo_CountryCode','Actor2Geo_ADM1Code',
    'TargetGeoLat','TargetGeoLong','Actor2Geo_FeatureID','ActionGeoType',
    'ActionGeo_FullName','ActionGeo_CountryCode','ActionGeo_ADM1Code',
    'ActionGeoLat','ActionGeoLong','ActionGeo_FeatureID','DATEADDED','SOURCEURL'
]

# V3: Goldstein, NumMentions, AvgTone eklendi
SELECTED_COLUMNS = [
    'DATEADDED',
    'Actor1Geo_CountryCode', 'Actor2Geo_CountryCode', 'ActionGeo_CountryCode',
    'QuadClass', 'EventRootCode', 'CAMEOCode',
    'Goldstein',      # -10 (çatışma) ile +10 (işbirliği) arası
    'NumMentions',    # medya önem ağırlığı
    'AvgTone',        # -100 (negatif) ile +100 (pozitif) arası
]

# ============================================================
# KONU TANIMLARI (CAMEO KODLARI)
# ============================================================
TOPICS = {
    'appeal_of_leadership_change': ['1041'],
    'coup': ['195','194','1724','012','092','0831','112','133','141','160','170','173'],
    'democratization': ['0343','0351','0353','063','081','0811','0812','0813','0814',
                        '083','0833','0841','0842','091','092','1052','1051'],
    'deteriorating_bilateral_relations': ['130','131','1311','1312','1313','132','138',
                                          '1382','1383','1384','139','160','161','162',
                                          '1621','1622','1623','163'],
    'dispute_settlement': ['036','037','038','039','086','0861','0862','0863',
                           '1056','1055','106','107','108'],
    'domestic_violence': ['180','183','1831','1832','1833','1834','185','186','200',
                          '201','202','203','204','145','1451','1453','1454'],
    'ethnic_religious_violence': ['1122','1123','1124','1233','1243','1453','1711',
                                  '1712','1721','1724','173','174','175','200','201','203'],
    'government_instability': ['012','104','1041','1042','1043','1051','1052','1053',
                               '1054','111','1121','1122','1123','1125','114','116','113',
                               '123','1231','1241','1233','1232','1242','1243','1411','1321',
                               '1322','1323','1324','137','140','1412','1413','1421','1422',
                               '1423','1431','1432','1433','153','151','1711','1712','1721',
                               '1722','1723','1724','173','174','175','176','180','1822',
                               '1831','1832','1833','1834','185','186'],
    'impose_curfew': ['1723'],
    'imposing_state_of_emergency': ['1724'],
    'increasing_international_financial_support': ['013','0311','0331','0354','061',
                                                   '071','085','1031'],
    'increasing_bilateral_relations': ['021','0211','0212','0213','0214','022','0234',
                                       '030','0311','0312','0314','032','0331','0332',
                                       '0333','0334','037','050','060','061','063','064',
                                       '071','072','074'],
    'instability': ['1724','1723','1722','1721','172','1324','1323','1322','1321',
                    '132','1041','0831','0832'],
    'institutional_strength': ['0343','034','0833'],
    'international_crisis': ['1311','1312','1313','134','135','136','125','126',
                             '127','129','1244','1245'],
    'international_support': ['013','018','019','030','031','0311','0312','0313',
                              '0314','032','033','0331','0332','0333','0334','039',
                              '041','043','050','051','052','053','054','057','060',
                              '061','062','063','064','071','072'],
    'leadership_change': ['0831'],
    'mass_killing': ['202'],
    'military_clash': ['202','203','196','194','193','192','191','190','1246',
                       '0874','0873','0871','087'],
    'military_crisis': ['155','154','153','152','151','150','138','1381','1382',
                        '1383','1384','1385'],
    'military_deescalation': ['087','0871','0872','0873','0874','0312','0356','1056'],
    'military_escalation': ['138','1381','1382','1383','1384','1385','139','152',
                            '153','154','155','161','180','190','191','192','193',
                            '194','195','1951','1952','196'],
    'opposition_activeness': ['133','140','1413','1412','1411','1421','1422','1423'],
    'political_crisis': ['133','137'],
    'political_dissent': ['133','140'],
    'political_instability': ['1822','185','186','012','111','112','1121','1122',
                              '1123','1124','1125','024','0241','0242','0243','0244',
                              '113','114','115','116','123','1231','1232','1233','1234',
                              '1241','1242','1243','1244','1245','1246','132','1321',
                              '1322','1323','1324','133','137','140','141','1411','1412',
                              '1413','1414','142','1421','1422','1423','1424','143','144',
                              '145','1451','1452','1453','1454','151','153','1711','172',
                              '1721','1722','1723','1724','173','174','175','176'],
    'political_stability': ['013','085','0341','081','0811','0812','0813','0814',
                            '0252','0342','0343','0344','082','0831','0832','0833','0834'],
    'protest': ['140','141','1411','1412','1413','1414','143','1431','1432','1433',
                '1434','144','1441','1442','1443','1444','145','1451','1452','1453','1454'],
    'regime_instability': ['012','0344','1044','1124','1234','1312','1313','1414',
                           '1424','1434','145','1451','1452','1453','1454','151','152',
                           '153','154','201','202','203','1724','1723'],
    'political_repression': ['1223','123','1231','1232','1233','1241','1243','128',
                             '132','1321','1322','1324','137','153','171','1711','1712',
                             '172','1721','1722','1724','173','174','175','1822','203','201'],
    'terrorism': ['186','185','1834','1833','1832','1831','183','180'],
    'threaten_in_international_relations': ['138','1382','1383','1384','1312','1313'],
    'torture': ['1822'],
    'mass_expulsion': ['201'],
    'repression_tactics': ['175'],
    'pressure_to_political_parties': ['1722'],
    'authoritarianism': ['1721'],
    'confiscate_property': ['171'],
    'human_rights_abuses': ['1122'],
    'corruption': ['1121'],
}

COUNTRY_CODES = {
    'AF':'Afghanistan','AR':'Argentina','AM':'Armenia','AS':'Australia',
    'BE':'Belgium','BR':'Brazil','CA':'Canada','CH':'China','CO':'Colombia',
    'DA':'Denmark','EG':'Egypt','ET':'Ethiopia','FR':'France','GZ':'Gaza Strip',
    'GM':'Germany','GH':'Ghana','GR':'Greece','HK':'Hong Kong','IC':'Iceland',
    'IN':'India','ID':'Indonesia','IR':'Iran','IZ':'Iraq','IS':'Israel',
    'IT':'Italy','JM':'Jamaica','JA':'Japan','JO':'Jordan','KZ':'Kazakhstan',
    'KE':'Kenya','KU':'Kuwait','KG':'Kyrgyzstan','LE':'Lebanon','MY':'Malaysia',
    'MX':'Mexico','NL':'Netherlands','NG':'Niger','NI':'Nigeria','KN':'North Korea',
    'NO':'Norway','PK':'Pakistan','RP':'Philippines','PO':'Portugal','RQ':'Puerto Rico',
    'QA':'Qatar','RS':'Russia','SA':'Saudi Arabia','SO':'Somalia','SF':'South Africa',
    'KS':'South Korea','SP':'Spain','SW':'Sweden','SZ':'Switzerland','SY':'Syria',
    'TU':'Turkey','UP':'Ukraine','AE':'United Arab Emirates','UK':'United Kingdom',
    'US':'United States','YM':'Yemen',
}

# ============================================================
# ÇEKIRDEK FONKSİYONLAR
# ============================================================

def download_gdelt_day(filename):
    """Tek bir günün GDELT verisini indir. Hata varsa yeniden dene."""
    url = f"http://data.gdeltproject.org/events/{filename}.export.CSV.zip"
    for attempt in range(RETRY_COUNT):
        try:
            resp = urlopen(url, timeout=60)
            zipfile = ZipFile(BytesIO(resp.read()))
            df = pd.read_csv(
                zipfile.open(f'{filename}.export.CSV'),
                sep='\t', header=None, names=V2HEADERS,
                usecols=SELECTED_COLUMNS,
                dtype={'CAMEOCode': str},
                low_memory=False
            )
            return filename, df
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return filename, None
            print(f"  [!] HTTP {e.code} — {filename} (deneme {attempt+1}/{RETRY_COUNT})")
        except Exception as e:
            print(f"  [!] Hata — {filename}: {e} (deneme {attempt+1}/{RETRY_COUNT})")
        if attempt < RETRY_COUNT - 1:
            time.sleep(RETRY_DELAY)
    return filename, None


def compute_day_indices(df):
    """
    V3 — Sentiment-Weighted Index

    Formül:
      Skor = Σ(NumMentions × |AvgTone|/100 × |Goldstein|/10)  [eşleşen]
             ─────────────────────────────────────────────────
             Σ(NumMentions)                                     [tüm olaylar]

    Sıfır bölme ve eksik veri koruması dahil.
    """
    if df is None or len(df) == 0:
        return None

    # Eksik değerleri doldur
    df = df.copy()
    df['NumMentions'] = pd.to_numeric(df['NumMentions'], errors='coerce').fillna(1).clip(lower=1)
    df['Goldstein']   = pd.to_numeric(df['Goldstein'],   errors='coerce').fillna(0)
    df['AvgTone']     = pd.to_numeric(df['AvgTone'],     errors='coerce').fillna(0)

    # Tüm günün toplam medya ağırlığı (payda)
    total_weight = df['NumMentions'].sum()
    if total_weight == 0:
        return None

    # Duygu yoğunluğu: 0–1 arası
    # |AvgTone|/100 → medya tonunun şiddeti
    # |Goldstein|/10 → olayın doğasındaki şiddet
    df['intensity'] = (df['AvgTone'].abs() / 100) * (df['Goldstein'].abs() / 10)

    # Ağırlıklı katkı = medya önem × duygu yoğunluğu
    df['weighted_contribution'] = df['NumMentions'] * df['intensity']

    results = {}

    for cont in COUNTRY_CODES:
        # Ülke maskesi
        country_mask = (
            (df['ActionGeo_CountryCode'] == cont) |
            (df['Actor1Geo_CountryCode'] == cont)  |
            (df['Actor2Geo_CountryCode'] == cont)
        )
        country_df = df[country_mask]
        if len(country_df) == 0:
            for topic in TOPICS:
                results[(topic, cont)] = 0.0
            continue

        country_cameo = country_df['CAMEOCode']

        for topic, codes in TOPICS.items():
            topic_mask = country_cameo.isin(codes)
            matched = country_df[topic_mask]

            if len(matched) == 0:
                results[(topic, cont)] = 0.0
            else:
                # Payı: eşleşen olayların ağırlıklı duygu katkısı
                numerator = matched['weighted_contribution'].sum()
                results[(topic, cont)] = numerator / total_weight

    return results


def load_existing_indices(filepath):
    if os.path.exists(filepath):
        print(f"Mevcut indeks dosyası bulundu: {filepath}")
        df = pd.read_csv(filepath, sep=',', header=0, index_col=[0, 1])
        print(f"  → {len(df.columns)} gün yüklendi.")
        return df
    else:
        print("Yeni başlanıyor (mevcut dosya bulunamadı).")
        idx = pd.MultiIndex.from_product(
            [TOPICS.keys(), COUNTRY_CODES.keys()],
            names=['topic', 'country']
        )
        return pd.DataFrame(index=idx)


def get_missing_dates(indices):
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    if len(indices.columns) == 0:
        start = yesterday - datetime.timedelta(days=30)
        print("⚠ İlk çalıştırma: son 30 gün indirilecek.")
    else:
        last = str(indices.columns[-1])
        start = datetime.datetime.strptime(last, '%Y%m%d') + datetime.timedelta(days=1)

    date_list = []
    cur = start
    while cur <= yesterday:
        date_list.append(int(cur.strftime('%Y%m%d')))
        cur += datetime.timedelta(days=1)
    return sorted(date_list)


# ============================================================
# ANA FONKSİYON
# ============================================================
def run():
    print("=" * 60)
    print("GDELT INDEX GENERATOR v3.0  (Sentiment-Weighted)")
    print("=" * 60)
    print("Formül: Σ(NumMentions × |AvgTone|/100 × |Goldstein|/10)")
    print("=" * 60)

    indices = load_existing_indices(OUTPUT_FILE)
    date_list = get_missing_dates(indices)

    if not date_list:
        print("\n✓ Tüm veriler güncel.")
        return indices

    print(f"\n{len(date_list)} gün indirilecek: {date_list[0]} → {date_list[-1]}")
    print(f"Paralel worker: {MAX_WORKERS}\n")

    success, skipped, total = 0, 0, len(date_list)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_gdelt_day, d): d for d in date_list}
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            filename, df = future.result()
            if df is not None:
                day_results = compute_day_indices(df)
                if day_results:
                    indices[str(filename)] = pd.Series(day_results)
                    success += 1
                    print(f"  [{i:>4}/{total}] ✓ {filename}  ({len(df):,} olay)")
                else:
                    skipped += 1
            else:
                skipped += 1
                print(f"  [{i:>4}/{total}] ✗ {filename}  (atlandı)")

            if i % 10 == 0:
                indices.to_csv(OUTPUT_FILE)
                print(f"  → Ara kayıt ({i}/{total})")

    indices = indices.reindex(sorted(indices.columns), axis=1)
    indices.to_csv(OUTPUT_FILE)

    print("\n" + "=" * 60)
    print(f"✓ Tamamlandı! Başarılı: {success}  Atlanan: {skipped}")
    print(f"  Toplam: {len(indices.columns)} gün × {len(indices):,} (konu×ülke)")
    print(f"  Kayıt: {OUTPUT_FILE}")
    print("=" * 60)
    return indices


if __name__ == '__main__':
    run()