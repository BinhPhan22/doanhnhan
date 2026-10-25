"""
Dữ liệu nền bắt buộc: 34 tỉnh/thành (theo sắp xếp đơn vị hành chính có hiệu lực từ 12/6/2025),
cây ngành nghề, các văn bản chính sách (bản khung chờ luật sư hoàn thiện), bài viết trang tài trợ, cài đặt chung.
Chạy nhiều lần không tạo trùng.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.directory.models import Province, Sector
from apps.sitecontent.models import DonationSettings, PolicyDocument, PolicyVersion, SiteSettings

# (mã, tên, là thành phố, hợp nhất từ)
PROVINCES = [
    ("ha-noi", "Hà Nội", True, ""),
    ("tp-ho-chi-minh", "TP. Hồ Chí Minh", True, "TP. Hồ Chí Minh, Bà Rịa – Vũng Tàu, Bình Dương"),
    ("hai-phong", "Hải Phòng", True, "Hải Phòng, Hải Dương"),
    ("da-nang", "Đà Nẵng", True, "Đà Nẵng, Quảng Nam"),
    ("can-tho", "Cần Thơ", True, "Cần Thơ, Sóc Trăng, Hậu Giang"),
    ("hue", "Huế", True, ""),
    ("an-giang", "An Giang", False, "An Giang, Kiên Giang"),
    ("bac-ninh", "Bắc Ninh", False, "Bắc Ninh, Bắc Giang"),
    ("ca-mau", "Cà Mau", False, "Cà Mau, Bạc Liêu"),
    ("cao-bang", "Cao Bằng", False, ""),
    ("dak-lak", "Đắk Lắk", False, "Đắk Lắk, Phú Yên"),
    ("dien-bien", "Điện Biên", False, ""),
    ("dong-nai", "Đồng Nai", False, "Đồng Nai, Bình Phước"),
    ("dong-thap", "Đồng Tháp", False, "Đồng Tháp, Tiền Giang"),
    ("gia-lai", "Gia Lai", False, "Gia Lai, Bình Định"),
    ("ha-tinh", "Hà Tĩnh", False, ""),
    ("hung-yen", "Hưng Yên", False, "Hưng Yên, Thái Bình"),
    ("khanh-hoa", "Khánh Hòa", False, "Khánh Hòa, Ninh Thuận"),
    ("lai-chau", "Lai Châu", False, ""),
    ("lam-dong", "Lâm Đồng", False, "Lâm Đồng, Đắk Nông, Bình Thuận"),
    ("lang-son", "Lạng Sơn", False, ""),
    ("lao-cai", "Lào Cai", False, "Lào Cai, Yên Bái"),
    ("nghe-an", "Nghệ An", False, ""),
    ("ninh-binh", "Ninh Bình", False, "Ninh Bình, Hà Nam, Nam Định"),
    ("phu-tho", "Phú Thọ", False, "Phú Thọ, Vĩnh Phúc, Hòa Bình"),
    ("quang-ngai", "Quảng Ngãi", False, "Quảng Ngãi, Kon Tum"),
    ("quang-ninh", "Quảng Ninh", False, ""),
    ("quang-tri", "Quảng Trị", False, "Quảng Trị, Quảng Bình"),
    ("son-la", "Sơn La", False, ""),
    ("tay-ninh", "Tây Ninh", False, "Tây Ninh, Long An"),
    ("thai-nguyen", "Thái Nguyên", False, "Thái Nguyên, Bắc Kạn"),
    ("thanh-hoa", "Thanh Hóa", False, ""),
    ("tuyen-quang", "Tuyên Quang", False, "Tuyên Quang, Hà Giang"),
    ("vinh-long", "Vĩnh Long", False, "Vĩnh Long, Bến Tre, Trà Vinh"),
]

# (tên, biểu tượng, mô tả, mã VSIC tham chiếu, [(phân ngành, mã VSIC)])
# Mã = ngành cấp 2 (2 chữ số) theo Hệ thống ngành kinh tế Việt Nam VSIC 2025 (Quyết định 36/2025/QĐ-TTg,
# hiệu lực 15/11/2025, thay Quyết định 27/2018/QĐ-TTg). Dùng để tham chiếu và lọc dữ liệu;
# khi đăng ký kinh doanh doanh nghiệp dùng mã cấp 4 — biên tập viên đối chiếu tại dangkykinhdoanh.gov.vn.
SECTORS = [
    ("Công nghệ & Phần mềm", "tech", "Nền tảng số, AI, thương mại điện tử", "62, 63",
     [("Phần mềm doanh nghiệp", "62"), ("Thương mại điện tử", "47"), ("Fintech", "66"), ("AI & Dữ liệu", "63"),
      ("Edtech", "85"), ("Marketing số", "73")]),
    ("Sản xuất – Vật liệu", "factory", "Nhà máy, cơ khí, vật liệu xây dựng", "C",
     [("Cơ khí – chế tạo", "25"), ("Vật liệu xây dựng", "23"), ("Dệt may – da giày", "13, 14, 15"),
      ("Bao bì – nhựa", "22")]),
    ("Thương mại – Bán lẻ", "retail", "Chuỗi cửa hàng, phân phối, xuất nhập khẩu", "46, 47",
     [("Chuỗi bán lẻ", "47"), ("Phân phối", "46"), ("Xuất nhập khẩu", "46")]),
    ("F&B – Nhà hàng", "food", "Chuỗi ẩm thực, cà phê, thực phẩm chế biến", "56, 10",
     [("Chuỗi nhà hàng", "56"), ("Cà phê – đồ uống", "56"), ("Thực phẩm chế biến", "10")]),
    ("Xây dựng – Bất động sản", "building", "Thi công, phát triển dự án, nội thất", "41–43, 68",
     [("Thi công xây dựng", "41, 42"), ("Phát triển dự án", "68"), ("Nội thất – kiến trúc", "43")]),
    ("Giáo dục – Đào tạo", "education", "Trường học, đào tạo kỹ năng, edtech", "85",
     [("Trường học", "85"), ("Đào tạo kỹ năng", "85"), ("Ngoại ngữ", "85")]),
    ("Nông nghiệp – Thực phẩm", "agri", "Nông sản sạch, chế biến, chuỗi cung ứng", "01, 03, 10",
     [("Nông sản sạch", "01"), ("Chế biến nông sản", "10"), ("Thủy sản", "03")]),
    ("Dịch vụ – Logistics", "logistics", "Vận tải, kho bãi, dịch vụ doanh nghiệp", "49–53, 82",
     [("Vận tải", "49"), ("Kho bãi", "52"), ("Dịch vụ doanh nghiệp", "82")]),
]

TERMS = """## 1. Phạm vi áp dụng & Tôn chỉ hoạt động
- **doanhnhan.wiki** là nền tảng số phi lợi nhuận lưu giữ, tôn vinh và giới thiệu các gương mặt doanh nhân, doanh nghiệp tiêu biểu của Việt Nam.
- Toàn bộ nội dung hồ sơ, thông tin sự nghiệp, thương hiệu và dấu mốc phát triển được Ban biên tập thu thập, biên soạn từ các nguồn tư liệu uy tín, công khai và **bắt buộc phải được gửi tới chính Doanh nhân / Doanh nghiệp liên quan để cùng tham khảo, đối chiếu, xác nhận và duyệt kỹ lưỡng trước khi chính thức lên bài (xuất bản công khai)**.
- Khi truy cập, tra cứu thông tin hoặc gửi đề xuất trên doanhnhan.wiki, người dùng đồng ý tuân thủ toàn bộ các điều khoản này.

