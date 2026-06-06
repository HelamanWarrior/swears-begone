import os
import sys

from swears_begone.cli import main

def patch_cuda_paths():
    """Dynamically add pip-installed NVIDIA libraries to the loading path."""
    if not sys.platform.startswith("linux"):
        return
    
    import site

    paths = site.getsitepackages()
    if hasattr(site, 'getusersitepackages'):
        paths.append(site.getusersitepackages())
    
    cuda_libs = []
    for base_path in paths:
        # Check for the local nvidia libraries
        cublas_path = os.path.join(base_path, "nvidia", "cublas", "lib")
        cudnn_path = os.path.join(base_path, "nvidia", "cudnn", "lib")

        if os.path.exists(cublas_path):
            cuda_libs.append(cublas_path)
        if os.path.exists(cudnn_path):
            cuda_libs.append(cudnn_path)
    
    if cuda_libs:
        # Safely prepend to existing LD_LIBRARY_PATH
        existing = os.environ.get("LD_LIBRARY_PATH", "")
        prefix = ":".join(cuda_libs)
        os.environ["LD_LIBRARY_PATH"] = f"{prefix}:{existing}" if existing else prefix

if __name__ == "__main__":
    patch_cuda_paths()
    main()
