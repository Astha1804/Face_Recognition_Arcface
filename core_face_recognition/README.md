• Core Face Recognition Engine:

This module implements a complete ArcFace-based face recognition pipeline, including:
-Dataset-based embedding generation
-Persistent CSV embedding storage
-Cosine similarity matching
-Threshold-based unknown face rejection
-Offline evaluation (accuracy + confidence)
-Real-time webcam face recognition

• This module acts as the base engine for multiple applications, including attendance systems and access control.

How to Run:
```bash
python face_recognition.py

# Configuration:
threshold = 0.5

• Author
Astha Dubey