## 2. Quy trình biên soạn & Phê duyệt nội dung
- **Biên soạn cẩn trọng:** Đội ngũ biên tập viên thực hiện việc tổng hợp, biên tập thông tin theo phong cách bách khoa trung lập, khách quan và minh bạch.
- **Duyệt bởi chính chủ thể:** Mọi thông tin nhân thân, hành trình sự nghiệp, số liệu doanh nghiệp trước khi phát hành đều được gửi tham vấn và duyệt bởi chính Doanh nhân hoặc người đại diện ủy quyền hợp pháp của Doanh nghiệp.
- **Kiểm soát xuất bản:** Không có nội dung nào được tự ý đưa lên nếu chưa qua quy trình xác minh nguồn và phê duyệt của Ban biên tập cùng sự đồng thuận từ chủ thể hồ sơ.

## 3. Tài khoản & Góp ý, bổ sung thông tin
- Độc giả xem và tra cứu thông tin trên doanhnhan.wiki hoàn toàn miễn phí và không cần tài khoản.
- Tài khoản quản trị và biên tập viên được cấp duyệt chặt chẽ bởi Ban quản trị nền tảng.
- Bất kỳ cá nhân, doanh nghiệp hoặc đối tác nào muốn bổ sung dấu mốc mới, cung cấp tư liệu hoặc phát hiện thông tin cần điều chỉnh đều có thể gửi qua kênh **Góp ý / Báo thông tin cần cập nhật**. Ban biên tập sẽ phối hợp cùng doanh nghiệp để xác minh và cập nhật minh bạch.

