import os
import sys
import ctypes

from swears_begone.cli import main

def patch_cuda_paths() -> None:
    """Dynamically add pip-installed NVIDIA libraries to the loading path."""
    if not sys.platform.startswith("linux"):
        return
    
    import site

    paths = site.getsitepackages()
    if hasattr(site, 'getusersitepackages'):
        paths.append(site.getusersitepackages())
    
    target_subdirs = [
        ("nvidia", "cublas", "lib"),
        ("nvidia", "cudnn", "lib")
    ]

    for base_path in paths:
        for subdir in target_subdirs:
            lib_dir = os.path.join(base_path, *subdir)

            if os.path.exists(lib_dir):
                for filename in os.listdir(lib_dir):
                    # Matches 'libcublas.so.X' or 'libcudnn.so.X'
                    if filename.startswith("lib") and ".so" in filename:
                        full_path = os.path.join(lib_dir, filename)
                        try:
                            # Load the binary globally in memory
                            ctypes.CDLL(full_path, mode=ctypes.RTLD_GLOBAL)
                        except Exception:
                            pass

patch_cuda_paths()

if __name__ == "__main__":
    main()
