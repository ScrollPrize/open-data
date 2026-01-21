# Vesuvius Challenge Open Data Documentation

## Overview

A vast library of papyrus scrolls in ancient Herculaneum was buried beneath twenty meters of volcanic mud and ash during the 79 AD eruption of Mount Vesuvius, carbonized into a fragile but miraculously preserved state. The Vesuvius Challenge uses micro‑CT imaging to study both intact Herculaneum scrolls and detached fragments. Our goal is to virtually unwrap the scrolls from their 3D X‑ray volumes and recover the text hidden inside the scrolls. Detached fragments contain exposed ink and provide ground truth for improving machine‑learning ink detection models.

X-ray scans were acquired at various resolutions and energy levels were performed at the Diamond Light Source DLS and European Synchrotron Radiation Facility (ESRF), producing volumetric datasets.

The Vesuvius Challenge Open Data repository provides access to X-ray scans, 3D volumes, segmented surfaces, and machine learning results for the Herculaneum papyri. This dataset supports researchers working on virtually unrolling and reading ancient carbonized scrolls from the Villa of the Papyri in Herculaneum.

See [scrollprize.org](https://scrollprize.org/) for more information about the Vesuvius Challenge.

## Pipeline and Artifacts

- Scan Acquisition: X-ray tomography scans of scrolls and fragments at synchrotron facilities leading to raw projection data (currently not shared)
- Volume Reconstruction: Conversion of raw projections into 3D volumetric datasets, these usually consist of 2D slices of tifs (currently not shared)
- Volume Masking and Export: Isolating the papyrus material from the background roughly, windowing the 16 bit intensities and exporting as 8-bit OME-Zarr arrays leading to _volumes_
- ML-based Surface Prediction: Using neural networks to predict papyrus surface locations within the volumes leading to _predicted surfaces_
- Segmentation and Surface Extraction: Identifying papyrus layers and extracting 3D surface meshes leading to _segments_
- Ink Detection: Applying machine learning models to identify ink patterns on the papyrus surfaces leading to _ink detection results_

## Data Organization

### Repository Structure

```
s3://vesuvius-challenge-open-data/
├── PHerc0332/
├── PHerc1667/
└── ...
```

#### Sample Data Structure

Each sample (e.g., `PHerc0332/`) contains:

```
PHerc0332/
├── volumes/          # 3D volumetric scan data
├── segments/         # Segmented papyrus surfaces
├── representations/  # Derived representations (e.g., predicted surfaces, ink detection)
|   ├── predictions/
|   |   ├── surfaces/ # Predicted papyrus surfaces
└── scans/            # Raw scan metadata (if available and shared)
```

#### Volumes

Volumes are 3D reconstructions of X-ray scans stored in OME-ZARR format.

**Directory structure:**

```
volumes/
└── {id}-{descriptive suffix}.zarr/
    ├── 0/            # Highest resolution level
    ├── 1/            # Downsampled level 1
    ├── 2/            # Downsampled level 2
    ├── ...           # Additional downsampled levels
    └── .zattrs       # OME-ZARR metadata
```

**Example:**

- `20231201141544-3.240um-70keV-masked.zarr` - 3.24µm resolution scan at 70keV, masked to show only papyrus

#### Segments

Segments represent extracted papyrus surfaces with mesh data, extracted surface volumes, and ink detection results.

**Directory structure:**

```
segments/
└── {id}-{suffix}/
    ├── mesh/
    │   ├── intermediate/
    │   │   ├── tifxyz_original/        # Original TIFXYZ coordinates
    │   │   ├── {id}_original.obj       # Original 3D mesh from volume
    │   │   ├── {id}_flattened.obj      # Flattened mesh
    │   │   └── {id}_normalized.obj     # Oriented and normalized mesh
    │   └── tifxyz/
    │       ├── x.tif                   # X coordinates for each pixel
    │       ├── y.tif                   # Y coordinates for each pixel
    │       ├── z.tif                   # Z coordinates for each pixel
    │       └── meta.json               # Metadata about the TIFXYZ mesh
    ├── surface-volumes/                # Extracted volumes at different resolutions
    │   ├── {resolution}-{energy}-volume-{volume_id}.zarr/
    │   │   ├── 0/                      # Highest resolution level
    │   │   ├── 1/                      # Downsampled level 1
    │   │   ├── ...                     # Additional downsampled levels
    │   │   ├── .zattrs                 # OME-ZARR metadata
    │   │   └── .zgroup
    │   └── {resolution}-{energy}-volume-{volume_id}.tifs/
    │       ├── 00.tif                  # Layer 0 (surface)
    │       ├── 01.tif                  # Layer 1
    │       ├── ...
    │       └── NN.tif                  # Layer N (depth varies by segment)
    └── ink-detection/                  # Ink detection results (if available)
        └── {sample}-{segment_id}-{volume_id}-{model_id}-tile{size}-stride{size}.tif
```

**Surface volumes** contain texture data extracted from the parent volume along the segment surface at different depths. These are available in both OME-ZARR format (for streaming access) and as TIFF stacks (numbered 00.tif, 01.tif, etc.).

**Ink detection results** are prediction outputs from machine learning models applied to segment surface volumes. The filename encodes:

- Sample ID
- Segment ID
- Volume ID used for extraction
- Model ID used for inference
- Tiling parameters (tile size and stride for processing large images)

**Example:** `PHerc0139-20250731185658-2.403um-0.22m-77keV-volume-20250820105138-20250807020208-canonical-2um-tile256-stride82.tif`

#### Representations

Representations contain derived data products generated from volumes, such as ML model predictions.

**Directory structure:**

```
representations/
└── predictions/
    └── surfaces/                       # Predicted papyrus surfaces
        └── {volume_id}-surface-{model_id}.zarr/
            ├── 0/                      # Highest resolution level
            ├── 1/                      # Downsampled level 1
            ├── ...
            ├── .zattrs                 # OME-ZARR metadata
            └── .zgroup
```

**Predicted surfaces** are ML model outputs that identify papyrus surface locations within volumes. These are stored as OME-ZARR volumes with the same spatial dimensions as the source volume, where voxel values indicate the probability or presence of a surface at that location.

## ID and Naming Conventions

All IDs follow a UTC datetime-based format: `YYYYMMDDhhmmss`

**Structure:**

- **Short ID:** `20231201141544` (creation timestamp)
- **Long ID:** `20231201141544-3.240um-70keV` (includes descriptive metadata)
- **Full filename:** `20231201141544-3.240um-70keV-masked.zarr` (includes suffix)

**Naming components:**

- **Resolution:** `3.240um` - pixel/voxel size in micrometers
- **Energy:** `70keV` - X-ray energy
- **Suffix:** `masked`, `masked.zarr`, `tiff_16bits`, etc. - processing or format indicator

## Data Types and Formats

### Volume Formats

| Format       | Description                          | Usage                                                  |
| ------------ | ------------------------------------ | ------------------------------------------------------ |
| **OME-ZARR** | Cloud-optimized chunked array format | Primary distribution format, supports streaming access |
| **TIFF**     | Traditional image stack              | Legacy format, full download required                  |

#### OME-ZARR Volumes

An [OME-ZARR](https://ngff.openmicroscopy.org/latest/) volume is a cloud-optimized, chunked, multi-resolution representation of 3D volumetric data. Volumes are stored in a hierarchical directory structure with multiple resolution levels for efficient access. Each level (with level 0 being the highest resolution) is stored in its own subdirectory which itself represents a self-contained [zarr](https://zarr.readthedocs.io/en/stable/) array. Volume data is usually stored with 8-bit intensities in
128^3 voxel chunks (a trade-off between reasonable interactive access speeds and storage concerns).

#### TIFF Stacks

Volumes and Segments might be exported as traditional TIFF stacks (usually 8 bit). These are stored as a series of 2D TIFF images in a directory. Each image represents a slice of the 3D volume or segment.

### Mesh Formats

| Format     | Description                     | Usage                                        |
| ---------- | ------------------------------- | -------------------------------------------- |
| **OBJ**    | 3D mesh with vertices and faces | Surface geometry                             |
| **TIFXYZ** | Three TIFF images (x, y, z)     | Per-pixel 3D coordinates for texture mapping |

#### Waveform Mesh (.obj)

Segments are represented as 3D meshes in the Wavefront OBJ format. These files contain vertex and face information to define the geometry of the papyrus surfaces. The vertice coordinates are in a 3D space corresponding to the original volume. The texture coordinates represent the 2D flattened space of the papyrus surface. These uv-texture coordinates are sometimes scaled to the interval [0..1] and to render an image need to be multiplied by the width/height of the segment to arrive at image
coordinates.

#### TIFXYZ Mesh (.tif)

A TIFXYZ mesh is a (custom) sampled representation of a mesh that directly converts image coordinates to the 3D coordinates in the original volume. It is stored with this file structure:

```tifxyz/
├── x.tif   # 3D X coordinates for each 2D uv pixel
├── y.tif   # 3D Y coordinates for each 2D uv pixel
├── z.tif   # 3D Z coordinates for each 2D uv pixel
└── meta.json  # Metadata about the TIFXYZ mesh
```

TIFXYZ is implemented and supported by [VC3D](https://github.com/ScrollPrize/villa/tree/main/volume-cartographer).

#### Metadata Files

(not yet published)

## How to Access the Data

### Web Browser

Navigate to https://<TBD>/ and browse directories (FIXME)

### Python S3 Zarr access

To access OME-ZARR volumes directly from S3 using Python, you can use the `zarr` library along with `fsspec` for remote file system access.

**Runnable example:** See [`zarr_volume_access.py`](examples/zarr_volume_access.py) which can be run with:

```bash
uv run examples/zarr_volume_access.py
```

```python
import zarr
import fsspec
import matplotlib.pyplot as plt

# Configure S3 file system access
s3 = fsspec.filesystem('s3', anon=False)  # Set anon=True if using public access

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
plt.show()

# For segment surface volumes (TIFF stacks), you can use tifffile:
import tifffile

# Read a specific layer from a surface volume
with s3.open('s3://vesuvius-challenge-open-data/PHerc0139/segments/20250731185658-z_dbg_gen_09900/surface-volumes/9.362um-1.2m-113keV-volume-20250728140407.tifs/00.tif', 'rb') as f:
    layer_0 = tifffile.imread(f)
    plt.imshow(layer_0, cmap='gray')
    plt.title('Surface layer 0')
    plt.show()
```

## Support and Citation

### Contact

For questions or issues with the data:

- Vesuvius Challenge Web Site: [https://scrollprize.org/](https://scrollprize.org/)
- GitHub Issues: [Vesuvius Challenge repository](https://github.com/scrollprize/villa)
- Community Forum: [Scroll Prize Discord](https://discord.gg/V4fJhvtaQn)

### Citation

(to be done if needed)

### License

[CC-BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
