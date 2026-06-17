#!/usr/bin/env python3
"""
cha_integrate.py

Standalone utility for integrating an atlas or a connectome into the
Common Hierarchical Atlas (CHA).

Two operations are provided:

  1. Containment-based assignment
     Label each region of a source atlas by the CHA region it is most
     contained in (maximum containment).

  2. Containment-weighted projection
     Map a connectome defined on a source atlas into CHA space as
         F_CHA = W.T @ F @ W
     where W is the source-to-CHA containment table.

The companion notebooks (CHA_quants and CHA_Validation_Tracer) document
how these operations were used in the manuscript, with the marmoset
retrograde tracer (FLNe) connectome as the worked example. This module
exposes the same operations as reusable functions and as a command-line
entry point, so they can be run on a reader's own atlas and connectome.

Inputs a user provides:
  - their atlas as a NIfTI label volume, aligned to the relevant species
    template (alignment is performed externally in DSI Studio or other registration tools)
  - a label text file ("ID name" per line) for that atlas
  - the CHA label volume and its label text file for the same species
  - optionally, a connectome as a CSV (source regions x source regions)

Dependencies: numpy and pandas; nibabel only for steps that read
NIfTI volumes.

Examples
--------
Compute a containment table from two aligned label volumes:
    python cha_integrate.py containment \
        --atlas my_atlas.nii.gz --atlas-labels my_atlas.txt \
        --cha cha.nii.gz --cha-labels cha.txt \
        --out W.csv

Assign each source region to its CHA region of maximum containment:
    python cha_integrate.py assign --containment W.csv --out assignment.csv

Project a connectome into CHA space:
    python cha_integrate.py project \
        --connectome my_connectome.csv --containment W.csv \
        --out connectome_cha.csv
"""

import argparse
import json

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Label handling
# ---------------------------------------------------------------------------

def read_labels(txt_path):
    """Read a label file with 'ID name' per line.

    Returns a DataFrame indexed by integer ID with the name in column 1.
    """
    return pd.read_table(txt_path, index_col=0, header=None, sep=r"\s+")


def get_roi_names(txt_path):
    """Return the list of ROI names from a label text file."""
    return list(read_labels(txt_path)[1].values)


# ---------------------------------------------------------------------------
# Containment computation
# ---------------------------------------------------------------------------

def get_percent_overlap(atlas, target, roi_indices, verbose=False):
    """Fractional overlap of each atlas ROI with each target parcel.

    For atlas ROI i and target parcel j:
        overlap[i, j] = voxels(atlas == i AND target == j) / voxels(atlas == i)

    Returns the overlap matrix (n_atlas x n_target) and the target IDs.
    """
    target_ids = np.unique(target)
    n_atlas = len(roi_indices)
    n_target = len(target_ids)

    percent_overlap = np.zeros((n_atlas, n_target))
    for i, roi_id in enumerate(roi_indices):
        if verbose and i % 100 == 0:
            print(f"  processing ROI {i}/{n_atlas}", flush=True)
        atlas_mask = (atlas == roi_id)
        atlas_count = np.sum(atlas_mask)
        if atlas_count == 0:
            continue
        for j, tid in enumerate(target_ids):
            percent_overlap[i, j] = np.sum(atlas_mask & (target == tid)) / atlas_count
    return percent_overlap, target_ids


def build_overlap_df(atlas_labels, target_labels_txt, percent_overlap, target_ids):
    """Assemble the overlap matrix into a labelled DataFrame.

    Rows are source-atlas region names, columns are target (CHA) region
    names. A trailing 'SUM' column reports the row sum.
    """
    target_labels = read_labels(target_labels_txt)
    col_names = []
    for tid in target_ids:
        tid_int = int(tid)
        if tid_int == 0:
            col_names.append("0")
        elif tid_int in target_labels.index:
            col_names.append(target_labels.loc[tid_int, 1])
        else:
            col_names.append(f"unknown_{tid_int}")
    popd = pd.DataFrame(percent_overlap, index=atlas_labels[1].values, columns=col_names)
    popd["SUM"] = popd.sum(axis=1)
    return popd


def containment_from_arrays(atlas_data, cha_data, atlas_labels, cha_labels_txt,
                            verbose=False):
    """Build the source-to-CHA containment table W from label arrays.

    W has source-atlas regions as rows and CHA regions as columns; entry
    W[i, k] is the fraction of source region i contained in CHA region k.
    The background column ('0') and the 'SUM' column are removed.
    """
    roi_indices = atlas_labels.index.values
    overlap, target_ids = get_percent_overlap(atlas_data, cha_data, roi_indices,
                                              verbose=verbose)
    popd = build_overlap_df(atlas_labels, cha_labels_txt, overlap, target_ids)
    drop = [c for c in ("0", "SUM") if c in popd.columns]
    return popd.drop(columns=drop)


def containment_table(atlas_nii, cha_nii, atlas_labels_txt, cha_labels_txt,
                      verbose=False):
    """Build W directly from two aligned NIfTI label volumes.

    Requires nibabel. The atlas and CHA volumes must be in the same space
    (alignment is performed beforehand in DSI Studio).
    """
    import nibabel as nib  # imported lazily so the module loads without it
    atlas_data = nib.load(atlas_nii).get_fdata().astype(int)
    cha_data = nib.load(cha_nii).get_fdata().astype(int)
    atlas_labels = read_labels(atlas_labels_txt)
    return containment_from_arrays(atlas_data, cha_data, atlas_labels,
                                   cha_labels_txt, verbose=verbose)


