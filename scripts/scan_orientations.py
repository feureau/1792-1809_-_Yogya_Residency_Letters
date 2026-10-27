import os
import cv2
import numpy as np
import json

def detect_line_angles(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None, 0, 0, 0
    h, w = img.shape
    scale = 1000 / max(h, w)
    small = cv2.resize(img, (int(w * scale), int(h * scale)))
    
    # We want to focus on the central 80% to avoid outer page borders/table surface
    sh, sw = small.shape
    crop = small[int(sh*0.1):int(sh*0.9), int(sw*0.1):int(sw*0.9)]
    
    edges = cv2.Canny(crop, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=50, maxLineGap=10)
    
    if lines is None:
        return 'No lines', 0, 0, 0
    
    horiz_count = 0
    vert_count = 0
    for l in lines:
        pts = l.flatten()
        x1, y1, x2, y2 = pts[0], pts[1], pts[2], pts[3]
        angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi)
        if angle < 15 or angle > 165:
            horiz_count += 1
        elif 75 < angle < 105:
            vert_count += 1
            
    ratio = (horiz_count + 1) / (vert_count + 1)
    return 'ok', horiz_count, vert_count, ratio

def main():
    results = []
    
    # Check Cover
    cover_files = sorted([os.path.join('Cover/jpg', f) for f in os.listdir('Cover/jpg') if f.lower().endswith('.jpg')])
    jpg_files = sorted([os.path.join('jpg', f) for f in os.listdir('jpg') if f.lower().endswith('.jpg')])
    
    all_files = cover_files + jpg_files
    print(f"Scanning {len(all_files)} images...")
    
    suspicious = []
    for idx, path in enumerate(all_files):
        status, h, v, r = detect_line_angles(path)
        if r < 1.5 or status == 'No lines':
            suspicious.append({
                'path': path,
                'status': status,
                'horiz': h,
                'vert': v,
                'ratio': round(r, 3)
            })
        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1}/{len(all_files)}...")
            
    print(f"\nDone! Found {len(suspicious)} suspicious/low-ratio images:")
    for s in suspicious:
        print(f"  {s['path']}: Horiz={s['horiz']}, Vert={s['vert']}, Ratio={s['ratio']}")
        
    with open('scripts/suspicious_orientations.json', 'w', encoding='utf-8') as out:
        json.dump(suspicious, out, indent=2)

if __name__ == '__main__':
    main()
