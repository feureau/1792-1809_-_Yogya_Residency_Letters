"""Apply identified orientation corrections in-place to ensure all images in Cover/jpg and jpg/ are upright.
"""
import os
from PIL import Image

OPERATIONS = [
    ("Cover/jpg/IMG_0277.JPG", Image.ROTATE_180, "180 deg (invert ColorChecker)"),
    ("Cover/jpg/IMG_0278.JPG", Image.ROTATE_180, "180 deg (invert ColorChecker focus target)"),
    ("Cover/jpg/IMG_0279.JPG", Image.ROTATE_270, "90 deg CW (binder front cover)"),
    ("Cover/jpg/IMG_0283.JPG", Image.ROTATE_270, "90 deg CW (Carey manuscript index notes)"),
    ("Cover/jpg/IMG_0284.JPG", Image.ROTATE_270, "90 deg CW (Carey manuscript index notes verso)"),
    ("jpg/IMG_20260618_0109_rotated_180.jpg", Image.ROTATE_180, "180 deg (ANRI Djokjo Brieven 48 f.1)"),
    ("jpg/IMG_20260618_0110_rotated_180.jpg", Image.ROTATE_180, "180 deg (ANRI Djokjo Brieven 48 f.2)"),
    ("jpg/IMG_20260618_0111_rotated_180.jpg", Image.ROTATE_90, "90 deg CCW (ANRI Djokjo Brieven 48 f.3)"),
    ("jpg/IMG_20260619_0114.jpg", Image.ROTATE_90, "90 deg CCW (Daendels Plakaatboek pp. 62-63)"),
    ("jpg/IMG_20260619_0115.jpg", Image.ROTATE_270, "90 deg CW (Daendels Plakaatboek pp. 64-65)")
]

def apply_all():
    print(f"Applying orientation corrections to {len(OPERATIONS)} images...")
    for rel_path, rot_op, description in OPERATIONS:
        if not os.path.exists(rel_path):
            print(f"ERROR: File not found: {rel_path}")
            continue
        
        with Image.open(rel_path) as im:
            orig_size = im.size
            icc = im.info.get("icc_profile")
            exif = im.getexif()
            
            # Transpose pixels
            rotated = im.transpose(rot_op)
            
            # Ensure EXIF orientation is normalized (1 = Normal)
            if exif:
                exif[0x0112] = 1
                
            save_kwargs = {
                "quality": 95,
                "subsampling": 0
            }
            if icc:
                save_kwargs["icc_profile"] = icc
            if exif:
                save_kwargs["exif"] = exif
                
            temp_path = rel_path + ".tmp.jpg"
            rotated.save(temp_path, **save_kwargs)
            new_size = rotated.size
            
        os.replace(temp_path, rel_path)
        print(f"SUCCESS: {rel_path} | {orig_size} -> {new_size} | {description}")

if __name__ == "__main__":
    apply_all()
