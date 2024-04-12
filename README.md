[![stable](http://badges.github.io/stability-badges/dist/stable.svg)](http://github.com/badges/stability-badges)
[![python](https://img.shields.io/badge/-Python__3.9-blue?logo=python&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/HelmholtzAI-Consultants-Munich/NMOs-Contraction)

# NMOs-Contraction

## Description
This project aims to analyze the contraction of neuromuscular organoids developed from induced pluripotent stem cells coming from healthy individuals and patients with neuromuscular diseases. Specifically, we focus on organoids from patients with spinal muscular atrophy where the contraction of the muscle is severely affected.

The approach is divided into two main steps: the time series extraction and the time series analysis.

The **time series extraction** consists of the following steps:

- thresholding (Otsu method) for binary segmentation
- border extraction (Caddy Edge Detector method)
- border rotation
- border division into subregions
- vertical movement of the mean point of each region recorder over time to produce a time series

The previous steps are summarized in this video:

https://user-images.githubusercontent.com/104511563/221238175-c4786bb6-c710-43cb-b46a-b27510255ec3.mp4


The **time series analysis** comprehends the signal pre-processing, the feature extraction, and the univariate and bivariate analysis.

The pre-processing steps are:
- interpolation, to fill NaNs value which may occur from signal extraction
- scaling, to convert into physical units
- smoothing, to reduce noise
- de-trending, to correct organoid drift

## Installation and Requirement
The code has been implemented using Python 3.9. The libraries used by the pipeline are all listed in requirements.txt.

The notebooks in the NMO-colab branch can be run on a browser without the need for any installation on your local machine.
You can upload the folder on your Google Drive and run the notebooks on Colab, please note that you must have access to a Google account.

## Repo structure
The directory structure of the project looks like this:
```
├── colab                  <- folders and notebooks for Google Colab environment
│ 
├── exploration            <- notebooks and presentation from the exploration phase
│
├── local                  <- folders and notebooks for local run
│
├── utils                  <- scripts with general utility scripts
│
├── requirements.txt       <- file for installing python dependencies
│
└── README.md
```
## Instructions
The content in the 'colab' folder is outdated as of 30/05/2023 and should not be used.

To run the latest code, navigate to the 'local' folder. Open the notebooks in a Jupyter Lab session and click on the Voilà icon to execute the code.

## Contributing
Comments and input are very welcome! Please, if you have a suggestion or you think something should be changed, open an issue or submit a pull request.
