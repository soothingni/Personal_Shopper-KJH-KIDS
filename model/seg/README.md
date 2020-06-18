# Fashion Image segmentation with Detectron2

![sampleimage1](imgs/mask.gif)



## Requirement

- Linux or macOS with Python ≥ 3.6
- Detectron2
- PyTorch ≥ 1.4
- torchivision that matches the PyTorch installation. You can install them together at [pytorch.org](https://pytorch.org) to make sure of this
- CUDA ≥ 10.1
- OpenCV, PIL to save RGBA type image
- pycocotools
- gcc &g++  ≥5 are required.



## Hardware

The model are trained using following hardware:

- Nvidia Tesla P4
- 32GB RAM



## Installation

```
pip install -U torch==1.5 torchvision==0.6 -f https://download.pytorch.org/whl/cu101/torch_stable.html 
pip install cython pyyaml==5.1
pip install -U 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
pip install detectron2==0.1.3 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu101/torch1.5/index.html
```



## Getting Started

```python
python mask.py --dir demo
```

## Model

[Pretrained_200610](https://drive.google.com/file/d/1mGvNaa1u6SFbldQbaZqB9X_WSV3hVo2i/view?usp=sharing)



## License

Fashion Image Segmentation is relesed under the [Apache 2.0 license.](https://github.com/facebookresearch/detectron2/blob/master/LICENSE)