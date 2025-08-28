import cv2
import os
from deepface import DeepFace

def extract_frames(video_path, timestamps, out_dir="/tmp/frames"):
    os.makedirs(out_dir, exist_ok=True)
    vid = cv2.VideoCapture(video_path)
    fps = vid.get(cv2.CAP_PROP_FPS)
    frames = []
    for i, t in enumerate(timestamps):
        frame_no = int(t * fps)
        vid.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ret, frame = vid.read()
        if not ret:
            frames.append(None)
            continue
        fname = os.path.join(out_dir, f"frame_{i}.jpg")
        cv2.imwrite(fname, frame)
        frames.append(fname)
    vid.release()
    return frames

def guess_gender_from_frame(frame_path: str) -> str:
    try:
        analysis = DeepFace.analyze(frame_path, actions=["gender"], enforce_detection=False)
        if isinstance(analysis, list):
            analysis = analysis[0]
        gender = analysis.get("gender")
        if isinstance(gender, dict):
            male_score = gender.get("Man", 0)
            female_score = gender.get("Woman", 0)
            return "male" if male_score >= female_score else "female"
        if isinstance(gender, str):
            if "man" in gender.lower() or gender.lower().startswith("m"):
                return "male"
            if "woman" in gender.lower() or gender.lower().startswith("f"):
                return "female"
        return "unknown"
    except Exception as e:
        print("gender detect error:", e)
        return "unknown"
