# 📊 Báo Cáo Đánh Giá RAGAS - Chủ Đề Du Lịch

## 1. Điểm số trung bình (Overall Scores)

| Tiêu chí (Metric) | Điểm trung bình |
|-------------------|-----------------|
| Faithfulness (Độ tin cậy) | 0.6270 |
| Answer Relevancy (Đúng trọng tâm) | 0.6045 |
| Context Recall (Độ bao phủ tài liệu) | 0.8571 |
| Context Precision (Độ chính xác tài liệu) | 0.8885 |

## 2. Chi tiết từng câu hỏi

### Câu hỏi 1: Thời điểm lý tưởng nhất để đi du lịch biển Đồ Sơn, Hải Phòng là vào tháng mấy?
- **Câu trả lời chuẩn (Ground Truth):** Thời điểm đẹp nhất là mùa hè từ tháng 5 đến tháng 8 vì trời nắng, ít mưa. Tuy nhiên nếu muốn xem lễ hội chọi trâu thì nên đi vào tháng 9 (mùng 9/8 Âm lịch).
- **AI trả lời (Actual Answer):** Thời điểm lý tưởng nhất để đi du lịch biển Đồ Sơn, Hải Phòng là vào mùa hè, từ tháng 5 đến tháng 8, khi trời nắng và ít mưa. Tuy nhiên, từ tháng 9, biển bắt đầu lạnh, nhưng đây cũng là dịp khách đến Đồ Sơn vì diễn ra lễ hội chọi trâu. Từ tháng 10 đến tháng 4 năm sau, thời tiết không thích hợp để tắm biển. (Source: article_10.md)
- **Điểm số:** Faithfulness: `nan`, Relevancy: `0.88`, Recall: `1.00`, Precision: `nan`

### Câu hỏi 2: Có những hãng xe khách nào đi thẳng từ Hà Nội đến Đồ Sơn?
- **Câu trả lời chuẩn (Ground Truth):** Có các hãng như Hải Âu, Hoàng Long, Limousine Hải Phòng Travel đi thẳng đến Đồ Sơn.
- **AI trả lời (Actual Answer):** Có nhiều hãng xe khách từ Hà Nội đến thẳng Đồ Sơn mà không cần qua Hải Phòng, bao gồm các hãng như Hải Âu, Hoàng Long, và Limousine Hải Phòng Travel. Giá vé dao động từ 150.000 VNĐ đến 250.000 VNĐ/chiều. (Source: article_10.md)
- **Điểm số:** Faithfulness: `1.00`, Relevancy: `0.88`, Recall: `1.00`, Precision: `1.00`

### Câu hỏi 3: Dinh thự Bảo Đại ở Đồ Sơn được xây dựng từ năm nào và có đặc điểm gì?
- **Câu trả lời chuẩn (Ground Truth):** Dinh thự được xây dựng năm 1928, nằm trên đồi Vung cao 40m. Đây là công trình hình bát giác, kiến trúc Pháp đặc trưng với 2 tầng và 1 hầm.
- **AI trả lời (Actual Answer):** Dinh thự Bảo Đại ở Đồ Sơn được xây dựng vào năm 1928. Đây là dinh thự duy nhất của Bảo Đại ở miền Bắc, nằm ở độ cao gần 40 m so với mặt nước biển. Dinh có diện tích 1.000 m2 và nằm trong khuôn viên rộng hơn 3.700 m2 trên đỉnh đồi Vung. Công trình được xây theo hình bát giác, kiến trúc Pháp đặc trưng với hai tầng và một hầm, móng được kè đá ong (Source: article_10.md).
- **Điểm số:** Faithfulness: `1.00`, Relevancy: `0.89`, Recall: `1.00`, Precision: `0.87`

### Câu hỏi 4: Khu du lịch Đồi Rồng ở Đồ Sơn có những bãi tắm và công viên gì?
- **Câu trả lời chuẩn (Ground Truth):** Có bãi biển nhân tạo, công viên nước Thuỷ Tinh, công viên Ánh Sáng Dragon Lighting Park và rừng ngập mặn Dragon Mangrove Forest.
- **AI trả lời (Actual Answer):** Khu du lịch Đồi Rồng ở Đồ Sơn là khu du lịch phức hợp hiện đại nhất, đón khách từ mùa hè 2020. Khu này có bãi biển nhân tạo dài hơn 1 km và rộng 23 ha, cùng với nhiều tiện ích như khách sạn và khu vui chơi. Khách lưu trú tại Đồi Rồng được sử dụng miễn phí các tiện ích, trong khi khách tham quan có thể mua vé vào công viên nước Thủy Tinh, bãi biển Rồng, công viên Ánh Sáng Dragon Lighting Park và rừng ngập mặn Dragon Mangrove Forest để trải nghiệm đa dạng trò chơi hấp dẫn. (Source: article_10.md)
- **Điểm số:** Faithfulness: `0.50`, Relevancy: `nan`, Recall: `1.00`, Precision: `nan`

