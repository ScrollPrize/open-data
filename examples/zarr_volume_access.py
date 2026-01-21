#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "zarr>=2.16.0",
#     "fsspec>=2023.1.0",
#     "s3fs>=2023.1.0",
#     "matplotlib>=3.7.0",
#     "tifffile>=2023.7.0",
#     "numpy>=1.24.0",
#     "imagecodecs"
# ]
# ///
"""
Example script for accessing Vesuvius Challenge open data from S3.

This script demonstrates how to:
- Access OME-ZARR volumes from S3
- Read different resolution levels
- Visualize volume slices
- Read TIFF surface volumes from segments

Run with: uv run examples/zarr_volume_access.py
"""

import zarr
import fsspec
import matplotlib.pyplot as plt
import tifffile

# Configure S3 file system access
s3 = fsspec.filesystem('s3', anon=True)  # Public bucket; set anon=False if using credentials

# Open an OME-ZARR volume from S3
store = s3.get_mapper('s3://vesuvius-challenge-open-data/PHerc0332/volumes/20231201141544-3.240um-70keV-masked.zarr/')
root = zarr.open(store, mode='r')

# Access data at different resolution levels
level_0 = root['0']  # Highest resolution (full size)
level_1 = root['1']  # 2x downsampled
level_2 = root['2']  # 4x downsampled

print(f"Level 0 shape: {level_0.shape}")  # [z, y, x]
print(f"Level 1 shape: {level_1.shape}")
print(f"Level 2 shape: {level_2.shape}")

# Read a slice from level 1 (good balance of speed and detail)
slice_data = level_1[1000, :, :]

# Visualize the slice
plt.figure(figsize=(10, 10))
plt.imshow(slice_data, cmap='gray')
plt.title('Slice 1000 from Level 1')
plt.axis('off')
plt.savefig('volume_slice.png', dpi=150, bbox_inches='tight')
print("Saved volume_slice.png")
plt.show()

# For segment surface volumes (TIFF stacks), you can use tifffile:
# Read a specific layer from a surface volume
with s3.open('s3://vesuvius-challenge-open-data/PHerc0139/segments/20250731185658-z_dbg_gen_09900/surface-volumes/9.362um-1.2m-113keV-volume-20250728140407.tifs/00.tif', 'rb') as f:
    layer_0 = tifffile.imread(f)
    plt.figure(figsize=(10, 10))
    plt.imshow(layer_0, cmap='gray')
    plt.title('Surface layer 0')
    plt.axis('off')
    plt.savefig('surface_layer.png', dpi=150, bbox_inches='tight')
    print("Saved surface_layer.png")
    plt.show()
