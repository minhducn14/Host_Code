# Content-Based Filtering (Trang chi tiết sản phẩm)

## 1. Mở rộng thông tin đầu vào cho TF-IDF  
Có thể đưa thêm **category_id** hoặc các thông số chi tiết (**metadata**) như:  
- **brand** (thương hiệu)  
- **camera resolution** (độ phân giải camera)  
- **battery size** (dung lượng pin)  

Cập nhật cách xử lý dữ liệu:  

```python
df['combined_features'] = df['name'] + ' ' + df['category_id'].astype(str)
tfidf_matrix = tfidf.fit_transform(df['combined_features'])
```

## 2. Thêm fallback khi dữ liệu thưa  
Nếu người dùng chưa xem nhiều sản phẩm, có thể hiển thị **category-wide popular items** (các sản phẩm phổ biến trong cùng danh mục) để đảm bảo có đủ gợi ý.  

## 3. Linh hoạt số lượng sản phẩm gợi ý  
Hiện tại, chỉ lấy 5 sản phẩm cuối cùng từ danh sách (`[-6:-1]`), điều này có thể quá ít. Thay vì cố định, có thể **refactor** để số lượng gợi ý linh hoạt với tham số `n_recommendations`:  

### Code cải tiến:  
```python
def recommend_products(product_id, n_recommendations=5):
    # Lấy danh sách sản phẩm tương tự đã được tính toán trước đó
    similar_products = get_similar_products(product_id)
    
    # Chỉ lấy số lượng sản phẩm theo tham số n_recommendations
    return similar_products[-(n_recommendations + 1):-1]
```

### Lợi ích của cách tiếp cận này:  
✔ **Linh hoạt**: Có thể hiển thị số lượng sản phẩm gợi ý tùy theo UI (mobile, desktop).  
✔ **Tùy chỉnh dễ dàng**: Không cần sửa code thủ công khi muốn thay đổi số lượng gợi ý.  

---

# 2. Collaborative Filtering (Trang Giỏ Hàng)

## Logic Hiện Tại:
Hệ thống lấy dữ liệu hành vi khách hàng (**customer_id, product_id, action_type**) từ database, dự kiến sẽ xây dựng ma trận user-item để tính toán độ tương đồng.

### Có Hợp Lý Không?
✔ **Có**, vì Collaborative Filtering rất phù hợp với trang giỏ hàng, giúp gợi ý sản phẩm (vd: điện thoại, phụ kiện) dựa trên những gì khách hàng tương tự đã thêm vào giỏ.

## Cải Tiến Tiềm Năng:

### 1. Hoàn Thiện Logic:
Hãy đảm bảo code bao gồm:
- Xây dựng **ma trận user-item** (hàng: customer_id, cột: product_id, giá trị: action counts/ratings).
- Tính **user-user** hoặc **item-item similarity** dùng cosine similarity.
- Trả về **top-N recommendations**.

#### Example Code:
```python
df = pd.read_sql(query, db.engine, params={"customer_id": customer_id})
user_item_matrix = df.pivot_table(index='customer_id', columns='product_id', values='action_type', aggfunc='count', fill_value=0)
similarity = cosine_similarity(user_item_matrix)
# Logic to get top-N products for customer_id
```

### 2. Gán Trọng Số Action:
- **View = 1**, **Add-to-Basket = 3**, **Purchase = 5**.
- Giúp đề cao sản phẩm chất lượng hơn.

### 3. Xử Lý Cold Start:
- Khách hàng mới: Kết hợp gợi ý theo **sản phẩm phổ biến** hoặc **content-based filtering**.

---

# 3. Hybrid Recommendation (Trang Chủ)

## Logic Hiện Tại:
Hệ thống kết hợp kết quả từ **collaborative filtering** và **content-based filtering** bằng cách hợp nhất tập hợp (set) và trả về danh sách kết hợp.

### Có Hợp Lý Không?
✔ **Có**, vì cách này giúp người dùng nhận được cả gợi ý cá nhân hóa và gợi ý theo sản phẩm tương tự.

## Cải Tiến Tiềm Năng:

### 1. Áp Dụng Trọng Số (Weighted Hybrid Approach):
Thay vì chỉ lấy hợp của hai danh sách, có thể gán trọng số dựa trên độ tin cậy:
- **Collaborative Filtering** có thể ưu tiên hơn cho người dùng thường xuyên.
- **Content-Based Filtering** phù hợp hơn với người dùng mới.

#### Code Cải Tiến:
```python
def hybrid_recommendation(db, customer_id, collab_weight=0.6, content_weight=0.4):
    collab_results = collaborative_filtering(db, customer_id)
    content_results = content_based_filtering(db, customer_id)
    
    # Gán điểm cho từng sản phẩm
    scored_results = {prod: collab_weight for prod in collab_results}
    for prod in content_results:
        scored_results[prod] = scored_results.get(prod, 0) + content_weight
    
    # Sắp xếp theo điểm số và trả về danh sách tốt nhất
    return sorted(scored_results.keys(), key=lambda x: scored_results[x], reverse=True)[:5]
```

### 2. Chiến Lược Loại Bỏ Trùng Lặp (Deduplication Strategy):
- Cách dùng `set()` loại bỏ trùng lặp nhưng không ưu tiên kết quả tốt nhất.
- Thay vào đó, sắp xếp danh sách dựa trên điểm số như trên để đảm bảo hiển thị gợi ý chất lượng hơn.

### 3. Điều Chỉnh Theo Ngữ Cảnh (Context Awareness):
- Nếu người dùng **đăng nhập và quay lại nhiều lần**, ưu tiên **collaborative filtering**.
- Nếu người dùng **mới hoặc ẩn danh**, thiên về **content-based filtering** hoặc **sản phẩm thịnh hành**.

---

