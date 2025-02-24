import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def collaborative_filtering(db, customer_id):
    query = """
        SELECT customer_id, product_id, action_type 
        FROM UserActions 
        WHERE action_type = 'purchase'
    """
    df = pd.read_sql(query, db.engine)

    # Tạo Pivot Table
    user_product_matrix = df.pivot_table(index='customer_id', columns='product_id', aggfunc='size', fill_value=0)
    
    # Tính toán độ tương đồng giữa khách hàng
    similarity_matrix = cosine_similarity(user_product_matrix)
    similarity_df = pd.DataFrame(similarity_matrix, index=user_product_matrix.index, columns=user_product_matrix.index)

    # Lấy danh sách khách hàng tương tự
    similar_users = similarity_df[customer_id].sort_values(ascending=False)[1:6]
    recommended_products = user_product_matrix.loc[similar_users.index].sum().sort_values(ascending=False).index.tolist()

    return recommended_products[:5]
