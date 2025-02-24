from services.collaborative import collaborative_filtering
from services.content_based import content_based_filtering

def hybrid_recommendation(db, customer_id):
    collaborative_results = collaborative_filtering(db, customer_id)
    content_based_results = content_based_filtering(db, customer_id)
    combined_results = list(set(collaborative_results + content_based_results))
    return combined_results
