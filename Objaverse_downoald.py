#Objaverse_downoald 

import objaverse
import objaverse.xl as oxl

annotations = oxl.get_annotations(
    download_dir="/home/opdal/Bureau/5GMM/Synthetic-Data-Generation-for-Supervised-Learning-Using-3D-Tools/PYBLEND/objects6glb" # default download directory
)

oxl.download_objects(annotations[annotations["fileType"]== "glb"][2:102].reset_index(drop=True), "/home/opdal/Bureau/5GMM/Synthetic-Data-Generation-for-Supervised-Learning-Using-3D-Tools/PYBLEND/objects6gbl")
