from PIL.PngImagePlugin import PngImageFile, PngInfo
import sys

path = sys.argv[1]
json = sys.argv[2]


targetImage = PngImageFile(path)

metadata = PngInfo()
metadata.add_text("sat_data", json)
targetImage.save(path, pnginfo=metadata)

