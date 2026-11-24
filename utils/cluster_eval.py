from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score, adjusted_rand_score
from scipy.sparse import issparse
import numpy as np

def evaluate_clustering(x, labels, y_true = None):
    mask = labels != -1

    x_valid = x[mask]
    labels_valid = labels[mask]

    n_clusters = len(np.unique(labels_valid))
    noise_percentage = (1 - np.mean(mask)) * 100

    silhouette = np.nan
    davies_bouldin = np.nan
    calinski_harabasz = np.nan
    adjusted_rand = np.nan

    if 2 <= n_clusters < x_valid.shape[0]:
        
        if hasattr(x_valid, "toarray"):
            x_valid = x_valid.toarray()
        
        silhouette = silhouette_score(x_valid, labels_valid, random_state = 42)
        davies_bouldin = davies_bouldin_score(x_valid, labels_valid)
        calinski_harabasz = calinski_harabasz_score(x_valid, labels_valid)

    if y_true is not None:
        adjusted_rand = adjusted_rand_score(
            y_true[mask],
            labels_valid
        )

    return {
        'Clusters': n_clusters,
        'Noise (%)': noise_percentage,
        'Silhouette': silhouette,
        'Davies-Bouldin': davies_bouldin,
        'Calinski-Harabasz': calinski_harabasz,
        'Adjusted Rand Score': adjusted_rand
    }