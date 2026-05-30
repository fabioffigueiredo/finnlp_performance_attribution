"""Serviço que encapsula o pipeline src/ para uso pelo frontend.

Carrega o corpus e treina os modelos uma única vez (lazy warmup) e mantém
tudo em memória para responder requisições de análise sem recarregar.
"""
from __future__ import annotations
import logging
import threading
from typing import Any, Optional

import spacy

from src.coleta_preprocessamento import load_phrasebank, lemmatize_text
from src.modelagem_vetorizacao import (
    build_tfidf, prepare_classification_data, train_svm, train_naive_bayes,
    search_by_similarity, build_lda_model, get_top_words_per_topic,
)
from src.ner_grafo import extract_org_entities, normalize_entities, extract_regex_patterns

_log = logging.getLogger(__name__)
LABELS = ["negative", "neutral", "positive"]


class PipelineService:
    """Singleton de pipeline: warmup carrega corpus + modelos; métodos servem inferência."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._ready = False
        self._df = None
        self._tfidf_vec = None
        self._tfidf_matrix = None
        self._clf = None
        self._clf_vec = None
        self._lda = None
        self._lda_vec = None
        self._lda_terms = None
        self._nlp = None

    def warmup(self) -> None:
        """Carrega corpus e treina modelos uma vez (idempotente, thread-safe)."""
        with self._lock:
            if self._ready:
                return
            _log.info("PipelineService warmup: carregando corpus e treinando modelos...")
            df = load_phrasebank()
            df["text_clean"] = df["text"].apply(lambda t: lemmatize_text(t, "en"))
            self._df = df

            self._tfidf_vec, self._tfidf_matrix = build_tfidf(df["text_clean"].tolist())

            X_tr, _, y_tr, _, clf_vec = prepare_classification_data(df, text_col="text_clean", label_col="label")
            self._clf = train_svm(X_tr, y_tr)
            self._clf_vec = clf_vec

            self._lda, self._lda_vec, _ = build_lda_model(df["text_clean"].tolist())
            terms = self._lda_vec.get_feature_names_out().tolist()
            self._lda_terms = get_top_words_per_topic(self._lda, terms, n_top=5)

            self._nlp = spacy.load("en_core_web_sm")
            self._ready = True
            _log.info("PipelineService pronto.")

    def _ensure(self) -> None:
        if not self._ready:
            self.warmup()

    def analyze(self, text: str, lang: str = "en", top_n: int = 3) -> dict[str, Any]:
        """Analisa um texto: sentimento + confiança + entidades + tópico + busca."""
        self._ensure()
        clean = lemmatize_text(text, lang)

        # Sentimento (decision_function → pseudo-confiança via softmax do score)
        X = self._clf_vec.transform([clean])
        sentiment = str(self._clf.predict(X)[0])
        confidence = self._decision_confidence(X)

        # Entidades ORG normalizadas
        orgs_raw = extract_org_entities(text, self._nlp)
        mapping = normalize_entities(orgs_raw, threshold=4)
        entities = sorted({mapping[o] for o in orgs_raw})

        # Tópico LDA dominante
        topic = self._dominant_topic(clean)

        # Busca semântica
        search = search_by_similarity(
            text, self._tfidf_matrix, self._tfidf_vec,
            self._df["text"].tolist(), lemmatize_text, top_n=top_n, lang=lang,
        )

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "entities": entities,
            "regex": extract_regex_patterns(text),
            "topic": topic,
            "search": search,
        }

    def search(self, query: str, top_n: int = 3) -> list[dict]:
        self._ensure()
        return search_by_similarity(
            query, self._tfidf_matrix, self._tfidf_vec,
            self._df["text"].tolist(), lemmatize_text, top_n=top_n, lang="en",
        )

    def _decision_confidence(self, X) -> float:
        """Converte a maior margem da decision_function em pseudo-probabilidade [0,1]."""
        import numpy as np
        scores = self._clf.decision_function(X)
        arr = np.atleast_2d(scores)
        exp = np.exp(arr - arr.max(axis=1, keepdims=True))
        proba = exp / exp.sum(axis=1, keepdims=True)
        return round(float(proba.max()), 4)

    def _dominant_topic(self, clean_text: str) -> dict:
        """Retorna o tópico LDA dominante do texto + top termos."""
        if not clean_text.strip():
            return {"id": -1, "terms": [], "score": 0.0}
        counts = self._lda_vec.transform([clean_text])
        dist = self._lda.transform(counts)[0]
        top_id = int(dist.argmax())
        terms = self._lda_terms[self._lda_terms["topic"] == f"Tópico {top_id + 1}"]["term"].tolist()
        return {"id": top_id + 1, "terms": terms, "score": round(float(dist.max()), 4)}


# Singleton de processo
PIPELINE = PipelineService()