### Câu hỏi 5: Khi đến Hà Giang, con đèo nào nổi tiếng nhất mà dân phượt thường chinh phục?
- **Câu trả lời chuẩn (Ground Truth):** Đèo Mã Pì Lèng là con đèo nổi tiếng nhất và nguy hiểm bậc nhất nằm trên con đường Hạnh Phúc nối liền Đồng Văn và Mèo Vạc.
- **AI trả lời (Actual Answer):** Khi đến Hà Giang, con đèo nổi tiếng nhất mà dân phượt thường chinh phục là đèo Mã Pì Lèng. Đây được biết đến là một trong những con đèo hiểm trở bậc nhất khu vực vùng núi phía Bắc, nối liền hai bờ Đồng Văn và Mèo Vạc với tổng chiều dài lên đến 20km. Mã Pì Lèng được mệnh danh là một trong “tứ đại đỉnh đèo” của núi phía Bắc và là một trong những địa điểm được nhiều tín đồ du lịch tự túc khao khát chinh phục nhất (Source: cam-nang-du-lich-ha-giang.md).
- **Điểm số:** Faithfulness: `1.00`, Relevancy: `0.83`, Recall: `nan`, Precision: `0.81`

### Câu hỏi 6: Thời điểm nào trong năm thích hợp nhất để ngắm hoa tam giác mạch ở Hà Giang?
- **Câu trả lời chuẩn (Ground Truth):** Tháng 10 đến tháng 11 là thời điểm hoa tam giác mạch nở rộ đẹp nhất ở Hà Giang.
- **AI trả lời (Actual Answer):** Thời điểm thích hợp nhất để ngắm hoa tam giác mạch ở Hà Giang là từ cuối tháng 10 đến đầu tháng 11. Đây được xem là thời điểm khi mùa hoa tam giác mạch bắt đầu đổ về, mang đến cảnh sắc rực rỡ dưới tiết trời se lạnh, thu hút hàng ngàn du khách đến tham quan. (Source: article_02.md)
- **Điểm số:** Faithfulness: `1.00`, Relevancy: `0.88`, Recall: `1.00`, Precision: `1.00`

### Câu hỏi 7: Từ Hà Nội đi Sapa bằng tàu hỏa thì điểm dừng cuối cùng là ga nào?
- **Câu trả lời chuẩn (Ground Truth):** Điểm dừng cuối cùng của tàu hỏa là ga Lào Cai. Sau đó du khách phải đi xe buýt hoặc taxi khoảng 1 tiếng nữa để lên trung tâm thị xã Sapa.
- **AI trả lời (Actual Answer):** Từ Hà Nội đi Sapa bằng tàu hỏa, điểm dừng cuối cùng là ga Lào Cai. Sau khi đến ga Lào Cai, bạn có thể tiếp tục di chuyển đến trung tâm Sa Pa bằng xe buýt hoặc taxi, giá khoảng 55.000 đồng/lượt, quãng đường chưa đến 2 km quanh khu Nhà thờ đá (Source: article_05.md).
- **Điểm số:** Faithfulness: `0.67`, Relevancy: `nan`, Recall: `1.00`, Precision: `1.00`

### Câu hỏi 8: Khu du lịch Tràng An ở Ninh Bình có mấy tuyến đò và mất bao nhiêu thời gian di chuyển?
- **Câu trả lời chuẩn (Ground Truth):** Tràng An thường có 3 tuyến đò chính, mỗi tuyến mất khoảng 2.5 đến 3 tiếng di chuyển qua các hang động và đền đài.
- **AI trả lời (Actual Answer):** Tôi không thể xác minh thông tin này từ nguồn hiện có.
- **Điểm số:** Faithfulness: `nan`, Relevancy: `0.00`, Recall: `1.00`, Precision: `0.68`

### Câu hỏi 9: Thác Bản Giốc nằm ở tỉnh nào và có điểm gì đặc biệt về biên giới?
- **Câu trả lời chuẩn (Ground Truth):** Thác Bản Giốc nằm ở tỉnh Cao Bằng. Điểm đặc biệt là phần thác chính nằm trên đường biên giới giao điểm giữa Việt Nam và Trung Quốc.
- **AI trả lời (Actual Answer):** Thác Bản Giốc nằm ở xã Đàm Thủy, huyện Trùng Khánh, tỉnh Cao Bằng. Đây là một trong những thác nước lớn và đẹp nhất Đông Nam Á, có vị trí đặc biệt nằm trên đường biên giới tự nhiên giữa Việt Nam và Trung Quốc. Phần thác bên trái và nửa phía tây của thác bên phải thuộc chủ quyền của Việt Nam, trong khi nửa phía đông của thác bên phải thuộc chủ quyền của Trung Quốc. Thác Bản Giốc không chỉ nổi tiếng với vẻ đẹp hùng vĩ mà còn là biểu tượng cho sự giao thoa văn hóa giữa hai quốc gia. (Nguồn: article_06.md)
- **Điểm số:** Faithfulness: `nan`, Relevancy: `0.89`, Recall: `1.00`, Precision: `1.00`

