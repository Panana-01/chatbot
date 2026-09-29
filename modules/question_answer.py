import pandas as pd
from Tool.similarity_calculate import generate_corpus_vectors, get_max_similarity
from modules.data_dir import data_file

qa_path = data_file("question_answer_dataset.csv")

#读取
df = pd.read_csv(qa_path)
questions = df["Question"].astype(str).tolist()
answers = df["Answer"].astype(str).tolist()

vectors, count_vect, tfidf = generate_corpus_vectors(questions)

def get_response(user_input, threshold=0.1):
    # vectorizer/transformer
    counts = count_vect.transform([user_input])
    user_vec = tfidf.transform(counts)
    sim, idx = get_max_similarity(user_vec, vectors, threshold)
    if idx is not None:
        return answers[idx], sim
    return None, sim

