import os
from PIL import Image

for filename in os.listdir('images'):
    if filename.startswith('min'):
        os.remove('images/' + filename)

for filename in os.listdir('images'):
    image = Image.open('images/' + filename)
    ratio = image.width / image.height
    if ratio < 1:
        image.thumbnail((150, 150 / ratio), Image.ANTIALIAS)
        image.crop((0, 0, 150, 150)).save('images/min_' + filename)
    else:
        image.thumbnail((150 * ratio, 150), Image.ANTIALIAS)
        image.crop((0, 0, 150, 150)).save('images/min_' + filename)
