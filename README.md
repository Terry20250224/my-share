# Terry's Hub — my-share

個人分享空間 · GitHub Pages + Android APK 雙線開發

## 🌐 Web 入口
- **links.html** — 9 鍵導航面板：https://terry20250224.github.io/my-share/links.html
- **index.html** — 首頁
- **news.html** — 新聞面板
- **search-portal** — https://zo.pub/terrywsc123/search-portal/search.html

## 📱 Android 專案：TerryHub
9 鍵導航面板嘅 Android 殼 App。
- 套件名：`com.terry.hub`
- minSdk 26（Android 8.1.1）· targetSdk 34
- 載入 [links.html](https://terry20250224.github.io/my-share/links.html) 作主畫面

### Build
GitHub Actions 自動建構 debug APK，見 `.github/workflows/build-apk.yml`。
下載位置：`app/build/outputs/apk/debug/app-debug.apk`（建構成功後可喺 Actions Artifacts 下載）。

## 📝 更新日誌
- 2026-06-29 · 補齊 Android 項目地基檔 + 啟動 APK 自動建構工作流