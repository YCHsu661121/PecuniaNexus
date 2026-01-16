# AI 功能設置指南

## 🤖 AI 投資助手

本系統整合了 **OpenAI GPT** 和 **Google Gemini** 兩種 AI 模型，可以回答股票相關問題。

## 🔑 API 金鑰設置

### 方法一：使用環境變數（推薦）

1. **複製示例文件**
   ```bash
   cp .env.example .env
   ```

2. **編輯 .env 文件**，填入你的 API 金鑰：
   ```
   OPENAI_API_KEY=sk-your-openai-api-key-here
   GEMINI_API_KEY=your-gemini-api-key-here
   ```

3. **重新啟動容器**：
   ```bash
   docker-compose restart pecunianexus
   ```

### 方法二：直接設置環境變數

```bash
export OPENAI_API_KEY="your-key-here"
export GEMINI_API_KEY="your-key-here"
docker-compose restart pecunianexus
```

## 🎯 獲取 API 金鑰

### OpenAI API Key
1. 前往 https://platform.openai.com/api-keys
2. 登入或註冊帳號
3. 點擊 "Create new secret key"
4. 複製金鑰（只會顯示一次！）

### Google Gemini API Key
1. 前往 https://makersuite.google.com/app/apikey
2. 登入 Google 帳號
3. 點擊 "Get API key"
4. 複製金鑰

## ✨ 功能特色

### AI 助手可以做什麼？
- 📊 分析技術指標（RSI、MACD、KD、布林通道）
- 📈 解讀 K 線圖形態
- 💡 提供投資建議（附風險提醒）
- 📚 解釋財經術語
- 🔍 分析市場趨勢

### 使用方式
1. 登入系統後，在右側找到 "🤖 AI 投資助手"
2. 選擇要使用的 AI 模型（OpenAI 或 Gemini）
3. 輸入問題並發送
4. 如果正在查看某支股票，AI 會自動參考該股票的數據來回答

### 示例問題
- "這支股票的 RSI 指標顯示什麼訊號？"
- "根據目前的技術指標，你認為這支股票適合買入嗎？"
- "什麼是 MACD？如何解讀？"
- "KD 指標的黃金交叉是什麼意思？"

## ⚠️ 注意事項

1. **費用**：使用 OpenAI 和 Gemini API 可能會產生費用
2. **隱私**：不要在 AI 對話中透露個人敏感資訊
3. **投資風險**：AI 的建議僅供參考，不構成投資建議
4. **API 限制**：請注意各平台的請求速率限制

## 🛠️ 故障排除

### AI 功能無法使用？

1. **檢查 API 金鑰是否設置**：
   ```bash
   docker exec pecunianexus printenv | grep API_KEY
   ```

2. **查看容器日誌**：
   ```bash
   docker logs pecunianexus --tail=50
   ```

3. **確認金鑰有效性**：
   - 登入對應平台檢查金鑰是否有效
   - 確認帳戶是否有足夠的配額

4. **重新構建容器**：
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

## 📝 更新日誌

- **v3.1** - 新增 AI 投資助手功能
  - 整合 OpenAI GPT-3.5-turbo
  - 整合 Google Gemini Pro
  - 自動帶入股票上下文
  - 支援多輪對話

---

**需要幫助？** 請在 GitHub 上提出 Issue！