# ---------------------------------------------------------------------------
# Optional specificity correction (matches adjust_containment in the notebook)
# ---------------------------------------------------------------------------

def cha_volume_fractions(cha_data, cha_labels_txt, cha_rois):
    """Volume fraction of each CHA region relative to total labelled volume."""
    cha_labels = read_labels(cha_labels_txt)
    name_to_ids = {}
    for idx, row in cha_labels.iterrows():
        name = row[1]
        if name in cha_rois:
            name_to_ids.setdefault(name, []).append(idx)
    volumes, total = {}, 0
    for name in cha_rois:
        count = sum(np.sum(cha_data == rid) for rid in name_to_ids.get(name, []))
        volumes[name] = count
        total += count
    return {name: (count / total if total > 0 else 0) for name, count in volumes.items()}


def adjust_containment(W, vol_fracs):
    """Specificity-corrected max containment: (raw - expected) / (1 - expected).

    expected is the volume fraction of the best-matching CHA region. Corrects
    for inflation caused by large CHA parcels. Returns a per-region Series.
    """
    cols = list(W.columns)
    valid = W[W.max(axis=1) > 0]
    raw_max = valid.max(axis=1)
    best_idx = valid.values.argmax(axis=1)
    expected = np.array([vol_fracs[cols[i]] for i in best_idx])
    adjusted = np.clip((raw_max.values - expected) / (1 - expected), 0, 1)
    return pd.Series(adjusted, index=raw_max.index)


# ---------------------------------------------------------------------------
# Assignment and projection
# ---------------------------------------------------------------------------

def assign_to_cha(W):
    """Label each source region by its CHA region of maximum containment.

    Returns a DataFrame with the chosen CHA region and its containment
    fraction for each source region that has any nonzero overlap.
    """
    valid = W[W.max(axis=1) > 0]
    return pd.DataFrame({"cha_region": valid.idxmax(axis=1),
                         "containment": valid.max(axis=1)})


def project_connectome_to_cha(F, W, label_map=None, drop_prefix="dummy"):
    """Project a connectome from source-atlas space into CHA space.

        F_CHA = W.T @ F @ W

    F           connectome in source space (source regions x source regions).
    W           containment table (source regions x CHA regions).
    label_map   optional dict harmonising source labels in F before alignment,
                for cases where F and W spell shared regions differently
                (for example {"A1/2": "A1/A2"}).
    drop_prefix source labels beginning with this are excluded (placeholders).

    Returns the connectome in CHA space (CHA regions x CHA regions).
    """
    if label_map:
        F = F.rename(index=label_map, columns=label_map)
    common = [c for c in sorted(set(F.index) & set(W.index))
              if not str(c).startswith(drop_prefix)]
    if not common:
        raise ValueError("no shared regions between connectome and containment "
                         "table after harmonisation; check labels or label_map")
    F_a = F.loc[common, common].fillna(0)
    W_a = W.loc[common].fillna(0)
    W_a = W_a[W_a.columns[W_a.sum(axis=0) > 0]]
    F_cha = W_a.values.T @ F_a.values @ W_a.values
    return pd.DataFrame(F_cha, index=W_a.columns, columns=W_a.columns)


# ---------------------------------------------------------------------------
# Command-line entry point
# ---------------------------------------------------------------------------

def _cmd_containment(args):
    W = containment_table(args.atlas, args.cha, args.atlas_labels, args.cha_labels,
                          verbose=args.verbose)
    W.to_csv(args.out)
    print(f"wrote containment table {W.shape} to {args.out}", flush=True)


def _cmd_assign(args):
    W = pd.read_csv(args.containment, index_col=0)
    assign_to_cha(W).to_csv(args.out)
    print(f"wrote assignment to {args.out}", flush=True)


def _cmd_project(args):
    F = pd.read_csv(args.connectome, index_col=0)
    W = pd.read_csv(args.containment, index_col=0)
    label_map = None
    if args.label_map:
        with open(args.label_map) as fh:
            label_map = json.load(fh)
    F_cha = project_connectome_to_cha(F, W, label_map=label_map)
    F_cha.to_csv(args.out)
    print(f"wrote CHA-space connectome {F_cha.shape} to {args.out}", flush=True)


def build_parser():
    p = argparse.ArgumentParser(description="Integrate an atlas or connectome into CHA.")
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("containment", help="compute the source-to-CHA containment table")
    c.add_argument("--atlas", required=True, help="source atlas NIfTI label volume")
    c.add_argument("--atlas-labels", required=True, help="source atlas label txt")
    c.add_argument("--cha", required=True, help="CHA NIfTI label volume (same space)")
    c.add_argument("--cha-labels", required=True, help="CHA label txt")
    c.add_argument("--out", required=True, help="output containment table CSV")
    c.add_argument("--verbose", action="store_true")
    c.set_defaults(func=_cmd_containment)

    a = sub.add_parser("assign", help="assign source regions by maximum containment")
    a.add_argument("--containment", required=True, help="containment table CSV")
    a.add_argument("--out", required=True, help="output assignment CSV")
    a.set_defaults(func=_cmd_assign)

    j = sub.add_parser("project", help="project a connectome into CHA space")
    j.add_argument("--connectome", required=True, help="connectome CSV (source x source)")
    j.add_argument("--containment", required=True, help="containment table CSV")
    j.add_argument("--label-map", help="optional JSON dict for source-label harmonisation")
    j.add_argument("--out", required=True, help="output CHA-space connectome CSV")
    j.set_defaults(func=_cmd_project)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()