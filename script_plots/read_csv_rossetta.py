import json
import os
import sys
import pandas as pd
import numpy as np

# Filter out libsodium in CROW paper
BLACKLIST = [
    "salsa20_xmm6int-sse2.variants.csv", 
    "all5.variants.csv", 
    "crypto_shorthash.variants.csv" , 
    "hash_sha256_cp.variants.csv"
    "scalarmult_ristretto255_ref10.variants.csv",
    "aead_xchacha20poly1305.variants.csv",
    "kdf_blake2b.variants.csv",
    "open.variants.csv",
    "aead_aes256gcm_aesni.variants.csv",
    "crypto_box_easy.variants.csv",
    "poly1305_donna.variants.csv",
    "core_hsalsa20_ref2.variants.csv",
    "salsa20_xmm6int-avx2.variants.csv",
    "ed25519_ref10.variants.csv",
    "core_hsalsa20.variants.csv",
    "crypto_stream.variants.csv",
    "crypto_kdf.variants.csv",
    "crypto_pwhash.variants.csv",
    "box_seal_curve25519xchacha20poly1305.variants.csv",
    "verify.variants.csv",


    #"Multiplication_tables.variants.csv",
    #"Base64_decode_data.variants.csv",
    #"Run-length_encoding.variants.csv",
    #"Validate_International_Securities_Identification_Number.variants.csv",
    #"Numerical_integration-Gauss-Legendre_Quadrature.variants.csv"
    ]

if __name__ == '__main__':
    folder = sys.argv[1]

    OVERALL = {}
    CUMULT = []
    CUMULU = []
    COUNT = 0
    files= os.listdir(folder)
    for i, csv in enumerate(files):

        if csv.endswith(".csv") and csv not in BLACKLIST:
            frame = pd.read_csv(f"{folder}/{csv}")
            
            items = []
            values = []
            names = []
            for index, t in frame.iterrows():
                # Data sanitization and deduplication
                if "~" not in t['name'] and t['name'] not in names:
                    values.append(t[' hash'])
                    names.append(t['name'])


            T = len(values)
            U = len(set(values))

            if T > 1:
                OVERALL[csv] = dict(
                    total=T,
                    unique=U
                )
                CUMULT.append(T - 1) # T and U are only based on the the variants
                CUMULU.append(U-1) # remove the original
                COUNT += 1

                

                print(f"{i}/{len(files)}",csv, "Real", len(frame['name'].values), "Final", len(values), "U", U, sum(CUMULT), sum(CUMULU), COUNT)

                if U > 99:
                    #input()
                    pass

    OVERALL["Total"] = sum(CUMULT)
    OVERALL["Unique"] = sum(CUMULU)
    OVERALL["UniqueAvg"] = np.mean(CUMULU)
    OVERALL["TotalAvg"] = np.mean(CUMULT)
    OVERALL["UniqueMedian"] = np.median(CUMULU)
    OVERALL["TotalMedian"] = np.median(CUMULT)

    open(sys.argv[2], 'w').write(json.dumps(OVERALL, indent=4))