## 4. Quyền sở hữu trí tuệ & Bản quyền
- Thương hiệu, logo, tên thương mại và hình ảnh đại diện của doanh nghiệp, doanh nhân thuộc quyền sở hữu hợp pháp của chính doanh nghiệp và cá nhân đó. doanhnhan.wiki tôn trọng và chỉ sử dụng nhằm mục đích giới thiệu, tôn vinh và phục vụ cộng đồng.
- Video phỏng vấn, phóng sự được nhúng trực tiếp từ các kênh chính thức của đối tác hoặc nền tảng gốc (YouTube, Vimeo, Facebook, TikTok). doanhnhan.wiki không lưu trữ tệp video trái phép.

## 5. Hành vi bị nghiêm cấm
- Nghiêm cấm mạo danh cá nhân, doanh nghiệp, tổ chức hoặc hiệp hội dưới mọi hình thức.
- Cung cấp hoặc phát tán thông tin sai lệch, bịa đặt, bôi nhọ danh dự, uy tín của doanh nhân và doanh nghiệp.
- Mọi hành vi cố tình quấy phá, gửi dữ liệu rác (spam) hoặc can thiệp kỹ thuật trái phép vào hệ thống sẽ bị ngăn chặn và xử lý theo quy định pháp luật.

## 6. Giới hạn trách nhiệm
- doanhnhan.wiki cam kết nỗ lực tối đa để đảm bảo tính chuẩn xác, khách quan của dữ liệu thông qua quy trình phối hợp duyệt bài trực tiếp với doanh nhân và doanh nghiệp.
- Thông tin trên trang phục vụ mục đích tham khảo, nghiên cứu và kết nối cộng đồng; không phải là lời khuyên đầu tư, khuyến nghị tài chính hay bảo lãnh thương mại cho bất kỳ hoạt động kinh doanh nào.

## 7. Đính chính, cập nhật & Gỡ bỏ hồ sơ
- Khi có bất kỳ sự thay đổi nào về thông tin pháp lý, cơ cấu doanh nghiệp hay nguyện vọng cá nhân, chính doanh nhân hoặc đại diện doanh nghiệp có thể gửi yêu cầu đính chính hoặc đề nghị ẩn/gỡ hồ sơ.
- Ban biên tập tiếp nhận và xử lý nhanh chóng trong vòng 24–48 giờ làm việc.

## 8. Cơ chế phối hợp & Thông tin liên hệ
- Ban vận hành & Ban biên tập doanhnhan.wiki
- Email: lienhe@doanhnhan.wiki
- Vận hành kỹ thuật: Digits Technology
"""

DATA = """## 1. Dữ liệu thu thập & Nguyên tắc bảo vệ
- **Hồ sơ doanh nhân & doanh nghiệp:** Họ tên, chức danh, nơi hoạt động, tóm tắt sự nghiệp, dấu mốc và các giải thưởng đạt được. Các thông tin này đều **được tham khảo, đối chiếu và duyệt bởi chính Doanh nhân / Doanh nghiệp trước khi công bố**.
- **Thông tin riêng tư:** Năm sinh, quê quán, email cá nhân... chỉ được hiển thị khi chính chủ thể đồng ý công khai. Doanh nhân có toàn quyền yêu cầu ẩn các thông tin này bất kỳ lúc nào.
- **Thông tin liên hệ góp ý:** Họ tên, số điện thoại, email của người gửi thông tin góp ý — chỉ dùng cho mục đích xác minh và đối chiếu dữ liệu, tuyệt đối không chia sẻ cho bên thứ ba vì mục đích thương mại.

## 2. Mục đích xử lý thông tin
- Xây dựng kho dữ liệu số bách khoa, chuẩn xác và trung thực về cộng đồng doanh nhân Việt Nam.
- Kết nối các hiệp hội doanh nghiệp, tạo cơ hội hợp tác và truyền cảm hứng khởi nghiệp cho thế hệ trẻ.
- Thực hiện công tác đối chiếu, kiểm chứng nguồn tin khi nhận được yêu cầu cập nhật hoặc đính chính từ chính doanh nghiệp.

