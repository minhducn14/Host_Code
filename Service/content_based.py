from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def content_based_filtering(db, customer_id):
    query = """
        SELECT pv.id, pv.name, pv.category_id, ua.customer_id
        FROM products_variants pv
        JOIN UserActions ua ON pv.id = ua.product_id
        WHERE ua.customer_id = :customer_id AND ua.action_type = 'view'
    """
    df = pd.read_sql(query, db.engine, params={"customer_id": customer_id})

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['name'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    indices = pd.Series(df.index, index=df['id'])
    recommended_products = cosine_sim[indices[customer_id]].argsort()[-6:-1][::-1]

    return df['id'].iloc[recommended_products].tolist()
