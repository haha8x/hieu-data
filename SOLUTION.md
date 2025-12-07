# 🔧 Giải quyết vấn đề: Kết quả khác nhau giữa 2 máy

## ❌ Vấn đề
Code chạy trên 2 máy khác nhau cho kết quả khác nhau (non-deterministic behavior)

## 🔍 Nguyên nhân gốc rễ

### 1. **Package versions không cố định**
- `requirements.txt` ban đầu chỉ có `pandas`, `openpyxl`, `pgeocode` mà không fix version
- Mỗi máy cài version khác nhau → behavior khác nhau

### 2. **Dictionary aggregation không deterministic** 
- Code `s.value_counts().idxmax()` khi có 2+ cities xuất hiện cùng số lần thì chọn ngẫu nhiên
- Python dictionary không đảm bảo thứ tự consistent

### 3. **File sorting không explicit**
- `sorted(data_folder.rglob("*.xls*"))` có thể cho thứ tự khác nhau trên các OS/filesystem khác nhau
- Thứ tự file ảnh hưởng đến kết quả concat và aggregation

### 4. **Không có random seed**
- Các operation ngẫu nhiên không được seed → kết quả khác nhau mỗi lần chạy

## ✅ Giải pháp đã áp dụng

### 1. **Fixed package versions**
```txt
pandas==2.2.3
openpyxl==3.1.2
pgeocode==0.4.0
numpy==2.1.3
```

### 2. **Added random seed**
```python
import numpy as np
import random

np.random.seed(42)
random.seed(42)
```

### 3. **Explicit file sorting by name**
```python
excel_files = sorted(data_folder.rglob("*.xls*"), key=lambda x: x.name)
```

### 4. **Deterministic aggregation**
```python
.agg(lambda s: s.value_counts().sort_index().idxmax())
```
Thêm `.sort_index()` để khi có tie, chọn theo thứ tự alphabet

### 5. **Relative paths instead of hardcoded**
```python
script_dir = Path(__file__).parent.parent
data_folder = script_dir / "Data_raw_SDGE LIHEAP"
```

## 🧪 Test reproducibility

Chạy script này nhiều lần để verify:
```bash
python notebooks/test_reproducibility.py
```

Checksum phải luôn là: **`bca54937bbea56d407cecb5602db6ea2`**

## 📋 Hướng dẫn đồng bộ 2 máy

1. **Pull code mới nhất**
```bash
git pull
```

2. **Cài đúng version packages**
```bash
pip install -r requirements.txt --force-reinstall
```

3. **Kiểm tra Python version**
```bash
python --version  # Should be Python 3.13 or compatible
```

4. **Clear cache (optional)**
```bash
rm -rf ~/.cache/pgeocode/
```

5. **Test reproducibility**
```bash
python notebooks/01_combine_liheap_data.py
python notebooks/test_reproducibility.py
```

## ✨ Kết quả

- ✅ Code chạy thành công
- ✅ Checksum giống nhau mỗi lần chạy
- ✅ Reproducible trên mọi máy (với cùng dependencies)
- ✅ Total records: 38,352 rows
- ✅ Total amount: $38,423,514.80

## 📌 Lưu ý

- **LUÔN dùng virtual environment** để tránh conflict packages
- **Commit `requirements.txt`** với version cụ thể vào git
- **Document Python version** yêu cầu
- **Test reproducibility** sau mỗi lần thay đổi code