## 3. Quyền của chủ thể dữ liệu
- Doanh nhân và đại diện doanh nghiệp là chủ thể dữ liệu có toàn quyền:
  1. Xem lại toàn bộ thông tin đang được lưu trữ và hiển thị trên hồ sơ.
  2. Yêu cầu sửa đổi, bổ sung hoặc đính chính thông tin khi có thay đổi.
  3. Yêu cầu ẩn bớt các trường thông tin nhạy cảm hoặc gỡ bỏ hoàn toàn hồ sơ khỏi nền tảng.
- Yêu cầu được gửi trực tiếp qua trang **Yêu cầu về dữ liệu cá nhân** hoặc nút **Góp ý / Báo thông tin** trên chính hồ sơ.

## 4. Bảo mật & Lưu trữ an toàn
- Hệ thống áp dụng các tiêu chuẩn mã hóa dữ liệu hiện đại, kiểm soát truy cập phân quyền nghiêm ngặt giữa đội ngũ kỹ thuật và biên tập viên.
- Toàn bộ lịch sử các lần chỉnh sửa thông tin đều được ghi nhận minh bạch để bảo vệ tính toàn vẹn của dữ liệu.

## 5. Liên hệ phụ trách dữ liệu
- Ban quản trị dữ liệu · doanhnhan.wiki
- Email: lienhe@doanhnhan.wiki
"""

EDITORIAL = """Quy chế này áp dụng cho mọi nội dung trên doanhnhan.wiki: hồ sơ doanh nhân, doanh nghiệp, hiệp hội, sự kiện và video.

## 1. Nguyên tắc chung
- **Trung lập:** viết như bách khoa, ngôi thứ ba, không dùng ngôn ngữ quảng cáo.
- **Có nguồn:** mọi con số, giải thưởng, mốc quan trọng cần nguồn kiểm chứng; chú thích bằng [^1], [^2]… khớp mục Nguồn tham khảo.
- **Duyệt trước khi lên bài:** nội dung được biên soạn, tham khảo và duyệt bởi chính Doanh nghiệp / Doanh nhân trước khi xuất bản.
- **Riêng tư:** không đăng thông tin cá nhân khi chưa được đồng ý; chủ hồ sơ có thể ẩn năm sinh, quê quán, email.

## 2. Quy trình biên soạn & Duyệt bài
1. Tư liệu được thu thập từ nguồn báo chí chính thống, cổng thông tin Đăng ký doanh nghiệp quốc gia hoặc do doanh nghiệp, hiệp hội cung cấp.
2. Biên tập viên tổng hợp, biên soạn bản thảo bài viết theo chuẩn bách khoa.
3. Bản thảo được gửi trực tiếp cho Doanh nhân / Doanh nghiệp để đối chiếu, tham khảo và duyệt nội dung.
4. Chỉ khi Doanh nhân / Doanh nghiệp xác nhận và Ban biên tập kiểm duyệt hoàn tất, hồ sơ mới được công bố chính thức lên hệ thống.
5. Mỗi lần cập nhật nội dung sau đó đều được lưu lịch sử sửa đổi minh bạch.

## 3. Xác minh
- **Đã kiểm tra cơ bản:** đối chiếu thông tin công khai.
- **Đã xác minh:** đối chiếu mã số thuế trên Cổng thông tin quốc gia về đăng ký doanh nghiệp và/hoặc giấy tờ do chính chủ cung cấp.
- **Hiệp hội xác nhận:** hiệp hội đối tác xác nhận hội viên.

## 4. Video
Chỉ nhúng link từ YouTube, Vimeo, Facebook, TikTok; không lưu tệp video. Video có link không còn xem được sẽ tự ẩn.

## 5. Khiếu nại, đính chính
Báo thông tin chưa chính xác qua nút Góp ý / Báo thông tin hoặc trang Liên hệ. Ban biên tập cùng doanh nghiệp đối chiếu và phản hồi trong thời gian sớm nhất.
"""

COOKIE = """doanhnhan.wiki chỉ dùng cookie cần thiết cho hoạt động của trang:

- **sessionid** — giữ trạng thái đăng nhập (chỉ khi bạn đăng nhập).
- **csrftoken** — chống giả mạo yêu cầu khi gửi biểu mẫu.

