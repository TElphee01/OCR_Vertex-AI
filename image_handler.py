from PIL import Image
import io


def convert_image(input):
    new_blob = input.download_as_bytes()
    file_like_object = io.BytesIO(new_blob)
    output = Image.open(file_like_object)

    if output is None:
        raise Exception("Passive error converting image")
    else:
        return output
