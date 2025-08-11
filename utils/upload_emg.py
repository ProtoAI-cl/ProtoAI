import os
import sys

import firebase_admin
import scipy.io
from firebase_admin import credentials, firestore

cred = credentials.Certificate("credentials/credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

DATASETS = {
    "db1": {
        "folder": "./utils/ninaproDB1",
        "collection": "emg_signals",
        "source": "DB1",
    },
    "db2": {
        "folder": "./utils/ninaproDB2",
        "collection": "emg_signals_db2",
        "source": "DB2",
    },
}

dataset_key = sys.argv[1] if len(sys.argv) > 1 else "db1"
if dataset_key not in DATASETS:
    print(
        f"❌ Dataset '{dataset_key}' is not supported. Use one of: {list(DATASETS.keys())}"
    )
    sys.exit(1)

folder_path = DATASETS[dataset_key]["folder"]
COLLECTION_NAME = DATASETS[dataset_key]["collection"]
SOURCE = DATASETS[dataset_key]["source"]

for filename in os.listdir(folder_path):
    if filename.endswith(".mat"):
        mat_path = os.path.join(folder_path, filename)

        try:
            data = scipy.io.loadmat(mat_path)

            subject = filename.split("_")[0].replace("S", "")
            exercise = filename.split("_")[2].replace(".mat", "")

            emg = data.get("emg")
            glove = data.get("glove")
            force = data.get("force")
            stimulus = data.get("stimulus")
            restimulus = data.get("restimulus")

            emg_trunc = emg[:100] if emg is not None else None
            glove_trunc = glove[:100] if glove is not None else None
            force_trunc = force[:100] if force is not None else None

            emg_by_channel = (
                {f"ch{i}": emg_trunc[:, i].tolist() for i in range(emg_trunc.shape[1])}
                if emg_trunc is not None
                else {}
            )

            glove_by_sensor = (
                {
                    f"sensor{i}": glove_trunc[:, i].tolist()
                    for i in range(glove_trunc.shape[1])
                }
                if glove_trunc is not None
                else {}
            )

            force_by_channel = (
                {
                    f"f{i}": force_trunc[:, i].tolist()
                    for i in range(force_trunc.shape[1])
                }
                if force_trunc is not None
                else {}
            )

            doc_data = {
                "subject": f"S{subject}",
                "exercise": f"E{exercise}",
                "shape": list(emg.shape) if emg is not None else [],
                "emg_by_channel": emg_by_channel,
                "glove": glove_by_sensor,
                "force": force_by_channel,
                "stimulus": (
                    stimulus[:100].flatten().tolist() if stimulus is not None else []
                ),
                "restimulus": (
                    restimulus[:100].flatten().tolist()
                    if restimulus is not None
                    else []
                ),
                "source": SOURCE,
            }

            doc_id = filename.replace(".mat", "")
            db.collection(COLLECTION_NAME).document(doc_id).set(doc_data)
            print(f"✅ Uploaded: {doc_id}")

        except Exception as e:
            print(f"❌ Error with {filename}: {e}")
