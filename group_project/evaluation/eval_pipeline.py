"""
RAG Evaluation Pipeline.
"""

import json
import pandas as pd
from pathlib import Path
import sys
import os

# Cấu hình đường dẫn gốc để có thể import thư mục src/
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

GOLDEN_DATASET_PATH = Path(__file__).parent / "golden_dataset.json"
RESULTS_PATH = Path(__file__).parent / "results.md"


def load_golden_dataset() -> list[dict]:
    """Load golden dataset từ JSON file."""
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_with_ragas(rag_pipeline, golden_dataset: list[dict]) -> pd.DataFrame:
    """
    Evaluate RAG pipeline sử dụng RAGAS.
    """
    try:
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_recall,
            context_precision,
        )
        from datasets import Dataset
    except ImportError:
        print("Vui lòng chạy lệnh: pip install ragas datasets langchain-openai")
        return pd.DataFrame()

    print("\n--- BƯỚC 1: ĐANG LẤY CÂU TRẢ LỜI TỪ AI CHO TỪNG CÂU HỎI ---")
    eval_data = {"question": [], "answer": [], "contexts": [], "ground_truth": []}

    for idx, item in enumerate(golden_dataset):
        question = item["question"]
        expected_answer = item["expected_answer"]
        print(f"Đang xử lý câu {idx + 1}/{len(golden_dataset)}: {question[:50]}...")
        
        try:
            # Gọi hàm của Task 10
            result = rag_pipeline(question)
            
            # Xử lý format trả về của Task 10
            if isinstance(result, dict):
                answer = result.get("answer", "")
                sources = result.get("sources", [])
                contexts = [c.get("content", "") if isinstance(c, dict) else str(c) for c in sources]
            else:
                answer = str(result)
                contexts = ["Tài liệu dự phòng do không đọc được source"]
        except Exception as e:
            print(f"  -> Lỗi gọi pipeline: {e}")
            answer = "Lỗi hệ thống."
            contexts = ["Lỗi không có tài liệu"]

        eval_data["question"].append(question)
        eval_data["answer"].append(answer)
        eval_data["contexts"].append(contexts)
        eval_data["ground_truth"].append(expected_answer)

    print("\n--- BƯỚC 2: RAGAS BẮT ĐẦU CHẤM ĐIỂM (CÓ THỂ MẤT VÀI PHÚT) ---")
    dataset = Dataset.from_dict(eval_data)
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
    )
    
    return result.to_pandas()


def export_results(df: pd.DataFrame):
    """Xuất kết quả đánh giá ra file Markdown"""
    if df.empty:
        print("Không có dữ liệu để xuất báo cáo.")
        return
        
    mean_scores = df[['faithfulness', 'answer_relevancy', 'context_recall', 'context_precision']].mean()
    
    content = "# 📊 Báo Cáo Đánh Giá RAGAS - Chủ Đề Du Lịch\n\n"
    content += "## 1. Điểm số trung bình (Overall Scores)\n\n"
    content += "| Tiêu chí (Metric) | Điểm trung bình |\n"
    content += "|-------------------|-----------------|\n"
    content += f"| Faithfulness (Độ tin cậy) | {mean_scores['faithfulness']:.4f} |\n"
    content += f"| Answer Relevancy (Đúng trọng tâm) | {mean_scores['answer_relevancy']:.4f} |\n"
    content += f"| Context Recall (Độ bao phủ tài liệu) | {mean_scores['context_recall']:.4f} |\n"
    content += f"| Context Precision (Độ chính xác tài liệu) | {mean_scores['context_precision']:.4f} |\n\n"
    
    content += "## 2. Chi tiết từng câu hỏi\n\n"
    for index, row in df.iterrows():
        content += f"### Câu hỏi {index + 1}: {row['question']}\n"
        content += f"- **Câu trả lời chuẩn (Ground Truth):** {row['ground_truth']}\n"
        content += f"- **AI trả lời (Actual Answer):** {row['answer']}\n"
        
        # Xử lý trường hợp có thể bị NaN
        f_score = row.get('faithfulness', 0)
        ar_score = row.get('answer_relevancy', 0)
        cr_score = row.get('context_recall', 0)
        cp_score = row.get('context_precision', 0)
        
        content += f"- **Điểm số:** Faithfulness: `{f_score:.2f}`, Relevancy: `{ar_score:.2f}`, Recall: `{cr_score:.2f}`, Precision: `{cp_score:.2f}`\n\n"

    RESULTS_PATH.write_text(content, encoding="utf-8")
    print(f"\n✅ Đã xuất báo cáo thành công tại: {RESULTS_PATH}")


if __name__ == "__main__":
    from dotenv import load_dotenv
    # Load biến môi trường chứa API Key
    load_dotenv(project_root / ".env")
    
    golden_dataset = load_golden_dataset()
    
    # ⚠️ MẸO QUAN TRỌNG: 
    # Cắt ngắn bộ dữ liệu để test không bị Rate Limit (429 Too Many Requests)
    # Khi nào ghép code xong thật sự, hãy xoá đoạn [:3] đi để chạy đủ 15 câu!
    test_dataset = golden_dataset # Đã mở khoá toàn bộ 15 câu!
    
    print(f"Đã load {len(golden_dataset)} câu hỏi. Đang test thử {len(test_dataset)} câu đầu tiên.")

    try:
        from src.task10_generation import generate_with_citation
        pipeline_func = generate_with_citation
        print("✅ Đã load thành công hàm generate_with_citation từ Task 10.")
    except (ImportError, ModuleNotFoundError):
        print("⚠ Chưa có Task 10. Sẽ chạy bằng Mock Pipeline (Giả lập) để bạn test code RAGAS trước...")
        # Mock pipeline giả lập để Role 5 có thể test eval ngay lập tức
        def pipeline_func(question):
            return {
                "answer": "Hạ Long là một thành phố thuộc tỉnh Quảng Ninh (Thông tin giả lập để test luồng).",
                "sources": [{"content": "Cẩm nang du lịch Quảng Ninh"}]
            }

    # Chạy RAGAS
    df_results = evaluate_with_ragas(pipeline_func, test_dataset)
    
    # Xuất báo cáo
    if not df_results.empty:
        export_results(df_results)

