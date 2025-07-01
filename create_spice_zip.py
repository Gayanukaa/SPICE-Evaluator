import zipfile
import os
from pathlib import Path

def create_spice_zip():
    """Create a ZIP file from the SPICE-1.0 folder"""
    base_dir = Path(__file__).parent
    spice_dir = base_dir / "SPICE-1.0"
    zip_path = base_dir / "SPICE-1.0.zip"

    if not spice_dir.exists():
        print("❌ SPICE-1.0 folder not found!")
        return False

    print("📦 Creating SPICE-1.0.zip...")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(spice_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(base_dir)
                zipf.write(file_path, arcname)
                print(f"Added: {arcname}")

    print(f"✅ Created {zip_path}")
    print(f"📏 Size: {zip_path.stat().st_size / (1024*1024):.1f} MB")

    return True

if __name__ == "__main__":
    create_spice_zip()
