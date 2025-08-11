import logging
import os
import sys
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from firebase_admin import credentials, firestore, initialize_app

load_dotenv()

# Load Firebase credentials from the environment variable
CRED_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


class FirestoreHandler:
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize Firestore client with credentials.

        Args:
            credentials_path: Path to Firebase credentials JSON file.
                             If None, uses FIREBASE_CREDENTIALS_PATH env var.
        """
        logger.info(f"retrieving the credentials from {CRED_PATH}")
        try:
            cred_path = credentials_path or CRED_PATH
            if not cred_path:
                error_message = "Firebase credentials path not provided"
                logger.error(error_message)
                raise ValueError(error_message)

            cred = credentials.Certificate(cred_path)
            initialize_app(cred)

            self.db = firestore.client()
            logger.info("✅ Firestore client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Error initializing Firestore: {e}")
            raise

    def save_to_firestore(self, data, collection="responses"):
        """
        Saves data to Firestore in the specified collection with tags and a custom doc ID.
        """
        try:
            detected_object = (
                data.get("image_analysis", {})
                .get("detected_object", "")
                .strip()
                .lower()
            )
            if not detected_object or detected_object == "unknown":
                detected_object = "unlabeled"

            existing_tags = data.get("tags", [])
            tags = set(existing_tags + [detected_object])  # evitar duplicados
            data["tags"] = list(tags)

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            doc_id = f"{detected_object}_{timestamp}"

            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.set(data)

            print(f"✅ Data saved with doc ID: {doc_id} in collection: {collection}")
        except Exception as e:
            print(f"❌ Error saving data to Firestore: {e}")
