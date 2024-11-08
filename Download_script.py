import json
import random
from functools import partial
from typing import Any, Dict, List, Literal, Optional, Union

import pandas as pd
from loguru import logger

import objaverse.xl as oxl
from objaverse.utils import get_uid_from_str


'''
def get_example_objects1() -> pd.DataFrame:                                         ### FOnction originale, enlever le 1
    """Returns a DataFrame of example objects to use for debugging."""
    return pd.read_json("example-objects.json", orient="records")

def get_example_objects1() -> pd.DataFrame:                                     ### Ma fonction
    df = pd.read_parquet('~/.objaverse/sketchfab/sketchfab.parquet')
    ret = df.sample(n=5, random_state= random.randint(0, len(df)))
    return ret
'''
def get_example_objects() -> pd.DataFrame:                                     ### Ma fonction
    annotations = oxl.get_annotations(
    download_dir="~/.objaverse" # default download directory
	)
    #return annotations.sample(5)
    return annotations


def save_object_addresses_to_json(annotations: pd.DataFrame, output_path: str = "adresses-objets.json") -> None:    ### Ma fonction
    """
    Saves a JSON file containing addresses of downloaded objects in a format similar to example-objects.json.

    Args:
        annotations (pd.DataFrame): A DataFrame containing annotations of objects.
        output_path (str): The path where the JSON file will be saved.

    Returns:
        None
    """
    # Select only the columns required for the JSON output
    objects_info = annotations[['sha256', 'fileIdentifier', 'source']]

    # Convert to a list of dictionaries
    objects_list = objects_info.to_dict(orient="records")

    # Save to a JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(objects_list, f, indent=2)

    print(f"File saved to {output_path}")



##############################
annotations = get_example_objects()  # Assuming this fetches the full annotations DataFrame
save_object_addresses_to_json(annotations, "/home/vazqueza/5A/4/objaverse-xl/scripts/rendering/all_adresses_objets.json")          ###### Chemin à modifier 