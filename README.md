# OmniConnectModel

This repository is an **umbrella project** for computational neuroscience tools and models.  
It integrates multiple approaches to studying brain networks across scales, from **cross-species atlases** to **directed connectomes** and **network modeling**.

---

## Structure

All projects live under the `projects/` directory. Each project includes its own README and `requirements.txt`.

```
OmniConnectModel/
├── README.md              # Top-level overview (this file)
├── LICENSE                # MIT license for the whole repository
│
└── projects/
    ├── common_cross_species_atlas/   # Common gray-matter atlas across species
    └── cross_species_connectomics/   # Directed connectomics and tracer integration
```

---

## Projects

### 1. Common Cross-Species Atlas
**Path:** `projects/common_cross_species_atlas/`  

Contains the code and minimal data required to reproduce all quantitative analyses and figures for the **Common Cross-Species Atlas**.  
Includes the hierarchical parcellation framework, volumetric statistics, and atlas validation metrics across mouse, marmoset, rhesus macaque, and human.

📄 [Project README](projects/common_cross_species_atlas/README.md)  
📖 Citation:  
> **A common cross-species atlas of cortical gray matter.**  
> Siva Venkadesh, Yuhe Tian, Wen-Jieh Linn, Jessica Barrios Martinez, Harrison Mansour, James Cook,  
> David J. Schaeffer, Diego Szczupak, Afonso C. Silva, G Allan Johnson, Fang-Cheng Yeh.  
> *bioRxiv* (2025). doi: [10.1101/2025.09.08.675002](https://doi.org/10.1101/2025.09.08.675002)

---

### 2. Cross-Species Connectomics
**Path:** `projects/cross_species_connectomics/`  

Framework for constructing **directed connectomes** by integrating **mouse viral tracing** with **diffusion MRI** across species.  
Includes tractography shell scripts, connectome construction, validation, and statistical analysis code.

📄 [Project README](projects/cross_species_connectomics/README.md)  
📖 Citation:  
> **Cross-species brain circuitry from diffusion MRI tractography and mouse viral tracing.**  
> Siva Venkadesh, Wen-Jieh Linn, Yuhe Tian, G Allan Johnson, Fang-Cheng Yeh.  
> *bioRxiv* (2025). doi: [10.1101/2025.09.07.674762](https://doi.org/10.1101/2025.09.07.674762)

---

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/OmniConnectModel.git
cd OmniConnect-ModelForge
```

Install dependencies:

Each project defines its own `requirements.txt` for additional dependencies.

---

## License

This repository is released under the **MIT License**.  
See the [LICENSE](LICENSE) file for details.

---
