# Tool/similarity_calculate.py
from typing import List, Tuple, Optional
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity


def generate_corpus_vectors(texts: List[str]) -> Tuple[csr_matrix, CountVectorizer, TfidfTransformer]:

    if texts is None:
        texts = []
    texts = [t if isinstance(t, str) else "" for t in texts]

    count_vect = CountVectorizer()
    counts = count_vect.fit_transform(texts)         # shape=(n_samples, n_features)

    tfidf = TfidfTransformer()
    vectors = tfidf.fit_transform(counts)            # shape=(n_samples, n_features)

    return vectors, count_vect, tfidf


def generate_text_vectors(input_text: str,
                          count_vect: CountVectorizer,
                          tfidf_transformer: TfidfTransformer) -> csr_matrix:

   # 只使用传入的向量器/转换器将单条文本转成 TF-IDF 向量
    #绝不访问/修改任何全局对象。

    if count_vect is None or tfidf_transformer is None:
        raise ValueError("count_vect and tfidf_transformer must be provided and fitted.")
    if input_text is None:
        input_text = ""

    counts = count_vect.transform([input_text])      # shape=(1, n_features_of_count_vect)
    vector = tfidf_transformer.transform(counts)     # shape=(1, n_features_of_count_vect)
    return vector


def get_max_similarity(vector: csr_matrix,
                       vectors: csr_matrix,
                       threshold: float = 0.0) -> Tuple[float, Optional[int]]:

 #计算余弦相似度并返回 (max_sim, index)。加入严格的维度与空检查，避免崩溃
    # 基础空/零稀疏检查
    if vector is None or vectors is None:
        return 0.0, None
    if getattr(vector, "nnz", 0) == 0 or getattr(vectors, "nnz", 0) == 0:
        return 0.0, None
    # 维度兼容检查
    if vector.shape[1] != vectors.shape[1]:

        return 0.0, None

    sims = cosine_similarity(vector, vectors)        # shape=(1, n_samples)
    idx = int(np.argmax(sims))
    sim = float(sims[0, idx])

    if sim < threshold:
        return 0.0, None
    return sim, idx
