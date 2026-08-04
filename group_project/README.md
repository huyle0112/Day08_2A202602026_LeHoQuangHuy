# Bài Tập Nhóm — Chủ Đề 5: Trợ Lý Hướng Dẫn Viên Du Lịch Thông Minh

## Mục Tiêu

Sau khi hoàn thành bài cá nhân, nhóm ngồi lại để xây dựng **1 trong 2 sản phẩm**:

---

## Yêu cầu 1: Sản phẩm nhóm RAG Chatbot

Xây dựng chatbot trả lời câu hỏi về chính sách thương mại điện tử và hỗ trợ khách hàng liên quan.

**Yêu cầu:**

- Giao diện chat (Streamlit / Gradio / Chainlit)
- Trả lời có citation (dựa trên Task 10)
- Hỗ trợ follow-up questions (conversation memory)
- Hiển thị source documents đã dùng

**Stack gợi ý:**

```
Chainlit/Streamlit → Retrieval (Task 9) → Generation (Task 10) → Display
```

---

## Yêu cầu 2: RAG Evaluation Pipeline

Sử dụng **1 trong 3 framework** sau để evaluate pipeline RAG của nhóm:

### Framework lựa chọn

| Framework                                           | Cài đặt               | Đặc điểm                                      |
| --------------------------------------------------- | ------------------------ | ------------------------------------------------- |
| [DeepEval](https://github.com/confident-ai/deepeval) | `pip install deepeval` | Nhiều metric built-in, dễ integrate với pytest |
| [RAGAS](https://github.com/explodinggradients/ragas) | `pip install ragas`    | Chuẩn industry cho RAG eval, 3 trục chính      |
| [TruLens](https://github.com/truera/trulens)         | `pip install trulens`  | Dashboard UI, feedback functions mạnh            |

### Yêu cầu Evaluation

1. **Tạo Golden Dataset** — tối thiểu 15 cặp Q&A (question, expected_answer, expected_context)
2. **Chạy evaluation** trên toàn bộ golden dataset với các metrics sau:
   - **Faithfulness** — câu trả lời có bám đúng context không?
   - **Answer Relevance** — câu trả lời có đúng câu hỏi không?
   - **Context Recall** — retriever có lấy đủ evidence không?
   - **Context Precision** — trong context lấy về, bao nhiêu % thực sự hữu ích?
3. **So sánh A/B** — chạy eval trên ít nhất 2 config khác nhau (ví dụ: có reranking vs không reranking, hoặc hybrid vs dense-only)
4. **Báo cáo** — bảng điểm + phân tích worst performers + đề xuất cải tiến

Xem code mẫu (DeepEval/RAGAS/TruLens) chi tiết trong `README.md` gốc mục "Yêu cầu 2".

### Deliverable Evaluation

- [ ] File `group_project/evaluation/golden_dataset.json` — 15+ cặp Q&A
- [ ] File `group_project/evaluation/eval_pipeline.py` — script chạy evaluation
- [ ] File `group_project/evaluation/results.md` — bảng điểm + phân tích
- [ ] So sánh A/B ít nhất 2 configs

---

## Yêu Cầu Chung

1. **Tích hợp pipeline** từ bài cá nhân của các thành viên
2. **Demo hoạt động được** trong buổi trình bày (chạy local hoặc deploy)
3. **Evaluation pipeline** chạy được và có báo cáo kết quả
4. **Code push lên repository** chung của nhóm
5. **README** mô tả kiến trúc và phân công (điền bên dưới)

---

## Kiến Trúc Hệ Thống

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#eef2f3', 'edgeLabelBackground':'#fff', 'fontFamily': 'arial', 'clusterBkg': '#f9fbfd', 'clusterBorder': '#cce0ff'}}}%%
graph TD
    classDef data fill:#e3f2fd,stroke:#1e88e5,stroke-width:2px,rx:10px
    classDef process fill:#fff3e0,stroke:#fb8c00,stroke-width:2px,rx:10px
    classDef db fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px
    classDef logic fill:#e8f5e9,stroke:#43a047,stroke-width:2px,rx:10px
    classDef output fill:#ffebee,stroke:#e53935,stroke-width:2px,rx:10px

    subgraph "📂 DỮ LIỆU ĐẦU VÀO"
        A1[📄 Cẩm nang PDF/DOCX]:::data
        A2[🌐 Bài viết Blogger JSON]:::data
        B(⚙️ Tiền xử lý & Markdown):::process
        A1 --> B
        A2 --> B
    end

    subgraph "🗄️ LƯU TRỮ VECTOR & TỪ KHOÁ"
        C[✂️ Chunking 800 ký tự]:::process
        D1[(🔷 ChromaDB Vector)]:::db
        D2[(🔠 BM25 Index)]:::db
        B --> C
        C --> D1
        C --> D2
    end

    subgraph "🔍 LUỒNG TÌM KIẾM HYBRID"
        U((👤 User)):::output -- "Truy vấn" --> Q[❓ Xử lý câu hỏi]:::process
        Q --> E1[🧠 Semantic Search]:::logic
        Q --> E2[⌨️ Lexical Search]:::logic
    
        E1 --> D1
        E2 --> D2
    
        D1 --> F{⚖️ Gộp điểm RRF}:::process
        D2 --> F
    end

    subgraph "🤖 SINH CÂU TRẢ LỜI"
        F -- "Điểm >= 0.48" --> G[🔄 Reordering]:::logic
        F -- "Điểm < 0.48" --> H[📂 PageIndex Fallback]:::process
        H --> G
        G[🔄 Reordering] --> I[✨ LLM Sinh Câu Trả Lời]:::output
        I --> U
    end
  
    subgraph "📱 ỨNG DỤNG & ĐÁNH GIÁ"
        I -.-> UI[💬 Streamlit Web App]:::data
        I -.-> Eval[📊 RAGAS Evaluation]:::data
    end
```

---

## Phân Công Công Việc

| Thành viên          | MSSV        | Nhiệm vụ                            | Trạng thái |
| --------------------- | ----------- | ------------------------------------- | ------------ |
| Lê Hồ Quang Huy     | 2A202602026 | Role 1 (Team Leader & RAG Architect)  | Hoàn thành |
| Nguyễn Tiến Đạt  | 2A202601056 | Role 2 (Data & Dense Search Dev)      | Hoàn thành |
| Nguyễn Nam Phong     | 2A202601320 | Role 3 (Sparse Search & Reranking)    | Hoàn thành |
| Kiều Phúc Huy       | 2A202601678 | Role 4 (Frontend & Chatbot Developer) | Hoàn thành |
| Lã Phan Hoài An     | 2A202601846 | Role 5 (Evaluation & QA Engineer)     | Hoàn thành |

---

## Hướng Dẫn Chạy

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy app
streamlit run app.py
# hoặc
chainlit run app.py
```

---

## Lưu ý

Hãy giữ lại repo này nếu như bạn học track 3 giai đoạn 2, chúng ta sẽ phát triển tiếp dự án lên knowledge graph để khắc phục các câu hỏi hóc búa khi có các câu hỏi khó.
