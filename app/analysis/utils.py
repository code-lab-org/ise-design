from base64 import b64encode
import hashlib
from humanhash import humanize
import json
import numpy as np
from pkg_resources import resource_stream
from PIL import Image
import re
from xml.etree import ElementTree

from ..schemas.brick import Brick

with open(resource_stream(__name__, '../../resources/bricks.json').name, 'r') as data:
    BRICK_DATA = json.load(data)

VALID_BL_IDS = []
with open(resource_stream(__name__, '../../resources/ISE_Palette.xml').name, 'rb') as xml:
    tree = ElementTree.parse(xml)
    for item in tree.getroot().iter('ITEM'):
        bl_id = item.find('ITEMID').text
        VALID_BL_IDS.append(bl_id)
    VALID_BL_IDS.append("4345b") # fix BrickLink error (mislabled brick)

def crop_image(thumb_path):
    """
    Crops an image to the smallest non-empty rectangular bounding box.

    Args:
        thumb_path (str): path to the image file to be cropped.
    """
    image = Image.open(thumb_path)
    # image.crop(image.getbbox()).save(filename)
    image.load()
    image_data = np.asarray(image)
    image_data_bw = image_data.max(axis=2)
    non_empty_columns = np.where(image_data_bw.max(axis=0) > 0)[0]
    non_empty_rows = np.where(image_data_bw.max(axis=1) > 0)[0]
    if len(non_empty_columns) == 0 or len(non_empty_rows) == 0:
        cropBox = (0, 0, 0, 0)
    else:
        cropBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))
    image_data_new = image_data[cropBox[0]:cropBox[1]+1, cropBox[2]:cropBox[3]+1 , :]
    new_image = Image.fromarray(image_data_new)
    new_image.save(thumb_path)

def get_design_id(ldr_path):
    """
    Gets a unique identifier for a LDraw file.

    Args:
        ldr_path (str): path to the file that was uploaded.

    Returns:
        str: the UUID
    """
    h  = hashlib.sha1()
    b  = bytearray(128*1024)
    mv = memoryview(b)
    with open(ldr_path, 'rb', buffering=0) as f:
        for n in iter(lambda : f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()

def get_design_name(ldr_path, words=2):
    """
    Gets a unique design name for a LDraw file.

    Args:
        ldr_path (str): path to the file that was uploaded.
        words (int): number of words in the name.

    Returns:
        str: the design name
    """
    return humanize(get_design_id(ldr_path), words=2, separator=' ')

def get_thumbnail(thumb_path):
    """
    Gets the thumbnail in base64 encoding.
    """
    with open(thumb_path, 'rb') as thumb_fp:
        contents = thumb_fp.read()
        return b64encode(contents).decode('utf-8')

def get_brick_data(bl_id, ld_color=None):
    """
    Get the data for a brick.
    """
    for data in BRICK_DATA:
        if ((ld_color is None and data["bl_id"] == bl_id)
                or (ld_color is not None
                    and data["bl_id"] == bl_id
                    and data["ld_color"] == ld_color)):
            return data
    return None

def _parse_brick(ldr_line):
    """
    Parse a brick from a LDraw line.
    """
    elements = ldr_line.split()
    if len(elements) == 15 and elements[0] == "1" and re.match(r"^(\w+)\.dat$", elements[14]):
        bl_id = re.match(r"^(\w+)\.dat$", elements[14]).group(1)
        ld_color = int(elements[1])
        position = [float(elements[2]), float(elements[3]), float(elements[4])]
        rotation = [
            [float(elements[5]), float(elements[6]), float(elements[7])],
            [float(elements[8]), float(elements[9]), float(elements[10])],
            [float(elements[11]), float(elements[12]), float(elements[13])]
        ]
        data = get_brick_data(bl_id, ld_color)
        if data is None:
            # fall back to color-less version
            data = get_brick_data(bl_id)
        if data is None:
            return Brick(
                bl_id = bl_id,
                ld_color = ld_color,
                position = position,
                rotation = rotation
            )

        lower = np.array(data.get("offset", [0,0,0]))
        upper = lower - np.array(data.get("dimensions", [0,0,0]))
        raw_vertices = np.array([
            [lower[0],   lower[1],    lower[2]],
            [upper[0],   lower[1],    lower[2]],
            [upper[0],   upper[1],    lower[2]],
            [upper[0],   upper[1],    upper[2]],
            [upper[0],   lower[1],    upper[2]],
            [lower[0],   lower[1],    upper[2]],
            [lower[0],   upper[1],    upper[2]],
            [lower[0],   upper[1],    lower[2]],
        ])
        vertices = np.around(
            np.matmul(
                raw_vertices,
                np.array(rotation).transpose()
            ) + np.array(position)
        )
        return Brick(
            bl_id = bl_id,
            ld_color = ld_color,
            position = position,
            rotation = rotation,
            id = data.get("id", None),
            name = data.get("name", None),
            cost = data.get("cost", 0),
            mass = data.get("mass", 0),
            safety = data.get("safety", 0),
            coolness = data.get("coolness", 0),
            volume = np.product(data.get("dimensions", [0,0,0])),
            valid_forward_axes = data.get("valid_forward_axes", None),
            bl_color = data.get("bl_color", None),
            is_valid = bl_id in VALID_BL_IDS,
            vertices = vertices.tolist()
        )
    return None

def get_bricks(ldr_path):
    """
    Get the bricks from a LDraw file path.
    """
    with open(ldr_path, 'r') as ldr_fp:
        return [
            brick
            for line in ldr_fp.readlines()
            for brick in [_parse_brick(line)]
            if brick is not None
        ]
