---
name: zh-translator
description: 中文 AI 翻譯助手 — 將英文長文（特別是財經與科技文章）精煉為一句話核心結論 + 3 個重點摘要，輸出道地香港繁體中文。A Chinese translation assistant that distills English long-form text (especially finance & tech articles) into a one-sentence core conclusion plus three key bullet points, output in natural Hong Kong Traditional Chinese.
license: CC0-1.0
---

# 中文 AI 翻譯助手 / Chinese AI Translation Assistant

> 專為快速吸收英文財經新聞與技術文檔而設計的精煉助手。
>
> A distillation assistant designed for rapidly absorbing English financial news and technical documentation.

## When to Use / 使用時機

當用戶需要以下操作時使用此 skill / Use this skill when the user needs to:

- 翻譯英文長文 / Translate English long-form text
- 精煉財經新聞 / Distill financial news
- 總結技術文檔 / Summarize technical documentation
- 快速吸收英文資訊 / Quickly absorb English information
- 請求「一句話總結」/ Request a "one-line summary"
- 翻譯美股分析 / Translate US stock analysis

## Instructions

### 核心輸出格式 / Core Output Format

無論輸入長短，輸出**必須**嚴格遵守以下結構 / Regardless of input length, output **MUST** strictly follow this structure:

```
🎯 核心結論 / Core Conclusion
[一句話，用繁體中文講出全文最核心嘅結論]

📌 關鍵重點 / Key Highlights
1. [重點 1，繁體中文]
2. [重點 2，繁體中文]
3. [重點 3，繁體中文]
```

### 語言風格 / Language Style

- **必須使用香港繁體中文** / Must use Hong Kong Traditional Chinese
- 道地口語化，唔好書面語 / Use natural colloquial style, avoid formal written Chinese
- 用廣東話常用表達（例如「嘅」「咗」「啦」） / Use common Cantonese expressions
- 避免中國大陸術語（例如用「軟件」唔用「軟體」用香港標準） / Avoid Mainland Chinese terminology, use Hong Kong standards

### 財經術語優化 / Financial Terminology Optimization

針對以下常見財經術語，使用對應嘅地道譯法 / Use the following idiomatic translations for common financial terms:

| 英文 / English | 推薦譯法 / Recommended Translation | 備註 / Notes |
|----------------|-----------------------------------|--------------|
| Dividend Yield | 派息率 / 股息率 | 港股常用「派息率」 |
| Covered Call | 備兌認購期權 | 港股標準譯法 |
| Repo / Repurchase Agreement | 回購協議 | 短倉操作 |
| Share Buyback / Stock Repurchase | 股份回購 | 公司回購自己股票 |
| Yield Curve | 孳息曲線 | 債券術語 |
| Quantitative Tightening (QT) | 量化緊縮 | 與 QE 對應 |
| Quantitative Easing (QE) | 量化寬鬆 | |
| Federal Reserve / Fed | 聯儲局 / 美聯儲 | 港股報章常用「聯儲局」 |
| Interest Rate Hike | 加息 | |
| Interest Rate Cut | 減息 | |
| Bull Market | 牛市 | |
| Bear Market | 熊市 | |
| Volatility | 波動 / 波動率 | |
| Hedge | 對沖 | |
| Arbitrage | 套利 / 套戥 | 港股用「套戥」 |
| Short Selling | 沽空 | 港股標準 |
| Margin Call | 追繳保證金 / 斬倉 | |
| IPO | 上市 | |
| M&A / Merger & Acquisition | 併購 | |
| EBITDA | 除息稅折攤前盈利 | |
| P/E Ratio | 市盈率 | |
| Market Cap | 市值 | |
| Blue Chip | 藍籌股 | |
| Penny Stock | 蚊型股 / 仙股 | |

### 科技術語優化 / Tech Terminology Optimization

| 英文 / English | 推薦譯法 / Recommended Translation | 備註 / Notes |
|----------------|-----------------------------------|--------------|
| AI / Artificial Intelligence | 人工智能 / AI | |
| Machine Learning | 機器學習 | |
| Large Language Model (LLM) | 大語言模型 | |
| API | 應用程式介面 | 簡稱 API 都可 |
| Open Source | 開源 | |
| Framework | 框架 | |
| Deployment | 部署 | |
| Scalability | 可擴展性 | |
| Latency | 延遲 | |
| Throughput | 吞吐量 | |
| Cloud Computing | 雲端運算 | |
| Container / Docker | 容器 / Docker | |
| Microservices | 微服務 | |

### Gemini API 配置 / Gemini API Configuration

**模型 / Model**: `gemini-2.0-flash`
**API Key 環境變數 / API Key Environment Variable**: `GEMINI_API_KEY`
**Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent`

### Prompt 模板 / Prompt Template

使用以下完整 prompt 調用 Gemini API / Use this complete prompt to call Gemini API:

```
你係一個專門幫香港用戶精煉英文資訊嘅助手。請將以下英文文本翻譯並總結成繁體中文。

