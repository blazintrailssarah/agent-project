import os
import requests
import rasterio
import numpy as np
import matplotlib.pyplot as plt


def download_file(url: str, dest: str):
    """Download a file from a URL to dest path if not already present."""
    if os.path.exists(dest):
        print(f"{dest} already exists, skipping download.")
        return
    print(f"Downloading {url} to {dest}...")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print("Download complete.")


def create_png_from_band(src_path: str, dst_path: str, cmap="gray"):
    """Read a single-band raster and save it as a PNG for easy viewing."""
    with rasterio.open(src_path) as src:
        arr = src.read(1).astype(np.float32)
        # stretch to 0-1
        arr_min, arr_max = np.nanmin(arr), np.nanmax(arr)
        norm = (arr - arr_min) / (arr_max - arr_min)
        plt.figure(figsize=(6, 6))
        plt.imshow(norm, cmap=cmap)
        plt.axis("off")
        plt.savefig(dst_path, bbox_inches="tight", pad_inches=0)
        plt.close()
    print(f"Wrote PNG {dst_path}")


def calculate_ndvi(red_path: str, nir_path: str, dst_path: str):
    """Compute NDVI from red and NIR bands and write to GeoTIFF."""
    with rasterio.open(red_path) as red_src, rasterio.open(nir_path) as nir_src:
        red = red_src.read(1).astype(np.float32)
        nir = nir_src.read(1).astype(np.float32)
        ndvi = (nir - red) / (nir + red + 1e-6)
        profile = red_src.profile
        profile.update(dtype=rasterio.float32, count=1)
        with rasterio.open(dst_path, "w", **profile) as dst:
            dst.write(ndvi, 1)
    print(f"Computed NDVI and saved to {dst_path}")
    # also make png
    create_png_from_band(dst_path, dst_path.replace(".tif", ".png"), cmap="RdYlGn")


def main():
    os.makedirs("data", exist_ok=True)
    base_url = "https://sentinel-s2-l1c.s3.amazonaws.com/tiles/10/C/DA/2016/11/30/0/"
    red_filename = "B04.jp2"
    nir_filename = "B08.jp2"
    red_path = os.path.join("data", red_filename)
    nir_path = os.path.join("data", nir_filename)

    download_file(base_url + red_filename, red_path)
    download_file(base_url + nir_filename, nir_path)

    # convert to GeoTIFFs with rasterio
    red_tif = red_path.replace('.jp2', '.tif')
    nir_tif = nir_path.replace('.jp2', '.tif')
    for jp2, tif in [(red_path, red_tif), (nir_path, nir_tif)]:
        if not os.path.exists(tif):
            with rasterio.open(jp2) as src:
                profile = src.profile
                data = src.read(1)
            profile.update(driver='GTiff')
            with rasterio.open(tif, 'w', **profile) as dst:
                dst.write(data, 1)
            print(f"Converted {jp2} to {tif}")

    # make pngs for bands
    create_png_from_band(red_tif, os.path.join("data", "red_band.png"))
    create_png_from_band(nir_tif, os.path.join("data", "nir_band.png"))

    # compute NDVI
    calculate_ndvi(red_tif, nir_tif, os.path.join("data", "ndvi.tif"))


if __name__ == "__main__":
    main()
