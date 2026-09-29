import pandas as pd
from Tool.similarity_calculate import generate_corpus_vectors, get_max_similarity
from modules.data_dir import data_file

file_path = data_file("small_talk_dataset.csv")

df = pd.read_csv(file_path, encoding="gbk")
questions = df["Question"].astype(str).tolist()
answers = df["Answer"].astype(str).tolist()

vectors, count_vect, tfidf = generate_corpus_vectors(questions)

def get_response(user_input, threshold=0.25):
    #vectorizer/transformer
    counts = count_vect.transform([user_input])
    user_vec = tfidf.transform(counts)
    sim, idx = get_max_similarity(user_vec, vectors, threshold)
    if idx is not None:
        return answers[idx], sim
    return None, sim