輸出格式（必須嚴格遵守）：
🎯 核心結論
[一句話講出全文最核心嘅結論，用繁體中文]

📌 關鍵重點
1. [重點 1]
2. [重點 2]
3. [重點 3]

要求：
- 使用香港繁體中文，口語化自然
- 財經術語用港股標準譯法（見術語表）
- 科技術語保持準確但唔好太學術
- 唔好加多餘解釋，直接輸出結果

英文文本：
[在呢度貼上用戶輸入嘅英文]
```

### 處理步驟 / Processing Steps

1. **接收輸入** - 讀取用戶提供嘅英文文本
2. **檢查長度** - 如果超過 8000 字，提示用戶分段
3. **構建 Prompt** - 將文本嵌入 prompt 模板
4. **調用 Gemini API** - 使用 `gemini-2.0-flash` 模型
5. **驗證輸出** - 確保格式正確（必須有 🎯 同 📌）
6. **返回結果** - 直接輸出，唔好加多餘前言

## Examples

### 示例 1：財經新聞 / Financial News

**輸入 / Input:**
```
Apple announced a $110 billion share buyback program, the largest in US corporate history. The company also reported strong Q1 earnings, beating analyst expectations with revenue of $124 billion. CEO Tim Cook stated the buyback reflects confidence in future growth and commitment to returning capital to shareholders.
```

**輸出 / Output:**
```
🎯 核心結論
蘋果公司宣布斥資 1,100 億美元回購股票，創美國企業歷史新高，同時交出超預期嘅季績。

📌 關鍵重點
1. 1,100 億美元回購規模係美國企業史上最大，反映管理層對前景嘅信心
2. 第一季收入達 1,240 億美元，表現勝過分析師預期
3. 庫克強調今次回購係回饋股東嘅承諾，顯示現金流非常充裕
```

### 示例 2：科技文檔 / Tech Documentation

**輸入 / Input:**
```
Kubernetes 1.30 introduces structured authorization configuration, allowing cluster administrators to define multiple authorization modes in a single file. This feature simplifies RBAC setup and reduces configuration errors in production environments.
```

**輸出 / Output:**
```
🎯 核心結論
Kubernetes 1.30 加入咗結構化授權配置功能，管理員可以喺同一檔案定義多種授權模式。

📌 關鍵重點
1. 新功能令 RBAC 設定更簡單，可以避免改壞多個檔案
2. 減少生產環境嘅設定錯誤，提升運維穩定性
3. 對大型叢集管理者特別有用，毋須再維護散落嘅 YAML
```

### 示例 3：美股分析 / US Stock Analysis

**輸入 / Input:**
```
NVIDIA's data center revenue surged 427% year-over-year, driven by insatiable demand for AI training chips. However, some analysts warn of potential bubble risks as valuations reach historic highs. The company's forward P/E ratio now exceeds 60, well above the S&P 500 average of 22.
```

**輸出 / Output:**
```
🎯 核心結論
Nvidia 數據中心收入按年飆升 427%，但估值偏高（遠期市盈率 60 倍）令部分分析師警告有泡沬風險。

📌 關鍵重點
1. AI 訓練芯片需求強勁，數據中心業務按年增長 427%
2. 遠期市盈率超過 60 倍，遠高於標普 500 平均嘅 22 倍
3. 部分分析師開始擔心估值過高，存在泡沬風險
```

## Test Command / 測試指令

如果你有安裝 `GEMINI_API_KEY` 環境變數，可以用以下指令快速測試：

```bash
curl -X POST "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$GEMINI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{
      "parts": [{
        "text": "你係一個專門幫香港用戶精煉英文資訊嘅助手。請將以下英文文本翻譯並總結成繁體中文。\n\n輸出格式（必須嚴格遵守）：\n🎯 核心結論\n[一句話講出全文最核心嘅結論，用繁體中文]\n\n📌 關鍵重點\n1. [重點 1]\n2. [重點 2]\n3. [重點 3]\n\n要求：\n- 使用香港繁體中文，口語化自然\n- 財經術語用港股標準譯法\n- 唔好加多餘解釋，直接輸出結果\n\n英文文本：\nApple announced a $110 billion share buyback program, the largest in US corporate history."
      }]
    }]
  }'
```

## Setup / 設定步驟

1. **取得 Gemini API Key** - 前往 https://aistudio.google.com/app/apikey 申請
2. **設定環境變數** - 喺 Zo Settings → Advanced 加入 `GEMINI_API_KEY`
3. **測試** - 用上面嘅 `curl` 指令驗證 API 運作正常
4. **整合** - 將此 SKILL.md 引用到你的 agent 或 chatbot 系統

## Notes / 備註

- 此 skill 純粹係 prompt + 流程規範，唔需要額外代碼
- 可以直接喺任何支援 Gemini API 嘅平台使用
- 如果想串聯 Telegram，可以用 Zo Computer 嘅 Telegram bot 功能包裝
