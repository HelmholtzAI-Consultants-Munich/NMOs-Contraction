
[![stable](http://badges.github.io/stability-badges/dist/stable.svg)](http://github.com/badges/stability-badges)
[![python](https://img.shields.io/badge/-Python__3.9-blue?logo=python&logoColor=white)](https://github.com/pre-commit/pre-commit)

# NMOs-Contraction

## Description
This project aims to analyze the contraction of neuromuscular organoids developed from induced pluripotent stem cells coming from healthy individuals and patients with neuromuscular diseases. Specifically, we focus on organoids from patients with spinal muscular atrophy where the contraction of the muscle is severely affected.

The approach is divided into two main steps: the time series extraction and the time series analysis.

The **time series extraction** works with videos displaying contraction in a small area of the organoid and consists of the following steps:
- thresholding (Otsu method) for binary segmentation of organoid and background
- border extraction (Canny Edge Detector method)
- border rotation
- border division into subregions
- vertical movement of the mean point of each region recorder over time to produce a time series representing the border contraction

The previous steps are summarized in this video:

https://user-images.githubusercontent.com/104511563/221238175-c4786bb6-c710-43cb-b46a-b27510255ec3.mp4


The **time series analysis** comprehends the signal pre-processing, the feature extraction, and the univariate and bivariate analysis.

The pre-processing steps are:
- interpolation, to fill NaNs value which may occur from signal extraction
- scaling, to convert into physical units
- smoothing, to reduce noise
- de-trending, to correct organoid drift

## Installation and Requirements
The code has been implemented using Python 3.9. The libraries used by the pipeline are all listed in requirements.txt.
Below the instruction to create an environment and clone the repository.

1. Make sure you have Python version 3.9 installed on your system.

2. Create a new virtual environment with Python 3.9. You can use `venv` or `conda` depending on your preference:

    Using venv
    ```
    python3.9 -m venv NMO-contraction
    ```
   
    Using conda

    ```
    
    conda create --name NMO-contraction python=3.9
    ```

3. Activate the virtual environment:

    For Unix/Linux
    ```
    source NMO-contraction/bin/activate
    ```
    
    For Windows
    ```
    NMO-contraction\Scripts\activate
    ```
   
    For macOS with conda
    ```
    conda activate NMO-contraction
    ```

4. Clone this repository to your local machine:

    ```
    git clone https://github.com/HelmholtzAI-Consultants-Munich/NMOs-Contraction.git
    ```

5. Navigate to the cloned repository directory:

    ```
    cd NMOs-Contraction
    ```

6. Install the required packages from the `requirements.txt` file:

    ```
    pip install -r requirements.txt
    ```

Now you're all set up and ready to start working with the project!

## Repo structure
The directory structure of the project looks like this:
```
│
├── src                    <- folders and notebooks for running the notebooks
│
├── utils                  <- scripts with general utility scripts
│
├── requirements.txt       <- file for installing python dependencies
│
└── README.md
```

## Instructions

To run the latest code, navigate to the 'src' folder. Open the notebooks in a ![Jupyter Lab session](https://jupyterlab.readthedocs.io/en/stable/getting_started/starting.html) and click on the Voilà icon (see image below) to execute the code and interact with it.
![voila-example](https://github.com/HelmholtzAI-Consultants-Munich/NMOs-Contraction/assets/104511563/c368c2ce-f1e4-4149-97c7-52a130ec6458)


## Contributing
Comments and input are very welcome! Please, if you have a suggestion or you think something should be changed, open an issue or submit a pull request.
