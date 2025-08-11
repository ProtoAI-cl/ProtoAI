# Import necessary modules and dependencies
import logging
import os
import sys
import time
from typing import Optional, Tuple

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.firebase.firestore import FirestoreHandler
from models import ImageRequest
from openAI.client import OpenAIClient
from prompts.prompts import HAND_PROMPT_3, HAND_PROMPT_EMG_FUSION

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


# Load environment variables from .env file
logger.info("Looking for secrets")
load_dotenv()

# Initialize FastAPI application
app = FastAPI()

# Configure CORS middleware to allow all origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set model and API keys from environment variables
MODEL = "gpt-4.1-nano"
API_KEY = os.getenv("OPENAI_API_KEY")
RASP_API_URL = os.getenv("RASP_API_URL")

cliente_de_prueba = FirestoreHandler()


def get_emg_context(label_detected: str) -> Optional[Tuple[str, str]]:
    """
    Retrieve EMG signal context based on the detected object label.
    Returns a tuple containing the EMG context string and the sources used.
    """
    tag_to_exercise = {
        "bottle": ["E2", "EA1"],
        "cup": ["E3", "EA2"],
        "phone": ["E5", "EA5"],
    }

    label = label_detected.lower()
    matched_exercises = next(
        (e for k, e in tag_to_exercise.items() if k in label), None
    )

    if not matched_exercises:
        logger.warning(f"⚠️ No EMG mapping for label: '{label_detected}'")
        return None

    context_lines = []
    used_sources = set()

    # Iterate through EMG signal collections to find relevant data
    for collection_name in ["emg_signals", "emg_signals_db2"]:
        docs = cliente_de_prueba.db.collection(collection_name).stream()
        for doc in docs:
            emg_data = doc.to_dict()
            exercise_val = emg_data.get("exercise", "")
            if exercise_val not in matched_exercises:
                continue

            subject = emg_data.get("subject", "unknown")
            shape = emg_data.get("shape", [])
            emg_channels = emg_data.get("emg_by_channel", {})

            # Build a summary of available EMG channels
            all_channels = [
                f"ch{i}: {emg_channels.get(f'ch{i}', [])[:3]}"
                for i in range(len(emg_channels))
            ]
            context_lines.append(
                f"- {collection_name.upper()} / Subject {subject}, shape {shape}, "
                + " | ".join(all_channels)
            )
            used_sources.add(collection_name.upper())

    if not context_lines:
        logger.warning(f"⚠️ No EMG document found for exercises: {matched_exercises}")
        return None

    # Format EMG context string for further processing
    emg_context = (
        f"Exercises {', '.join(matched_exercises)} matched to the detected object.\n"
        "EMG signals were retrieved from the following sources:\n"
        + "\n".join(context_lines)
        + "\nUse this signal information to refine the hand movement instruction."
    )

    return emg_context, ", ".join(sorted(used_sources))


@app.get("/")
def ping():
    """
    Health check endpoint to verify server is running.
    """
    return {"response": "OK"}


@app.websocket("/ws")
async def websocket_server(websocket: WebSocket):
    """
    WebSocket endpoint to receive keypoints data from clients.
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received keypoints: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        await websocket.close()


@app.post("/upload-image")
def upload_image(request: ImageRequest):
    """
    Endpoint to process uploaded image, detect objects, suggest hand movements,
    and optionally fuse results with EMG signal data.
    """
    if not request.data:
        return {"error": "No image data provided."}

    selected_model = MODEL
    client = OpenAIClient(api_key=API_KEY)
    image_data = request.data
    start_time = time.time()

    # 1️⃣ Object detection using LLM
    detected_object_response = client.detect_object(selected_model, image_data)
    detected_object = client.extract_object_from_response(detected_object_response)
    logger.info(f"🧠 Detected object: '{detected_object}'")

    # 2️⃣ Suggest hand movement based on detected object
    suggested_movement_response = client.generate_suggested_movement(
        selected_model, detected_object
    )
    suggested_movement = client.extract_suggested_movement(suggested_movement_response)

    # 3️⃣ Generate standard hand movement instructions (vision only)
    vision_hand_response = client.generate_hand_movements(
        HAND_PROMPT_3, selected_model, image_data
    )
    cleaned_vision_response = vision_hand_response.strip()
    if not cleaned_vision_response.startswith("["):
        cleaned_vision_response = f"[{cleaned_vision_response}]"

    # 4️⃣ Save vision-only response to Firestore
    vision_result = {
        "hand_movements": cleaned_vision_response,
        "image_analysis": {
            "detected_object": detected_object,
            "suggested_movement": suggested_movement,
        },
        "provided_image": image_data,
        "llm_model": selected_model,
        "tags": [detected_object.lower(), selected_model],
        "processing_time_seconds": round(time.time() - start_time, 2),
    }
    cliente_de_prueba.save_to_firestore(vision_result, collection="responses")

    # 5️⃣ Attempt to generate fused response with EMG data
    emg_result_tuple = get_emg_context(detected_object)
    if emg_result_tuple:
        emg_context, emg_source = emg_result_tuple
        logger.info(f"✅ EMG sources used: {emg_source}")
        logger.info("🔬 EMG context retrieved. Generating fused response...")
        fusion_prompt = HAND_PROMPT_EMG_FUSION.replace("{EMG_CONTEXT}", emg_context)
        emg_response = client.generate_hand_movements(
            fusion_prompt, selected_model, image_data
        )
        cleaned_emg_response = emg_response.strip()
        if not cleaned_emg_response.startswith("["):
            cleaned_emg_response = f"[{cleaned_emg_response}]"

        emg_result = {
            "hand_movements": cleaned_emg_response,
            "image_analysis": {
                "detected_object": detected_object,
                "suggested_movement": suggested_movement,
                "emg_context": emg_context,
                "emg_source": emg_source,
            },
            "provided_image": image_data,
            "llm_model": selected_model,
            "tags": [detected_object.lower(), selected_model, emg_source, "fusion_emg"],
            "processing_time_seconds": round(time.time() - start_time, 2),
        }
        cliente_de_prueba.save_to_firestore(emg_result, collection="responses_emg_llm")
    else:
        logger.warning("🚫 No EMG fusion generated.")

    return {"status": "OK", "detected_object": detected_object}
