import os
import zipfile
import tempfile
from pathlib import Path

try:
    import streamlit as st
    import gdown
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    class MockStreamlit:
        def progress(self, value): return self
        def text(self, text): pass
        def empty(self): return self
        def info(self, text): print(f"INFO: {text}")
        def warning(self, text): print(f"WARNING: {text}")
        def error(self, text): print(f"ERROR: {text}")
        def success(self, text): print(f"SUCCESS: {text}")
        def markdown(self, text): print(text)
        def spinner(self, text): return self
        def balloons(self): pass
        def rerun(self): pass
        def cache_resource(self, func): return func
        def __enter__(self): return self
        def __exit__(self, *args): pass
    st = MockStreamlit()
    try:
        import gdown
    except ImportError:
        gdown = None


def download_spice_from_gdrive():
    """Download SPICE folder from Google Drive"""
    if not gdown:
        st.error("gdown package not available for Google Drive downloads")
        return False

    base_dir = Path(__file__).parent
    spice_dir = base_dir / "SPICE-1.0"

    gdrive_folder_url = os.getenv("GDRIVE_FOLDER_URL")

    try:
        with st.spinner("📥 Downloading SPICE files from Google Drive..."):
            gdown.download_folder(gdrive_folder_url, output=str(base_dir), quiet=False, use_cookies=False)

        if (spice_dir / "spice-1.0.jar").exists():
            st.success("✅ SPICE files downloaded successfully!")
            st.balloons()
            return True
        else:
            st.error("❌ Download completed but SPICE jar not found")
            return False

    except Exception as e:
        st.error(f"❌ Failed to download from Google Drive: {e}")
        return False


@st.cache_resource
def ensure_spice_files():
    """Download SPICE files if they don't exist"""
    base_dir = Path(__file__).parent
    spice_jar = base_dir / "SPICE-1.0" / "spice-1.0.jar"

    if spice_jar.exists():
        return True

    st.info("🔄 First time setup: Downloading SPICE evaluation files...")

    if download_spice_from_gdrive():
        if STREAMLIT_AVAILABLE:
            st.rerun()
        return True
    else:
        st.error("❌ Failed to download SPICE files")
        st.markdown("""
        **Manual Setup Required:**
        1. Download SPICE-1.0 from: https://drive.google.com/drive/folders/116BLLHsvg8z7i8gMZWcU3-VPx6g3dgWA
        2. Extract to project directory
        3. Refresh this page
        """)
        return False


def check_spice_availability():
    """Check if SPICE files are available without downloading"""
    base_dir = Path(__file__).parent
    spice_jar = base_dir / "SPICE-1.0" / "spice-1.0.jar"
    return spice_jar.exists()
