import pandas as pd
from Tool.similarity_calculate import generate_corpus_vectors, get_max_similarity
from modules.data_dir import data_file

data_path = data_file("intent_management.csv")
intent_df = pd.read_csv(data_path)

intents = intent_df['intent'].astype(str).tolist()
examples = intent_df['example'].astype(str).tolist()

# 生成本模块专属的向量空间
intent_vectors, intent_count_vect, intent_tfidf = generate_corpus_vectors(examples)

def match_intent(user_input, threshold=0.25):
    # vectorizer/transformer
    counts = intent_count_vect.transform([user_input])
    user_vector = intent_tfidf.transform(counts)
    sim, idx = get_max_similarity(user_vector, intent_vectors, threshold)
    if idx is not None:
        return intents[idx], sim
    return None, 0
