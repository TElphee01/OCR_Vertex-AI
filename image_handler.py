from PIL import Image
import io


def convert_image(input):
    output = None
    try:
        new_blob = input.download_as_bytes()
        file_like_object = io.BytesIO(new_blob)
        output = Image.open(file_like_object)
    except Exception as e:
        print("Error in image_handler: " + str(e))
    if output is None:
        print("Passive error converting image")

    return output
