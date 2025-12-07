# LIHEAP Data Processing Project

Dự án xử lý và phân tích dữ liệu LIHEAP (Low Income Home Energy Assistance Program) cho SDGE.

## 📋 Mô tả

Project này xử lý dữ liệu LIHEAP từ nhiều file Excel, chuẩn hóa, làm sạch, và tổng hợp thành một dataset duy nhất để phân tích.

### ✨ Tính năng chính

- ✅ Tự động phát hiện header row trong Excel files
- ✅ Chuẩn hóa tên cột từ nhiều format khác nhau
- ✅ Làm sạch ZIP code, dates, và pledge amounts
- ✅ Tự động điền City từ ZIP code (sử dụng pgeocode)
- ✅ Filter theo time range (2023-01 đến 2025-06)
- ✅ **Reproducible** - kết quả giống nhau trên mọi máy

## 🔧 Cài đặt

### Requirements

- Python 3.13+
- Virtual environment (khuyến nghị)

### Setup

1. Clone repository:
```bash
git clone https://github.com/haha8x/hieu.git
cd hieu
```

2. Tạo virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# hoặc
.venv\Scripts\activate  # Windows
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

## 🚀 Sử dụng

### Chạy data processing

```bash
python notebooks/01_combine_liheap_data.py
```

### Test reproducibility

```bash
python notebooks/test_reproducibility.py
```

Checksum phải luôn là: `bca54937bbea56d407cecb5602db6ea2`

## 📊 Kết quả

- **Total records**: 38,352 rows
- **Time range**: 2023-01 đến 2025-06
- **Total pledge amount**: $38,423,514.80
- **Unique cities**: 71
- **Unique ZIP codes**: 153

## 📂 Cấu trúc thư mục

```
hieu/
├── notebooks/
│   ├── 01_combine_liheap_data.py    # Main processing script
│   └── test_reproducibility.py       # Reproducibility test
├── Data_raw_SDGE LIHEAP/             # Raw Excel files (gitignored)
├── data_clean/                        # Output files (gitignored)
├── requirements.txt                   # Python dependencies
├── SOLUTION.md                        # Technical documentation
└── README.md                          # This file
```

## 🔍 Giải quyết vấn đề reproducibility

Xem chi tiết trong [SOLUTION.md](SOLUTION.md) về cách fix vấn đề kết quả khác nhau giữa các máy.

### Các fix chính:
- ✅ Lock package versions
- ✅ Set random seed
- ✅ Deterministic file sorting
- ✅ Deterministic aggregation
- ✅ Relative paths

## 📝 Dependencies

- `pandas==2.2.3` - Data processing
- `openpyxl==3.1.2` - Excel file handling
- `pgeocode==0.4.0` - ZIP code to city lookup
- `numpy==2.1.3` - Numerical operations

## 🤝 Contributing

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

## 📄 License

MIT License

## 👤 Author

haha8x

---

**Note**: Raw data files không được commit lên git (đã thêm vào `.gitignore`). Để chạy script, bạn cần có data files trong folder `Data_raw_SDGE LIHEAP/`.