Trang không dùng cookie quảng cáo. Video nhúng chỉ được tải khi bạn bấm Phát; khi đó nền tảng video (YouTube dùng chế độ youtube-nocookie, Vimeo, Facebook, TikTok) có thể đặt cookie theo chính sách của họ.
"""

DONATION_RULES = """- doanhnhan.wiki chỉ nhận tài trợ qua tài khoản được công bố tại trang **Donate**. Tài khoản mới hoặc thay đổi phải được hai quản trị viên xác nhận.
- Không có mức tài trợ tối thiểu; tài trợ không ảnh hưởng tới việc duyệt, xác minh hay vị trí hiển thị của bất kỳ hồ sơ nào.
- Toàn bộ kinh phí dùng cho hoạt động của trang: máy chủ, bảo mật, biên tập, ghi hình, phát triển tính năng.
- Mọi đóng góp đều được ghi nhận và công khai minh bạch theo quy chế của ban vận hành.
"""

POLICIES = [
    ("dieu-khoan", "Điều khoản sử dụng", True, 1, TERMS,
     "doanhnhan.wiki là trang lưu giữ hồ sơ doanh nhân, doanh nghiệp tiêu biểu Việt Nam.\n"
     "Nội dung được biên soạn, tham khảo và duyệt bởi chính doanh nghiệp, doanh nhân trước khi lên bài.\n"
     "Mọi thông tin minh bạch, có nguồn và lưu lịch sử sửa đổi."),
    ("chinh-sach-du-lieu", "Chính sách bảo vệ dữ liệu cá nhân", True, 2, DATA,
     "Thông tin trên hồ sơ được đối chiếu và duyệt bởi chính chủ thể trước khi công bố.\n"
     "Thông tin riêng tư được bảo vệ hoặc ẩn theo nguyện vọng cá nhân.\n"
     "Chủ thể có quyền xem, sửa, ẩn hoặc xóa hồ sơ bất kỳ lúc nào."),
    ("quy-che-bien-tap", "Quy chế biên tập & xác minh", False, 3, EDITORIAL,
     "Văn phong trung lập, có nguồn kiểm chứng.\n"
     "Biên soạn, tham khảo và duyệt bởi chính doanh nghiệp, doanh nhân.\n"
     "Mỗi lần sửa là một phiên bản trong lịch sử sửa đổi."),
    ("chinh-sach-cookie", "Chính sách cookie", False, 4, COOKIE, "Chỉ dùng cookie cần thiết.\nKhông có cookie quảng cáo."),
    ("quy-dinh-tai-tro", "Quy định về tài trợ", False, 5, DONATION_RULES,
     "Chỉ nhận qua tài khoản công bố trên trang Donate.\nTài trợ không ảnh hưởng việc duyệt hồ sơ."),
]

DONATION_LEAD = ("Mỗi doanh nhân là một câu chuyện về khát vọng, bản lĩnh và đóng góp cho nền kinh tế. "
                 "doanhnhan.wiki ra đời để những câu chuyện ấy được ghi chép đầy đủ, xác minh cẩn thận và lưu giữ lâu dài "
                 "— để hôm nay có nơi tra cứu, và thế hệ sau có nơi học hỏi.")
DONATION_BODY = """## Vì sao cần doanhnhan.wiki
Thông tin về doanh nhân hôm nay nằm rải rác trên báo chí, mạng xã hội và hồ sơ của các hiệp hội — khó tìm, khó kiểm chứng và dễ thất lạc theo thời gian. doanhnhan.wiki gom những thông tin ấy về một nơi: hồ sơ doanh nhân, doanh nghiệp, dấu mốc sự nghiệp, sự kiện và video phỏng vấn. Mỗi thông tin đều có nguồn trích dẫn và lịch sử chỉnh sửa minh bạch. Việc tra cứu luôn miễn phí cho tất cả mọi người.

## Chi phí để trang được duy trì
Để một kho dữ liệu đáng tin cậy tồn tại lâu dài, doanhnhan.wiki cần chi trả thường xuyên cho:

- **Máy chủ, tên miền và đường truyền** — để trang luôn hoạt động ổn định.
- **Bảo mật và sao lưu dữ liệu** — bảo vệ thông tin của các doanh nhân.
- **Biên tập và xác minh** — đối chiếu nguồn, kiểm duyệt từng hồ sơ trước khi công bố.
- **Phỏng vấn và ghi hình** — lưu lại câu chuyện bằng chính lời kể của doanh nhân.
- **Phát triển tính năng** — giúp cộng đồng tra cứu và kết nối dễ dàng hơn.

## Mọi khoản tài trợ đều quý giá
Không có mức tối thiểu. Dù nhiều hay ít, khoản tài trợ của anh chị là sự tiếp sức để doanhnhan.wiki tiếp tục ghi lại hành trình của mọi doanh nhân Việt Nam. Toàn bộ kinh phí nhận được được dùng cho hoạt động của trang.

