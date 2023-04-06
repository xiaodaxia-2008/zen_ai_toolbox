import openai
import re
import base64
import os
from IPython import embed
from PIL import Image
import pathlib
import io

# Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.proxy = os.getenv("http_proxy")

print(f"http_proxy: {os.getenv('http_proxy')}")
print(f"https_proxy: {os.getenv('https_proxy')}")


def get_new_file_name(file_name):
    # create image file directory
    p = pathlib.Path(file_name)
    if p.parent.exists() == False:
        os.makedirs(p.parent, exist_ok=True)

    # if img_file exists, add suffix to img_file
    p = pathlib.Path(file_name)
    i = 1
    while p.exists():
        p = p.parent / (p.stem + "_" + str(i) + p.suffix)
        i += 1
    return str(p)


def get_file_name_from_prompt(prompt, max_len=20):
    # get file name from prompt
    # find all words
    result = re.findall(r"[\w\d]+", prompt)
    # capitalize all words
    result = "_".join((word.lower() for word in result))
    img_file = result[:max_len] + ".png"
    return img_file


def create_image(prompt="This is a British Shorthair", n=1, size="1024x1024", response_format="b64_json", img_file=None):
    """create image using openai DALL·E model

    Args:
        prompt (str, optional): image description. Defaults to "This is a British Shorthair".
        n (int, optional): number of created images. Defaults to 1.
        size (str, optional): image size, ["256x256", "512x512", "1024x1024"]. Defaults to "1024x1024".
    """
    if img_file is None:
        img_file = get_file_name_from_prompt(prompt)
    img_file = get_new_file_name("./images/"+img_file)

    # request text to image
    response = openai.Image.create(
        prompt=prompt, n=n, size=size, response_format=response_format)

    if response_format == "b64_json":
        img_bytes = response['data'][0]['b64_json'].encode("utf8")
        with open(img_file, "wb") as f:
            f.write(base64.decodebytes(img_bytes))
    else:
        import requests
        img_url = response['data'][0]['url']
        print(f"Image URL: {img_url}")
        # download image from img_url
        response = requests.get(img_url)
        with open(img_file, "wb") as f:
            f.write(response.content)
    print(f"Image file: {img_file}")

    Image.open(img_file).show()


if __name__ == "__main__":
    prompt = """This is a cute British Shorthair and a little girl,
    the girl is embracing the cat,
    the girl wears a green dress,
    the cat is blue and white,
    the cat looks very sleepy,
    the image style is digital art
    """

    create_image(prompt=prompt,
                 n=1,
                 size="1024x1024", response_format="b64_json")
