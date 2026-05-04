from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

model = SentenceTransformer("all-MiniLM-L6-v2")

def semantic_icp(df):
    texts = (
        df["company_name"].astype(str) + " " +
        df["raw_text"].fillna("").astype(str)
    ).tolist()

    embeddings = model.encode(texts, normalize_embeddings=True)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df["icp_cluster"] = kmeans.fit_predict(embeddings)

    mapping = {
        0: "LOW INTENT - BROKER",
        1: "MID INTENT - SERVICE PROVIDER",
        2: "HIGH INTENT - INSTALLER",
        3: "BUYER READY - LOCAL CONTRACTOR"
    }

    df["icp_segment"] = df["icp_cluster"].map(mapping)
    return df