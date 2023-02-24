[![experimental](http://badges.github.io/stability-badges/dist/experimental.svg)](http://github.com/badges/stability-badges)
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/HelmholtzAI-Consultants-Munich/NMOs-Contraction)

# NMOs-Contraction

## Description
The aim of this project is to analyse the contraction of neuromuscular organoids developed from induced pluripotent stem cells coming from healthy individual and patients with neuromuscular diseases. Specifically, we focus on organoids from patients with spinal muscular atrophy where contraction of muscle is severely affected.

The appraoch is devided in two main step: the time series extraction and the time series analysis.

The **time series extraction** consists of the following steps:

- thresholding (Otsu method) for binary segmentation
- border extraction (Caddy Edge Detector method)
- border rotation
- border division into subregions
- vertical movement of mean point of each region recorder over time to produce time series

The previous steps are summerized in this video:

https://user-images.githubusercontent.com/104511563/221238175-c4786bb6-c710-43cb-b46a-b27510255ec3.mp4


The **time series analysis** comprehends the signal pre-processing and the univariate and bivariate analysis.

The pre-processing steps are:
- interpolation, to fill NaNs value which may occur from signal extraction
- scaling, to convert in physical units
- smoothing, to reduce noise
- de-trending, to correct organoid drift

## Installation and Requirement
The code has been implemented using Python 3.9. The libraries used by the pipeline are all listed in requirements.txt.

The notebooks in the NMO-colab branch can be run on a browser without the need of any installation on your local machine.
You can upload the folder on your Google Drive and run the notebooks on Colab, please note that you must have acces to a Google account.

## Contributing
Comments and input are very welcome! Please, if you have a suggestion or you think something should be changed, open an issue or submit a pull request.
