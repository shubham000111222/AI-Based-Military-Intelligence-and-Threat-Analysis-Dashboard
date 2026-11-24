"""
Group profiling and behavioral clustering module for threat actors.
Filters groups with at least 20 incidents (excluding 'Unknown').
Builds high-dimensional behavioral vectors:
- Attack-type shares
- Target-type shares
- Regional distribution shares
- Mean and median casualty statistics
- Active operational lifespan
Clusters groups with KMeans and projects to 2D with PCA.
Extracts deep dossier profile cards for individual militant factions.
"""

import logging
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from src.config import RANDOM_SEED, UNKNOWN_GROUP_NAME

logger = logging.getLogger(__name__)

# Minimum threshold of recorded incidents to qualify for behavioral profiling
MIN_GROUP_INCIDENTS: int = 20


def extract_group_behavior_vectors(
    df: pd.DataFrame,
    min_incidents: int = MIN_GROUP_INCIDENTS,
) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Construct standardized behavioral feature vectors for militant factions
    with at least min_incidents recorded attacks.

    Parameters
    ----------
    df : pd.DataFrame
        GTD DataFrame.
    min_incidents : int
        Minimum incident cutoff (default: 20).

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, List[str]]
        1. metadata_df: Group metadata (name, count, fatalities, active years).
        2. feature_matrix: Normalized behavior feature vectors.
        3. feature_names: List of column names in behavior vectors.
    """
    # Exclude Unknown
    known_mask = (df["gname"] != UNKNOWN_GROUP_NAME) & (df["gname"].notna()) & (df["gname"] != "")
    known_df = df[known_mask].copy()

    # Incident counts
    grp_counts = known_df["gname"].value_counts()
    valid_groups = grp_counts[grp_counts >= min_incidents].index.tolist()

    if len(valid_groups) == 0:
        logger.warning("No groups met the %d incident cutoff. Falling back to top 10 groups.", min_incidents)
        valid_groups = grp_counts.head(10).index.tolist()

    sub = known_df[known_df["gname"].isin(valid_groups)].copy()

    # 1. Attack type shares
    attack_shares = (
        pd.crosstab(sub["gname"], sub["attacktype1_txt"], normalize="index")
        .add_prefix("attk_")
    )

    # 2. Target type shares
    target_shares = (
        pd.crosstab(sub["gname"], sub["targtype1_txt"], normalize="index")
        .add_prefix("targ_")
    )

    # 3. Regional shares
    region_shares = (
        pd.crosstab(sub["gname"], sub["region_txt"], normalize="index")
        .add_prefix("reg_")
    )

    # 4. Casualty metrics and active years
    meta_records = []
    for g in valid_groups:
        g_sub = sub[sub["gname"] == g]
        tot_inc = len(g_sub)
        tot_kill = float(g_sub["nkill"].sum())
        tot_wound = float(g_sub["nwound"].sum())
        tot_cas = float(g_sub["ncasualty"].sum()) if "ncasualty" in g_sub.columns else tot_kill + tot_wound

        mean_cas = round(float(g_sub["ncasualty"].mean()), 2) if "ncasualty" in g_sub.columns else round(tot_cas / tot_inc, 2)
        med_cas = round(float(g_sub["ncasualty"].median()), 2) if "ncasualty" in g_sub.columns else 0.0

        min_yr = int(g_sub["iyear"].min())
        max_yr = int(g_sub["iyear"].max())
        active_span = max_yr - min_yr + 1
        active_yrs_count = g_sub["iyear"].nunique()

        top_country = g_sub["country_txt"].mode()[0] if not g_sub["country_txt"].empty else "Unknown"
        top_region = g_sub["region_txt"].mode()[0] if not g_sub["region_txt"].empty else "Unknown"

        meta_records.append({
            "gname": g,
            "incidents": tot_inc,
            "fatalities": int(tot_kill),
            "wounded": int(tot_wound),
            "total_casualties": int(tot_cas),
            "mean_casualties": mean_cas,
            "median_casualties": med_cas,
            "start_year": min_yr,
            "end_year": max_yr,
            "active_span": active_span,
            "active_years_count": active_yrs_count,
            "primary_country": top_country,
            "primary_region": top_region,
        })

    meta_df = pd.DataFrame(meta_records).set_index("gname")

    # Combine behavioral features
    behavior_df = pd.concat([attack_shares, target_shares, region_shares], axis=1).fillna(0.0)

    # Add numeric features (log-transformed for scaling balance)
    behavior_df["feat_mean_casualties"] = np.log1p(meta_df["mean_casualties"])
    behavior_df["feat_median_casualties"] = np.log1p(meta_df["median_casualties"])
    behavior_df["feat_active_span"] = meta_df["active_span"]

    # Realign index
    meta_df = meta_df.loc[behavior_df.index]

    return meta_df, behavior_df, behavior_df.columns.tolist()


def label_cluster_heuristically(
    cluster_means: pd.Series,
    feature_names: List[str],
) -> str:
    """
    Assign a descriptive tactical label to a behavioral cluster
    based on dominant tactical and target dimensions.
    """
    # Find dominant attack prefix
    attk_cols = [c for c in feature_names if c.startswith("attk_")]
    targ_cols = [c for c in feature_names if c.startswith("targ_")]

    top_attk = cluster_means[attk_cols].idxmax().replace("attk_", "") if attk_cols else "Unknown"
    top_targ = cluster_means[targ_cols].idxmax().replace("targ_", "") if targ_cols else "General"

    mean_cas = cluster_means.get("feat_mean_casualties", 0.0)
    high_lethality = mean_cas > 1.5

    if "Bombing" in top_attk:
        return "High-Lethality Explosive Campaigners" if high_lethality else "Asymmetric Bombing Factions"
    elif "Assault" in top_attk:
        return "Armed Insurgent Militias" if "Military" in top_targ or "Police" in top_targ else "Armed Guerrilla Units"
    elif "Assassination" in top_attk:
        return "Targeted VIP Assassination Operatives"
    elif "Kidnapping" in top_attk or "Hostage" in top_attk:
        return "Hostage-Taking & Extortion Syndicates"
    elif "Facility" in top_attk:
        return "Infrastructure & Logistics Saboteurs"
    else:
        return f"Regional Factions ({top_attk})"


def cluster_and_project_groups(
    df: pd.DataFrame,
    min_incidents: int = MIN_GROUP_INCIDENTS,
    n_clusters: int = 4,
    random_seed: int = RANDOM_SEED,
) -> Tuple[pd.DataFrame, Dict[int, str]]:
    """
    Execute KMeans clustering and 2D PCA projection on group behavior vectors.

    Parameters
    ----------
    df : pd.DataFrame
        GTD DataFrame.
    min_incidents : int
        Minimum incident cutoff (default: 20).
    n_clusters : int
        Number of behavioral clusters (default: 4).

    Returns
    -------
    Tuple[pd.DataFrame, Dict[int, str]]
        1. Comprehensive DataFrame with group metadata, cluster ID, cluster label, pca_x, pca_y.
        2. Mapping of cluster ID -> descriptive tactical label.
    """
    meta_df, behavior_df, feat_cols = extract_group_behavior_vectors(df, min_incidents=min_incidents)

    k = min(n_clusters, len(behavior_df))
    if k < 2:
        # Trivial single-cluster fallback
        meta_df["cluster_id"] = 0
        meta_df["cluster_label"] = "General Factions"
        meta_df["pca_x"] = 0.0
        meta_df["pca_y"] = 0.0
        return meta_df.reset_index(), {0: "General Factions"}

    scaler = StandardScaler()
    scaled_feats = scaler.fit_transform(behavior_df)

    # KMeans clustering
    km = KMeans(n_clusters=k, random_state=random_seed, n_init=10)
    cluster_labels = km.fit_predict(scaled_feats)
    meta_df["cluster_id"] = cluster_labels

    # Label clusters heuristically
    cluster_name_map: Dict[int, str] = {}
    for cid in range(k):
        sub_c = behavior_df[meta_df["cluster_id"] == cid]
        means = sub_c.mean()
        label = label_cluster_heuristically(means, feat_cols)
        cluster_name_map[cid] = label

    meta_df["cluster_label"] = meta_df["cluster_id"].map(cluster_name_map)

    # 2D PCA projection
    pca = PCA(n_components=2, random_state=random_seed)
    coords_2d = pca.fit_transform(scaled_feats)

    meta_df["pca_x"] = coords_2d[:, 0].round(3)
    meta_df["pca_y"] = coords_2d[:, 1].round(3)

    return meta_df.reset_index(), cluster_name_map


def get_group_dossier(
    df: pd.DataFrame,
    group_name: str,
) -> Dict[str, Any]:
    """
    Extract comprehensive operational dossier for an individual militant faction:
    - Active operational span
    - Cumulative casualties and lethality statistics
    - Top operational sovereign states
    - Attack tactics breakdown
    - Target sectors breakdown
    - Annual incident trajectory.
    """
    g_sub = df[df["gname"] == group_name].copy()
    if g_sub.empty:
        return {"gname": group_name, "error": "No recorded incidents found for this group."}

    tot_inc = len(g_sub)
    tot_kill = int(g_sub["nkill"].sum())
    tot_wound = int(g_sub["nwound"].sum())
    tot_cas = int(g_sub["ncasualty"].sum()) if "ncasualty" in g_sub.columns else tot_kill + tot_wound

    min_yr = int(g_sub["iyear"].min())
    max_yr = int(g_sub["iyear"].max())

    # Top countries
    top_countries = (
        g_sub["country_txt"].value_counts().head(5).reset_index()
    )
    top_countries.columns = ["country", "count"]

    # Top tactics
    top_tactics = (
        g_sub["attacktype1_txt"].value_counts().head(5).reset_index()
    )
    top_tactics.columns = ["tactic", "count"]

    # Top targets
    top_targets = (
        g_sub["targtype1_txt"].value_counts().head(5).reset_index()
    )
    top_targets.columns = ["target", "count"]

    # Timeline series
    timeline = (
        g_sub.groupby("iyear")
        .agg(incidents=("iyear", "count"), fatalities=("nkill", "sum"))
        .reset_index()
    )

    return {
        "gname": group_name,
        "total_incidents": tot_inc,
        "total_fatalities": tot_kill,
        "total_wounded": tot_wound,
        "total_casualties": tot_cas,
        "mean_fatalities_per_inc": round(tot_kill / tot_inc, 2),
        "mean_casualties_per_inc": round(tot_cas / tot_inc, 2),
        "start_year": min_yr,
        "end_year": max_yr,
        "active_span": max_yr - min_yr + 1,
        "active_years_count": g_sub["iyear"].nunique(),
        "top_countries": top_countries.to_dict(orient="records"),
        "top_tactics": top_tactics.to_dict(orient="records"),
        "top_targets": top_targets.to_dict(orient="records"),
        "timeline": timeline,
    }