**Trân trọng cảm ơn anh chị đã đồng hành!**

*Ban vận hành doanhnhan.wiki*
"""

ABOUT = """doanhnhan.wiki là **trang cộng đồng** lưu giữ hồ sơ doanh nhân Việt Nam: doanh nghiệp, ngành nghề, hiệp hội, sự kiện và video phỏng vấn.

- **Ai cũng xem được** — không cần tài khoản.
- **Muốn đưa thông tin lên** — tạo tài khoản và chờ ban quản trị duyệt; mỗi nội dung vẫn được biên tập viên kiểm duyệt trước khi công bố.
- **Minh bạch** — mọi thông tin có nguồn trích dẫn và lịch sử sửa đổi.
- **Video** chỉ được nhúng từ nền tảng gốc, trang không lưu trữ tệp video.

Muốn kể câu chuyện của mình trước ống kính? Hãy liên hệ để được ghi hình, phỏng vấn.

<h2 id="tieu-chi">Tiêu chí đăng hồ sơ</h2>

Mọi hồ sơ trên doanhnhan.wiki được kiểm duyệt công khai theo 4 tiêu chí:

1. **Người thật, việc thật:** Có hoạt động kinh doanh xác minh được bằng ít nhất một trong: mã số thuế doanh nghiệp/hộ kinh doanh, website/fanpage chính thức, bài báo đã đăng, hoặc xác nhận của hiệp hội/YBA.
2. **Thông tin minh bạch, có kiểm chứng:** Thông tin có nguồn, số liệu và thành tích phải kiểm chứng được; không bịa đặt, không phóng đại.
3. **Chuẩn mực nội dung:** Không có nội dung vi phạm pháp luật, không công kích cá nhân, không quảng cáo trá hình.
4. **Đồng thuận và quyền dữ liệu:** Chủ hồ sơ đồng ý công khai thông tin trên trang; muốn sửa hoặc gỡ thì gửi yêu cầu qua mục "Yêu cầu về dữ liệu".

*Cam kết xử lý:* Ban biên tập phản hồi hồ sơ trong vòng **3 ngày làm việc**. Nếu cần bổ sung, bạn sẽ nhận email nêu rõ nội dung cần bổ sung.
"""


class Command(BaseCommand):
    help = "Tạo dữ liệu nền: tỉnh/thành, ngành nghề, chính sách, trang tài trợ, cài đặt chung."

    @transaction.atomic
    def handle(self, *args, **options):
        for i, (code, name, is_city, merged) in enumerate(PROVINCES):
            Province.objects.update_or_create(code=code, defaults={"name": name, "is_city": is_city,
                                                                    "merged_from": merged, "sort_order": i})
        self.stdout.write(f"Tỉnh/thành: {Province.objects.count()}")

        for i, (name, icon, desc, vsic, children) in enumerate(SECTORS):
            root = Sector.objects.filter(name=name, parent__isnull=True).first() or Sector(name=name)
            root.icon, root.description, root.sort_order = icon, desc, i
            root.vsic_code = root.vsic_code or vsic
            root.save()
            for j, (child, child_vsic) in enumerate(children):
                obj = Sector.objects.filter(name=child, parent=root).first() or Sector(name=child, parent=root)
                obj.icon, obj.sort_order = icon, j
                obj.vsic_code = obj.vsic_code or child_vsic
                obj.save()
        self.stdout.write(f"Ngành nghề: {Sector.objects.count()}")

        for code, title, required, order, body, summary in POLICIES:
            doc, _ = PolicyDocument.objects.update_or_create(code=code, defaults={
                "title": title, "requires_acceptance": required, "sort_order": order})
            if not doc.versions.exists():
                PolicyVersion.objects.create(document=doc, version="1.0", body_md=body, summary_points=summary,
                                             summary_of_changes="Phiên bản đầu tiên.",
                                             status=PolicyVersion.State.PUBLISHED)
        self.stdout.write(f"Văn bản chính sách: {PolicyDocument.objects.count()}")

        donation = DonationSettings.load()
        if not donation.body_md:
            donation.lead, donation.body_md = DONATION_LEAD, DONATION_BODY
            donation.save()
        site = SiteSettings.load()
        if not site.operator_name or site.operator_name == "[Tên công ty vận hành]":
            site.operator_name = "Digits Technology"
        if not site.about_md:
            site.about_md = ABOUT
            site.save()
        self.stdout.write(self.style.SUCCESS("Đã tạo dữ liệu nền."))