### Câu hỏi 10: Quần đảo Cát Bà thuộc tỉnh nào và phương tiện chính ra đảo là gì?
- **Câu trả lời chuẩn (Ground Truth):** Cát Bà thuộc tỉnh Hải Phòng. Phương tiện chính là đi phà từ bến Gót hoặc đi cáp treo vượt biển.
- **AI trả lời (Actual Answer):** Quần đảo Cát Bà thuộc huyện Cát Hải, thành phố Hải Phòng. Để ra đảo Cát Bà, có ba phương án chính: đi tàu cao tốc từ bến Hồng Bàng ra thẳng cảng trung tâm thị trấn, đi xe buýt từ các bến Bính đến thị trấn, hoặc đi xe riêng từ Hải Phòng tới đảo Cát Hải rồi qua sông bằng cáp treo, phà hoặc tàu cao tốc (Source: cam-nang-du-lich-hai-phong-cat-ba.md).
- **Điểm số:** Faithfulness: `0.86`, Relevancy: `0.83`, Recall: `1.00`, Precision: `1.00`

### Câu hỏi 11: Vịnh Hạ Long có những hang động nổi tiếng nào?
- **Câu trả lời chuẩn (Ground Truth):** Hang Sửng Sốt, Động Thiên Cung, Hang Đầu Gỗ và Hang Luồn là những điểm đến nổi tiếng nhất.
- **AI trả lời (Actual Answer):** Tôi không thể xác minh thông tin này từ nguồn hiện có.
- **Điểm số:** Faithfulness: `0.00`, Relevancy: `0.00`, Recall: `0.00`, Precision: `0.80`

### Câu hỏi 12: Món đặc sản bánh cuốn chả mực là của địa phương nào?
- **Câu trả lời chuẩn (Ground Truth):** Đây là món đặc sản nổi tiếng của Hạ Long, tỉnh Quảng Ninh.
- **AI trả lời (Actual Answer):** Tôi không thể xác minh thông tin này từ nguồn hiện có.
- **Điểm số:** Faithfulness: `0.00`, Relevancy: `0.00`, Recall: `1.00`, Precision: `0.59`

### Câu hỏi 13: Lịch trình đi Mộc Châu 2 ngày 1 đêm từ Hà Nội thường có những điểm tham quan nào?
- **Câu trả lời chuẩn (Ground Truth):** Thường ghé Đèo Thung Khe, Rừng thông Bản Áng, Thác Dải Yếm, Đồi chè trái tim và thung lũng mận Nà Ka.
- **AI trả lời (Actual Answer):** Lịch trình đi Mộc Châu 2 ngày 1 đêm từ Hà Nội thường bao gồm các điểm tham quan nổi bật như sau:

- **Ngày 1**: 
  - Bản Pa Phách
  - Lâm Viên Tây Tiến
  - Đồi cỏ 68 Mộc Châu

- **Ngày 2**: 
  - Đồi chè Mộc Châu
  - Khu du lịch Mộc Châu Happy Land

Chi phí ước tính cho chuyến đi này khoảng 2.000.000 VNĐ/người (theo Source: cam-nang-du-lich-son-la-moc-chau.md).
- **Điểm số:** Faithfulness: `0.50`, Relevancy: `0.91`, Recall: `1.00`, Precision: `0.81`

### Câu hỏi 14: Mùa lúa chín ở Mù Cang Chải rơi vào tháng mấy?
- **Câu trả lời chuẩn (Ground Truth):** Mùa lúa chín vàng ở Mù Cang Chải đẹp nhất vào giữa tháng 9 đến giữa tháng 10 hàng năm.
- **AI trả lời (Actual Answer):** Mùa lúa chín ở Mù Cang Chải rơi vào tháng 9 đến tháng 10. Đây là thời điểm nổi tiếng nhất nhưng cũng đông và đắt khách nhất trong năm. (Source: cam-nang-du-lich-yen-bai-mu-cang-chai.md)
- **Điểm số:** Faithfulness: `1.00`, Relevancy: `0.87`, Recall: `1.00`, Precision: `1.00`

### Câu hỏi 15: Cách làm thủ tục xin giấy phép đi vào khu vực biên giới khi du lịch Lạng Sơn?
- **Câu trả lời chuẩn (Ground Truth):** Thủ tục xin giấy phép thường cần mang theo CMND/CCCD và làm việc trực tiếp tại đồn biên phòng quản lý khu vực đó.
- **AI trả lời (Actual Answer):** Tôi không thể xác minh thông tin này từ nguồn hiện có.
- **Điểm số:** Faithfulness: `0.00`, Relevancy: `0.00`, Recall: `0.00`, Precision: `1.00`

