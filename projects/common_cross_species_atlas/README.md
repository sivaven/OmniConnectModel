# Common Cross-Species Atlas
This project is part of the **OmniConnectModel** umbrella repository.  
It contains the quantitative analyses and figure generation code for:
> **A hierarchical framework for cortical and subcortical gray-matter parcellation across rodents, primates, and humans**  
> Siva Venkadesh, Yuhe Tian, Wen-Jieh Linn, Jessica Barrios Martinez, Harrison Mansour, James Cook, David J. Schaeffer, Diego Szczupak, Afonso C. Silva, G Allan Johnson, Fang-Cheng Yeh.  
> *bioRxiv* (2025). [doi: 10.1101/2025.09.08.675002](https://doi.org/10.1101/2025.09.08.675002)
---
## Project Structure
```
projects/common_cross_species_atlas/
├── README.md                                  # Project-specific documentation (this file)
├── requirements.txt                           # Dependencies for notebook and module execution
├── CHA_integrate.py                           # Standalone CLI / importable module to integrate a new atlas or connectome into CHA
├── CHA_quants.ipynb                           # Main notebook 1: generates Figures 4 and 5 all panels
├── CHA_Validation_Tracer.ipynb                # Main notebook 2: generates Figure 6 all panels
├── CHA_Validation_Homology_Confidence.ipynb   # Main notebook 3: generates Figure 7 all panels
└── data/                                      # Minimal dataset used in analyses
    ├── atlas/                                 # Species atlases and overlap metrics
    ├── roistats/                              # Regional volumetric statistics
    ├── primate_tracer/                        # Marmoset tracer data download and analysis outputs
    ├── homology_confidence/                   # analysis outputs from homology confidence (figure 7)
    └── dice_validation/                       # Dice matrices from NEUROPARC atlases
	
```
---
## Requirements
- **Python ≥ 3.8**  
- Install dependencies:
```bash
pip install -r requirements.txt
```
---
## Usage
Launch a notebook to reproduce all quantitative results and figures:
```bash
jupyter notebook CHA_<notebook 1, 2, or 3>.ipynb
```
All figures are displayed inline within the notebook.

---
## Integrate your own atlas or connectome
The notebooks above reproduce the manuscript analyses and figures. To apply the
same framework to your own data, use the standalone module `cha_integrate.py`,
which exposes the integration steps as a command-line tool and as importable
functions.

Given a source atlas aligned to the relevant species template (alignment is
performed in DSI Studio or any registration tool) and the CHA label volume for that species:
```bash
# 1. compute the containment table W (source regions x CHA regions)
python CHA_integrate.py containment \
    --atlas my_atlas.nii.gz --atlas-labels my_atlas.txt \
    --cha cha.nii.gz --cha-labels cha.txt --out W.csv

# 2a. assign each source region to its CHA region of maximum containment
python CHA_integrate.py assign --containment W.csv --out assignment.csv

# 2b. or project a connectome into CHA space  (F_CHA = W.T @ F @ W)
python CHA_integrate.py project \
    --connectome my_connectome.csv --containment W.csv --out connectome_cha.csv
```
The marmoset tracer integration in `CHA_Validation_Tracer.ipynb` is the worked
example for this workflow. The notebooks serve as the manuscript companion; the
module is the standalone path for new data.

The `containment` step requires `nibabel`; `assign` and `project` need only
`numpy` and `pandas`.

---
## Data Organization
The `data/` folder contains the subdirectories required for the analyses:
- `atlas/` — Atlas files and overlap metrics used in validation for each species.  
- `roistats/` — Regional volumetric data used for quantitative comparisons.  
- `dice_validation/` — Dice matrices generated using NEUROPARC atlases.
- `primate_tracer/` — Marmoset tracer data download, analysis and intermediate outputs.
- `homology_confidence/` — Analysis and intermediate outputs from homology confidence (figure 7).
Please follow the **license information provided in each atlas’s `license.txt`** when using these datasets.
---
## Reproducibility
All analyses and plots are produced directly from the provided data using deterministic processing steps.  
Dependency versions are pinned in `requirements.txt` to ensure compatibility.

---
## Citation
Please cite both the manuscript and this repository:
> **A hierarchical framework for cortical and subcortical gray-matter parcellation across rodents, primates, and humans**  
> Siva Venkadesh et al., *bioRxiv* (2025). [10.1101/2025.09.08.675002](https://doi.org/10.1101/2025.09.08.675002)
---
