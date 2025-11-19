# Common Cross-Species Atlas

This project is part of the **OmniConnectModel** umbrella repository.  
It contains the quantitative analyses and figure generation code for:

> **A common cross-species atlas of cortical gray matter**  
> Siva Venkadesh, Yuhe Tian, Wen-Jieh Linn, Jessica Barrios Martinez, Harrison Mansour, James Cook, David J. Schaeffer, Diego Szczupak, Afonso C. Silva, G Allan Johnson, Fang-Cheng Yeh.  
> *bioRxiv* (2025). [doi: 10.1101/2025.09.08.675002](https://doi.org/10.1101/2025.09.08.675002)

---

## Project Structure

```
projects/common_cross_species_atlas/
├── README.md                  # Project-specific documentation (this file)
├── requirements.txt           # Dependencies for notebook execution
├── CHA_quants.ipynb           # Main notebook: generates all manuscript figures
└── data/                      # Minimal dataset used in analyses
    ├── atlases/               # Species atlases and overlap metrics
    ├── roistats/              # Regional volumetric statistics
    └── dice_validation/       # Dice matrices from NEUROPARC atlases
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

Launch the notebook to reproduce all quantitative results and figures:

```bash
jupyter notebook CHA_quants.ipynb
```

All figures are displayed inline within the notebook.

---

## Data Organization

The `data/` folder contains the subdirectories required for the analyses:
- `atlases/` — Atlas files and overlap metrics used in validation for each species.  
- `roistats/` — Regional volumetric data used for quantitative comparisons.  
- `dice_validation/` — Dice matrices generated using NEUROPARC atlases.

Please follow the **license information provided in each atlas’s `license.txt`** when using these datasets.

---

## Reproducibility

All analyses and plots are produced directly from the provided data using deterministic processing steps.  
Dependency versions are pinned in `requirements.txt` to ensure compatibility.

---

## Citation

Please cite both the manuscript and this repository:

> **A common cross-species atlas of cortical gray matter**  
> Siva Venkadesh et al., *bioRxiv* (2025). [10.1101/2025.09.08.675002](https://doi.org/10.1101/2025.09.08.675002)

---
