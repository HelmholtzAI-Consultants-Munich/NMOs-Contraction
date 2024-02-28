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


The **time series analysis** comprehends the signal pre-processing and the univariate and bivariate analysis.

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
├── colab                  <- Final Jupyter notebook for Google Colab environment
│ 
├── exploration            <- notebooks and presentation from the exploration phase
│
├── signal-extraction      <- notebooks for the signal extraction step
│
├── time-series-analysis   <- scripts for the time series extraction
│
├── requirements.txt       <- File for installing python dependencies
│
└── README.md
```
## Notebooks Versioning
We report here the main difference between the colab notebook delivered to the collaborators

- v1 - 31/01/2023: first version built for the first batch of data
- v2 - 03/05/2023: add a widget to select the input channel for the video, add a condition for corrupted video from the first batch
- v3 - 30/05/2023: remove reference to curare and other classes, generalize for any kind of phenotype/treatment present in the Excel file with the data description
- v4 - 07/12/2023: ts-extraction: add neuro-muscular ratio calculation, ts-analysis: add widget to choose Excel file and save final table is CSV file
- v5 - 12/02/2024: added 1_time_series_extraction_v5: added computation pixel counts of the organoid and added to the Excel file (waiting for image resolution to convert in the physical area) and extended box widget for image selection
     - 28/02/2024: adapt the notebooks to the new Excel template format, added violin plots and total count plot (still waiting for pixel resolution to convert in the physical area).

## Contributing
Comments and input are very welcome! Please, if you have a suggestion or you think something should be changed, open an issue or submit a pull request.
