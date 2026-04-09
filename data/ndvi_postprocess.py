import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt


def create_png_from_band(src_path: str, dst_path: str, cmap="gray"):
    # read a downsampled version for quicker plotting
    with rasterio.open(src_path) as src:
        # choose an output shape no larger than 1000x1000
        height = src.height
        width = src.width
        factor = max(height / 1000, width / 1000, 1)
        out_shape = (
            int(src.count),
            int(height // factor),
            int(width // factor),
        )
        arr = src.read(1, out_shape=out_shape).astype(np.float32)
        arr = np.where(arr == src.nodata, np.nan, arr)
        arr_min = np.nanmin(arr)
        arr_max = np.nanmax(arr)
        norm = (arr - arr_min) / (arr_max - arr_min)
        plt.figure(figsize=(6, 6))
        plt.imshow(norm, cmap=cmap)
        plt.axis('off')
        plt.savefig(dst_path, bbox_inches='tight', pad_inches=0)
        plt.close()
    print(f"Wrote PNG {dst_path}")


def calculate_ndvi(red_path: str, nir_path: str, dst_path: str):
    # compute NDVI on a downsampled grid to keep processing fast
    with rasterio.open(red_path) as red_src, rasterio.open(nir_path) as nir_src:
        height = red_src.height
        width = red_src.width
        factor = max(height / 2000, width / 2000, 1)
        out_h = int(height // factor)
        out_w = int(width // factor)
        red = red_src.read(1, out_shape=(1, out_h, out_w)).astype(np.float32)
        nir = nir_src.read(1, out_shape=(1, out_h, out_w)).astype(np.float32)
        red = np.where(red == red_src.nodata, np.nan, red)
        nir = np.where(nir == nir_src.nodata, np.nan, nir)
        ndvi = (nir - red) / (nir + red)
        # update profile for the reduced resolution
        profile = red_src.profile
        profile.update(dtype=rasterio.float32, count=1, height=out_h, width=out_w)
        with rasterio.open(dst_path, 'w', **profile) as dst:
            dst.write(ndvi, 1)
    print(f"Computed NDVI and saved to {dst_path}")
    create_png_from_band(dst_path, dst_path.replace('.tif', '.png'), cmap='RdYlGn')


if __name__ == '__main__':
    red_tif = 'data/B04.tif'
    nir_tif = 'data/B08.tif'
    create_png_from_band(red_tif, 'data/red_band.png')
    create_png_from_band(nir_tif, 'data/nir_band.png')
    calculate_ndvi(red_tif, nir_tif, 'data/ndvi.tif')
