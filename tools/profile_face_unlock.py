import cv2
import numpy as np
import mediapipe as mp
from pathlib import Path
from livekit.agents import function_tool

KNOWN_DIR = Path("data/face_encodings")
mp_solutions = getattr(mp, "solutions", None)
mp_face_mesh = getattr(mp_solutions, "face_mesh", None) if mp_solutions else None


def get_face_embedding(image):
    if mp_face_mesh is None:
        return None
    with mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=1,
        refine_landmarks=True
    ) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            return None

        landmarks = results.multi_face_landmarks[0].landmark
        points = np.array([[lm.x, lm.y, lm.z] for lm in landmarks], dtype=np.float32)
        return points.flatten()


def load_known_encodings():
    encodings = []
    names = []

    for img in KNOWN_DIR.glob("*.jpg"):
        img_data = cv2.imread(str(img))
        emb = get_face_embedding(img_data)

        if emb is not None:
            encodings.append(emb)
            names.append(img.stem)

    return encodings, names


def compare_embeddings(e1, e2, threshold=0.09):
    if e1 is None or e2 is None:
        return False

    dist = np.linalg.norm(e1 - e2)
    return dist < threshold


@function_tool
async def profile_face_unlock_tool(action: str) -> str:
    if action != "scan":
        return "Use: scan"

    known_encodings, known_names = load_known_encodings()

    if not known_encodings:
        return "⚠ No saved face images in data/face_encodings/"

    cam = cv2.VideoCapture(0)
    ok, frame = cam.read()
    cam.release()

    if not ok:
        return "❌ Could not access camera"

    emb = get_face_embedding(frame)
    if emb is None:
        return "😶 Face not detected properly"

    for known_emb, name in zip(known_encodings, known_names):
        if compare_embeddings(emb, known_emb):
            return f"🔓 Face recognized → {name}"

    return "❌ Face not recognized"
