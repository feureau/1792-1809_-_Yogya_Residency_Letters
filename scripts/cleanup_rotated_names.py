"""Clean up filenames across the repository by removing '_rotated_180'.
Resolves the IMG_20260619_0001 collision by renaming the calibration target to IMG_20260619_0000.
Updates data.json, transcription markdown files, and references.
"""
import os
import json
import re

def run_cleanup():
    print("Beginning filename cleanup...")
    
    # 1. Update data.json mapping
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. Step 1: Handle IMG_20260619_0001 (calibration target) -> IMG_20260619_0000
    target_img_old = 'jpg/IMG_20260619_0001.jpg'
    target_img_new = 'jpg/IMG_20260619_0000.jpg'
    target_md_old = 'transcription/IMG_20260619_0001.md'
    target_md_new = 'transcription/IMG_20260619_0000.md'

    if os.path.exists(target_img_old):
        os.rename(target_img_old, target_img_new)
        print(f"Renamed: {target_img_old} -> {target_img_new}")

    if os.path.exists(target_md_old):
        with open(target_md_old, 'r', encoding='utf-8') as f:
            c = f.read()
        # update references inside
        c = c.replace('IMG_20260619_0001.jpg', 'IMG_20260619_0000.jpg')
        c = c.replace('IMG_20260619_0001', 'IMG_20260619_0000')
        with open(target_md_new, 'w', encoding='utf-8') as f:
            f.write(c)
        os.remove(target_md_old)
        print(f"Renamed and updated: {target_md_old} -> {target_md_new}")

    # 3. Step 2: Handle all 270 _rotated_180 files in transcription/ and jpg/
    trans_files = sorted([f for f in os.listdir('transcription') if 'rotated_180' in f])
    print(f"Found {len(trans_files)} markdown files with 'rotated_180' to process.")

    for mf in trans_files:
        old_path = os.path.join('transcription', mf)
        new_name = mf.replace('_rotated_180', '')
        new_path = os.path.join('transcription', new_name)

        with open(old_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update title, image file, and header folio in content
        base_old = mf[:-3] # without .md
        base_new = new_name[:-3]
        content = content.replace(f"{base_old}.jpg", f"{base_new}.jpg")
        content = content.replace(base_old, base_new)
        content = content.replace('_rotated_180.jpg', '.jpg')
        content = content.replace('_rotated_180', '')

        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(content)

        os.remove(old_path)

    print(f"Successfully migrated {len(trans_files)} markdown files.")

    # Process jpg files
    jpg_files = sorted([f for f in os.listdir('jpg') if 'rotated_180' in f])
    print(f"Found {len(jpg_files)} image files with 'rotated_180' to process.")

    for jf in jpg_files:
        old_path = os.path.join('jpg', jf)
        new_name = jf.replace('_rotated_180', '')
        new_path = os.path.join('jpg', new_name)

        os.rename(old_path, new_path)

    print(f"Successfully renamed {len(jpg_files)} image files.")

    # 4. Update data.json
    new_data = []
    for d in data:
        item = dict(d)
        if item['id'] == 'IMG_20260619_0001':
            item['id'] = 'IMG_20260619_0000'
            item['image'] = 'jpg\\IMG_20260619_0000.jpg'
            item['text'] = 'transcription/IMG_20260619_0000.md'
        else:
            item['id'] = item['id'].replace('_rotated_180', '')
            item['image'] = item['image'].replace('_rotated_180', '')
            item['text'] = item['text'].replace('_rotated_180', '')
        new_data.append(item)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    print("Successfully updated data.json.")

    # 5. Update transcription_status.json
    if os.path.exists('transcription_status.json'):
        with open('transcription_status.json', 'r', encoding='utf-8') as f:
            ts = json.load(f)
        new_ts = {}
        for k, v in ts.items():
            k_new = k.replace('_rotated_180', '')
            v_new = dict(v)
            if 'target_file' in v_new:
                v_new['target_file'] = v_new['target_file'].replace('_rotated_180', '')
            new_ts[k_new] = v_new
        with open('transcription_status.json', 'w', encoding='utf-8') as f:
            json.dump(new_ts, f, indent=2, ensure_ascii=False)
        print("Successfully updated transcription_status.json.")

    # 6. Verification
    print("\nVerifying all entries in data.json exist on disk...")
    missing_images = 0
    missing_texts = 0
    for item in new_data:
        # Normalize path separators for checking
        img_check = item['image'].replace('\\', '/')
        txt_check = item['text'].replace('\\', '/')
        if not os.path.exists(img_check):
            print(f"MISSING IMAGE: {img_check}")
            missing_images += 1
        if not os.path.exists(txt_check):
            print(f"MISSING TEXT: {txt_check}")
            missing_texts += 1

    if missing_images == 0 and missing_texts == 0:
        print(f"VERIFICATION SUCCESSFUL: All {len(new_data)} items exist on disk with clean names!")
    else:
        print(f"VERIFICATION FAILED: {missing_images} missing images, {missing_texts} missing texts.")

if __name__ == '__main__':
    run_cleanup()
