
For each primate species, cha_<species>_moused.nii.gz differs from cha_<species>.nii.gz as follows:
- level-2 divisions of primate PAR masked in cha_<species>_moused.nii.gz to align with rodents' lack of level-2 PAR 
- Caudate and Putamen divisions of primate BG masked in cha_<species>_moused.nii.gz to align with rodents' lack of such divisions (CaudoPutamen)

These masked files were used to enable systematic comparisons across rodents and primates (geometric consistency, connectivity comparison etc.)
On the other hand, primate cha_<species>.nii.gz were used in within-species analysis (containment evaluation, cross atlas dice similarities)