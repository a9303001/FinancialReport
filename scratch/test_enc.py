import csv, os

def test_enc(filename):
    filepath = os.path.join('StkScreenerResult', filename)
    for enc in ['utf-8-sig', 'utf-8', 'cp950', 'gbk']:
        try:
            with open(filepath, encoding=enc) as f:
                reader = list(csv.reader(f))
                print(f"{filename} with {enc}: Success! Header: {reader[0][:4]}, Row 1: {reader[1][:4]}")
                return enc
        except Exception as e:
            pass

test_enc('TW.csv')
test_enc('US.csv')
test_enc('hk.csv')
test_enc('jp.csv')
