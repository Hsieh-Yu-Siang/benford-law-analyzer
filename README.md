# Benford Law Analyzer

這個專案是一個簡單的 Flask 網站，讓你上傳 CSV 檔，從股票收盤價資料中抽出首位數字，統計 1～9 的出現次數與比例，並產生柱狀圖與班佛定律理論值做比較。

## 功能
- 上傳 CSV 檔
- 自動辨識收盤價欄位
- 抽出首位數字
- 統計 1～9 出現次數
- 計算實際比例
- 產生柱狀圖
- 對照班佛定律理論值

## 本機執行

1. 建立虛擬環境（可選）
   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   # venv\Scripts\activate    # Windows
   ```

2. 安裝依賴
   ```bash
   pip install -r requirements.txt
   ```

3. 啟動網站
   ```bash
   python app.py
   ```

4. 打開瀏覽器
   ```text
   http://localhost:5000
   ```

## 部署方式

### PythonAnywhere
- 建立帳號並建立 Flask Web App
- 上傳 `app.py` 和 `templates/index.html`
- 安裝 requirements
- 重新載入網站

### Render / Heroku
- 連接 GitHub repo
- 以 Python Web Service 部署
- 設定啟動指令為：`gunicorn app:app`

## 需求
- Python 3.10+
- Flask
- pandas
- matplotlib
