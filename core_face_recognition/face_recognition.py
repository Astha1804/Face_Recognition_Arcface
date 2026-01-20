import os
import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# CONFIGURATIONS
dataset_path = "data/Faces"
test_image_path = "data/test.jpg"
csv_output_path = "face_embeddings.csv"
threshold = 0.5

# Initialize ArcFace
print("Initializing ArcFace...")
app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0)

# Generate Embeddings from Dataset
print("\n Generating embeddings from dataset...")
data = []
image_paths = []

for root, _, files in os.walk(dataset_path):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_paths.append(os.path.join(root, file))

print(f"Found {len(image_paths)} images.")

for path in tqdm(image_paths):
    img = cv2.imread(path)
    if img is None:
        print(f"Could not read: {path}")
        continue

    faces = app.get(img)
    if faces and hasattr(faces[0], 'embedding'):
        emb = faces[0].embedding
    else:
        try:
            resized = cv2.resize(img, (112, 112))
            emb = app.models['recognition'].get_feat(resized).flatten()
        except:
            print(f"Failed to embed: {path}")
            continue

    label = os.path.basename(os.path.dirname(path))  # folder = name_roll
    data.append([label, path] + emb.tolist())

if data:
    df = pd.DataFrame(data)
    df.columns = ['name_roll', 'image_path'] + [f'emb_{i}' for i in range(len(data[0]) - 2)]
    df.to_csv(csv_output_path, index=False)
    print(f"Saved embeddings to {csv_output_path}")
else:
    print("No embeddings generated. Exiting.")
    exit()

# Test on Single Image
print("\n Testing with a single image...")
df = pd.read_csv(csv_output_path)
labels = df['name_roll'].tolist()
embeddings = df.drop(columns=['name_roll', 'image_path']).values

img = cv2.imread(test_image_path)
if img is None:
    print(" Could not read test image.")
else:
    faces = app.get(img)
    if faces and hasattr(faces[0], 'embedding'):
        test_emb = faces[0].embedding
        print(" Face embedded using ArcFace.")
    else:
        resized = cv2.resize(img, (112, 112))
        test_emb = app.models['recognition'].get_feat(resized).flatten()
        print(" ArcFace failed; fallback embedding used.")

    sims = cosine_similarity([test_emb], embeddings)[0]
    best_idx = np.argmax(sims)
    confidence = sims[best_idx]

    if confidence > threshold:
        print(f" Match found: {labels[best_idx]} ({confidence*100:.2f}%)")
    else:
        print(f" No confident match (confidence: {confidence*100:.2f}%)")

#  Train-Test Accuracy Report
print("\n Performing Train-Test Evaluation...")
X = df.drop(columns=['name_roll', 'image_path']).values
y = df['name_roll'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
y_pred, confidence_scores = [], []

for test_emb in X_test:
    sims = cosine_similarity([test_emb], X_train)[0]
    best_idx = np.argmax(sims)
    y_pred.append(y_train[best_idx])
    confidence_scores.append(sims[best_idx])

accuracy = accuracy_score(y_test, y_pred)
avg_confidence = np.mean(confidence_scores)
print(f"Accuracy: {accuracy*100:.2f}%")
print(f"Average Confidence: {avg_confidence*100:.2f}%")

# STEP 4: Real-Time Webcam Face Recognition
print("\n Starting real-time face recognition. Press 'q' to exit.")
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Checking camera setup
if not cap.isOpened():
    print("Webcam could not be opened.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame.")
        break

    faces = app.get(frame)

    for face in faces:
        if hasattr(face, 'embedding'):
            test_emb = face.embedding
            sims = cosine_similarity([test_emb], embeddings)[0]
            best_idx = np.argmax(sims)
            confidence = sims[best_idx]

            box = face.bbox.astype(int)
            x1, y1, x2, y2 = box

            if confidence > threshold:
                name = labels[best_idx]
                color = (0, 255, 0)
                label = f"{name} ({confidence*100:.2f}%)"
            else:
                color = (0, 0, 255)
                label = f"Unknown ({confidence*100:.2f}%)"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow("Real-time Face Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
