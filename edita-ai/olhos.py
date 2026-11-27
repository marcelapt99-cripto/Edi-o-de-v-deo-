import sys, cv2, json, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path='/home/user/edita-ai/face_landmarker.task'), num_faces=1))
out = {}
for f in sys.argv[1:]:
    cap = cv2.VideoCapture(f); i = 0; res = []
    while True:
        ok, fr = cap.read()
        if not ok: break
        r = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)))
        if r.face_landmarks:
            L = r.face_landmarks[0]; h, w = fr.shape[:2]
            le = ((L[33].x + L[133].x) / 2 * w, (L[33].y + L[133].y) / 2 * h)
            re = ((L[362].x + L[263].x) / 2 * w, (L[362].y + L[263].y) / 2 * h)
            # abertura do olho (pálpebra)
            op = (abs(L[159].y - L[145].y) + abs(L[386].y - L[374].y)) / 2 * h
            res.append([i, round(le[0]), round(le[1]), round(re[0]), round(re[1]), round(op, 1)])
        else: res.append([i, None])
        i += 1
    out[f] = res
json.dump(out, open('olhos.json', 'w'))
for f, res in out.items():
    print(f, len(res)); [print(' ', r) for r in res[::6]]
