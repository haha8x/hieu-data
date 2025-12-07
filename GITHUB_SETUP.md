# 📤 Hướng dẫn push lên GitHub

## Bước 1: Tạo repository trên GitHub

1. Truy cập: https://github.com/new
2. Repository name: `hieu`
3. Description (optional): "LIHEAP Data Processing with Reproducibility"
4. Chọn **Public** hoặc **Private**
5. **KHÔNG** chọn "Initialize this repository with a README" (vì đã có rồi)
6. Click **Create repository**

## Bước 2: Push code lên GitHub

Sau khi tạo xong repository, chạy lệnh sau:

```bash
cd /Users/haha8x/Project/hieu
git remote add origin https://github.com/haha8x/hieu.git
git branch -M main
git push -u origin main
```

Hoặc nếu muốn dùng SSH:

```bash
cd /Users/haha8x/Project/hieu
git remote add origin git@github.com:haha8x/hieu.git
git branch -M main
git push -u origin main
```

## Bước 3: Verify

Truy cập: https://github.com/haha8x/hieu

Bạn sẽ thấy:
- ✅ README.md với documentation đầy đủ
- ✅ SOLUTION.md với technical details
- ✅ requirements.txt với fixed versions
- ✅ notebooks/ với code
- ✅ .gitignore đã exclude data files

## 🔐 Authentication

Nếu gặp lỗi authentication:

### Option 1: Personal Access Token (HTTPS)
1. Tạo token tại: https://github.com/settings/tokens
2. Chọn scopes: `repo`, `workflow`
3. Khi push, dùng token thay vì password

### Option 2: SSH Key
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: https://github.com/settings/keys
```

## 📝 Status hiện tại

```
✅ Git initialized
✅ Files committed locally
✅ .gitignore configured
✅ README.md created
⏳ Waiting for GitHub repository creation
```

Repository URL: https://github.com/haha8x/hieu
