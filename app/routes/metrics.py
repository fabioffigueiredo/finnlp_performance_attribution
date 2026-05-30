"""Métricas ML: aponta para as imagens geradas pelo notebook."""
from __future__ import annotations
from pathlib import Path
from flask import Blueprint, jsonify, send_from_directory

bp = Blueprint("metrics", __name__)

_IMG_DIR = Path(__file__).resolve().parent.parent.parent / "reports" / "images"

_METRIC_IMAGES = {
    "classification": [
        "confusion_matrix_SVM_LinearSVC.png",
        "confusion_matrix_Naive_Bayes.png",
        "classifier_comparison.png",
    ],
    "topics": ["lda_topics_r3.png"],
    "embeddings": ["tsne_r2.png", "tfidf_heatmap_r2.png"],
}


@bp.get("/api/metrics")
def metrics():
    available = {
        cat: [img for img in imgs if (_IMG_DIR / img).exists()]
        for cat, imgs in _METRIC_IMAGES.items()
    }
    return jsonify({"images": available})


@bp.get("/api/metrics/img/<path:filename>")
def metric_image(filename: str):
    return send_from_directory(_IMG_DIR, filename)
