# AI 剪片工具包（Windows／Mac）

用 Claude 幫你剪口播影片：剪掉停頓和講錯的地方、上繁體中文字幕，也可以加特效、音效和背景音樂。
**不用安裝任何東西、不用開終端機**，下載、解壓縮、跟 Claude 說「幫我剪」就好。

## 下載（工具包選一個 + 模型）

| 檔案 | 大小 | 下載 |
|---|---|---|
| 工具包（Windows） | 約 1GB | [AI-Cut-Kit-Windows.zip](https://github.com/jackie81030/ai-video-editor-zip/releases/latest/download/AI-Cut-Kit-Windows.zip) |
| 工具包（Mac，M1 以後） | 約 0.5GB | [AI-Cut-Kit-Mac.zip](https://github.com/jackie81030/ai-video-editor-zip/releases/latest/download/AI-Cut-Kit-Mac.zip) |
| 轉文字用的模型（兩種電腦共用） | 約 1.4GB | [AI-Cut-Model-medium.zip](https://github.com/jackie81030/ai-video-editor-zip/releases/latest/download/AI-Cut-Model-medium.zip) |

檔案都放在「下載」資料夾就好。模型那個**不用解壓縮**，Claude 第一次用的時候會自己裝好。

## 開始用

1. 先裝好 [Claude 桌面版 App](https://claude.com/download) 並登入（要 Pro 或 Max 訂閱）。
2. 解壓縮工具包：Windows 在 zip 上按右鍵 →「全部解壓縮」；Mac 雙擊 zip（用 Safari 下載的會自動解開）。
3. 打開 Claude App，切到 Code（`</>`），選解壓縮出來的 `AI剪片工具包` 資料夾，按「信任」。
4. 把影片丟進 `我的影片` 資料夾，跟 Claude 說：「幫我剪這支影片」。

## 常見問題

- **第一次登入 Claude 後，Code 分頁一片空白**：把 Claude 關掉再打開。
- **用 Google 登入時瀏覽器問「要開啟 Claude 嗎？」**：按「開啟」（預設選的是取消）。
- **轉文字很久、畫面沒動**：正常，不是當機。一分鐘的影片大約要等幾分鐘。
- **Mac 跳出「Apple 無法驗證」**：按「完成」，跟 Claude 說一聲，它會自己解除。
- **防毒軟體擋住工具（Windows）**：在防毒軟體裡把 `AI剪片工具包` 資料夾設為信任，不要關掉防毒。
- **更新**：不用自己做。每次開始剪片時，Claude 會自動檢查並更新說明書和小程式。

## 關於使用紀錄

工具包會把**匿名的使用和錯誤紀錄**回傳給課程團隊，用來改進工具。送出前會自動洗掉電腦帳號名稱，不會傳你的影片、密碼或個資。跟 Claude 說「不要回傳紀錄」就會停。

## 內含的第三方軟體

Python（PSF License，Mac 版用 python-build-standalone）、FFmpeg（Windows 用 gyan.dev、Mac 用 martin-riedl.de 編譯版，GPLv3）、Node.js（MIT）、HyperFrames、Chrome Headless Shell、faster-whisper 與 Whisper medium 模型（MIT）、思源宋體（SIL Open Font License）。各自的授權檔在工具包的 `tools\` 資料夾裡。
