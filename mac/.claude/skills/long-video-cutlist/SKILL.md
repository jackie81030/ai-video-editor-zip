---
name: student-cutlist
description: "學員版長錄影選段（student cut-list）。When a student's long recording from their own service business (consultation, the service itself, result reveal, aftercare, a solo explanation, a class, staff training) or its transcript comes in and the reel-worthy segments need to be picked out for the student's editor, delivered as a PDF. The student records instead of creating; this skill watches the long file so they don't have to. Uses the same core method as 頭家's own reel-cutlist. Triggers on: '學員選段', '幫 {學員} 選段', '長錄影選段', '錄影選段', '服務過程錄影', '側錄', '上課錄影', '諮詢影片選段', '客戶諮詢錄影', a long video file path from a student, 'student cutlist', 'record cutlist', or 'consult cutlist'. Transcribes locally if given a file. Self-contained: no other skill required. Talk to the student in 繁體中文 from the very first line, including the first status update."
---

## ★ zip 版必讀（優先於下面全文）

這份技能原本寫給「自己裝工具」的版本。現在這個資料夾是 **zip 版**：轉逐字稿、印 PDF 的工具都已經內建，**什麼都不用安裝**。下面全文照做，但遇到以下情況一律照這張對照表改：

| 下面寫的 | zip 版改成 |
|---|---|
| `<opened_folder>` | 這個資料夾（有 `CLAUDE.md`、`tools/`、`我的影片/` 的那層） |
| `<skill_dir>` | `<opened_folder>/.claude/skills/long-video-cutlist` |
| 寫到 `<opened_folder>/transcript` 的檔案（SRT、HTML、PDF） | 寫到 `我的影片/工作檔/<影片名>/`；**PDF 印好後另外複製一份到 `我的影片/`**，再用 `bash tools/run.sh python ./tools/freecut/helpers/open_file.py "<PDF>" --reveal` 幫學員選起來 |
| Step 0 整段的安裝和轉錄指令（`.consult-whisper`、`transcribe_mac.sh`、`transcribe_cpu.py`、`install_ffmpeg.sh`、mlx、winget） | 全部跳過。轉逐字稿只用：`bash tools/run.sh python ./tools/transcribe.py "<影片>"`，SRT 會在 `我的影片/工作檔/<影片名>/<影片名>.srt` |
| 「做 PDF」第 3 步找 Chrome／Edge | 不用找。`bash tools/run.sh python ./tools/print_pdf.py "<HTML 路徑>"`（用內建的 Chrome） |
| 學員給連結（FB、IG、YouTube），用 yt-dlp 下載 | zip 版沒有下載工具。用白話請學員把影片檔丟進 `我的影片/` |

**其他 zip 版差異：**
- 轉逐字稿用內建的 medium 模型，比原本的 large-v3-turbo 慢。轉的時候程式會印進度百分比，照進度跟學員說轉到哪，**不要報要幾分鐘**（猜不準）。
- 轉好的逐字稿已經是繁體（只換字不換詞），還是要照下面的規則人工校對。
- 學員資料存在這個資料夾的 `我的資料.md`（跟 `我的剪輯偏好.md` 放一起）。
- **選段交件後**，問學員一句：「要我直接把其中一支剪出來嗎？跟我說第幾支就好。」學員說要，就照 `CLAUDE.md` 的剪片流程剪，只剪那一支的時間範圍（`.claude/skills/ai-edit/SKILL.md` 有從選段清單剪片的做法）。

---


# 學員選段（Student Cut-List）

**語言：從第一句話就用繁體中文。** 學員看到的每一行都是繁中，包括你開工前的第一句進度（例如「我來看這支錄影，幫你挑可以剪的片段。」），不要先講一句英文再切換。工具名和檔名照原樣。

Reads a long recording or transcript from a student's service business, finds the 30-90 秒 segments (longer when the reasoning needs it) that would make good IG reels, and writes a PDF cut-list the student's editor can follow. The idea behind it: students **record instead of create**. They leave the camera running during real work, and this skill does the watching.

**This skill selects. It does not cut.** Selection only, output is a PDF.

**選段方法和頭家自己用的 `reel-cutlist` 是同一套。** 方法寫在 `reference/core-method.md`，兩個 skill 一字不差。這個 SKILL.md 只是學員版的情境層：素材是學員自己的服務錄影，理想客戶和敏感資訊從學員檔案來，輸出是 PDF。學員要客製的是情境（自己的理想客戶、不能公開的東西），不是方法。

**版本：**

- **v1（2026-09-22）**：consult-cutlist 改名 record-cutlist，從客戶諮詢擴大到整條客戶旅程的長錄影。
- **v2（2026-09-24）**：改名 student-cutlist（和 reel-cutlist 太像，分不出來）。選段手藝改成讀 `reference/core-method.md`，和 reel-cutlist 共用：每支先寫「這支在講什麼」、開頭字卡＝主題句、開頭給候選和備案、訪談問答開頭例外、先定收尾再往回拉、定格點、保留停頓、批評別人的話標出來提醒、講者不確定標「？」。來源是 2026-09-23 學員D上海素材 教練 的退件意見。
- **v3（2026-10-17）**：核心方法 v2（1015 一對多 Q&A 選段四版的退件意見）：先畫全場地圖再選段、開頭從當事人的問題或專家的重整句找、陌生人測試、開頭的問題要回答到、推理不砍（超過 90 秒標偏長，不設硬上限）、穿插別處的句子要讓陌生人跟得上。執行面加兩條：簡轉繁不用 `s2twp`、帶名字的逐字稿講者標籤只當參考。

**不要在這個資料夾改 `reference/core-method.md`。** 母本在 `reel-cutlist/reference/core-method.md`，改完跑 `templates/學員選段-學員包/build.sh`，它會複製過來、檢查一致、重出學員包。學員機器上沒有母本，照這份就好。

---

## What comes in: the customer journey

A service business recording can be any stage of the customer journey, or none. Work out which kind it is at 核心第 1 步, because each kind hides its clips in a different place:

| Recording | Where the clips usually are |
|---|---|
| 諮詢／初診 | Customer names their situation → student diagnoses or corrects. The classic Q&A exchange. |
| 服務過程（邊做邊講） | Student explains what they're doing and why, or points out something the customer never noticed (「你這邊其實已經…」). |
| 服務中糾正 | Customer mentions a habit (「我都自己在家…」) → student stops them and explains why it's wrong. Often the strongest clips. |
| 成果揭曉／客人反應 | The reaction line plus the student's *why* it turned out this way. A reaction alone is not a clip. |
| 衛教／售後叮嚀 | Aftercare instructions, the "回家不要做這件事" moments. Very direct behavior-change clips. |
| 一個人對鏡頭講解／示範 | No customer. Student names a common mistake and shows the fix. |
| 上課／工作坊 | Student teaches a group. Pick the moments a participant asks or gets corrected. The participant's own question (often said when they first speak, minutes before the answer) is usually the opening. |
| 員工教育訓練 | Student explains a standard to staff. Good for "why we do it this way" clips. Sensitivity list is stricter here (internal numbers, staff names, pricing). |

A single file often covers several stages (consultation, then service, then reveal). Map each stage separately.

---

## Input

Three accepted forms, in order of preference:

1. **Video or audio file** (mp4, mov, m4a, mp3). Phone recordings, Zoom cloud recordings and Loom all work. This is the default path: the student never transcribes anything.
2. **SRT or timestamped transcript.** Skip transcription.
3. **Plain transcript, no timestamps** (from a dictation app). Works, but cuts get located by first/last sentence instead of timecodes. Say so in the PDF caveats.

**A link instead of a file (FB／IG live replay, YouTube): download the audio yourself with yt-dlp.** Selection only needs the sound; the student's editor cuts from their own original file later. yt-dlp lives in the same `~/.consult-whisper` venv as Whisper (Step 0 installs it; if only yt-dlp is missing, install just that: Mac `~/.consult-whisper/bin/pip install yt-dlp`, Windows `& "$env:USERPROFILE\.consult-whisper\Scripts\python.exe" -m pip install yt-dlp`). Tell the student in 繁中 first that you only download the sound, about 100MB for a 3-hour live, not the video. Then, with ffmpeg on PATH (Mac: `export PATH="$HOME/.local/bin:$PATH"`):

```bash
# Mac
~/.consult-whisper/bin/yt-dlp -f "bestaudio/best" -x --audio-format m4a -o "<opened_folder>/transcript/<短名>.%(ext)s" "<連結>"
# Windows PowerShell
& "$env:USERPROFILE\.consult-whisper\Scripts\yt-dlp.exe" -f "bestaudio/best" -x --audio-format m4a -o "<opened_folder>\transcript\<短名>.%(ext)s" "<連結>"
```

Name the file by what and when (例:`直播-0923`), then treat that audio as form 1. Write the link into the PDF's 來源 line.
- **Only the student's own content** (their page, their live, their account). A link to someone else's video: don't download it, explain in 繁中 that the skill only works on their own recordings.
- **It fails** (private video, login required, group-only, `Unsupported URL`, or a sudden extractor error): run `pip install -U yt-dlp` once and retry, because platforms change and old versions break. Still failing → ask for the file in 繁中 (their own phone or computer copy, or download it from the platform). Never try cookies, exporting a browser login, or other download sites and tools.
- Verified 2026-10-09 on Mac with a public FB live replay (pip install, no password, 60s of audio in 2s). Windows not yet tested on a student machine.

**The student doesn't have to name the file.** Students upload the video in the chat (ChatGPT: 「+」→「檔案和資料夾」; the app then tells you the file's full path) or put it in the opened folder, and say 「幫我挑片段」. An uploaded video can stay where it is (Downloads, Desktop); read it from that path and never copy or move it. Everything you write (`transcript/`, the SRT, the HTML and PDF) goes in `<opened_folder>/transcript`, the folder the app opened, never next to the video. If no file is named, look in the opened folder (top level, not `.agents` / `.claude` / `transcript`) for video and audio files that don't have a finished PDF yet. One → use it and say which one in 繁中. Several → list them with their length and ask which one (or 全部). None → tell the student in 繁中 to put the video into this folder. Never ask the student to type a file name.

## Step 0: Transcribe (form 1 only)

**Tools missing? Set up first.** This only works when the skill runs locally in Codex, Claude Code, or Claude Desktop Code in Local mode. A normal cloud chat cannot install tools, so ask for an SRT or timestamped transcript instead (form 2).

- **Check before installing anything.** Identify the OS and CPU, then check `ffmpeg -version`. On Apple Silicon, check `test -x ~/.consult-whisper/bin/mlx_whisper && echo ok` (not `--help`, which fails inside a sandbox even when installed); on Intel Mac, check `~/.consult-whisper/bin/python -c "import faster_whisper"`; on Windows, check `%USERPROFILE%\.consult-whisper\Scripts\python.exe -c "import faster_whisper"`. Install only what is missing. Before starting, tell the student in plain 繁中 what will be installed, that the operating system may ask for approval, and that the first model download is large, so use Wi-Fi.
- **Python is absent:** stop before trying random commands. Explain in 繁中 that local transcription needs Python 3, guide the student to install it through the official Python installer, then resume this step. Never request a password in chat or disable a security feature.
- **Apple Silicon Mac** (`uname -m` = `arm64`): install in ONE command, so the student approves once: `python3 -m venv ~/.consult-whisper && ~/.consult-whisper/bin/pip install mlx-whisper yt-dlp` (yt-dlp is small and lets the student paste a live-replay link later, see Input). The download is large and the command may move to the background after about 30 seconds; wait for it to finish. Then confirm the install landed with `test -x ~/.consult-whisper/bin/mlx_whisper && echo ok` (a plain file check, no approval needed). If it is missing, pip was cut off: run the same `pip install mlx-whisper` again (it resumes from its cache), then check again. Do not start transcribing until the check says ok. Run `install_ffmpeg.sh` from this skill's `reference/` folder. It installs verified `ffmpeg` in `~/.local/bin`. Then transcribe only through `reference/transcribe_mac.sh` (below). Never a bare `mlx_whisper` command and never `python -m mlx_whisper` (the package has no `__main__`, it fails after the model download and costs the student another approval).
- **Intel Mac** (`uname -m` = `x86_64`): MLX does not run here. Create `~/.consult-whisper` with `python3 -m venv ~/.consult-whisper`, then run `~/.consult-whisper/bin/pip install faster-whisper "ctranslate2<4.6" "setuptools<81" yt-dlp`. Run `install_ffmpeg.sh`, then `export PATH="$HOME/.local/bin:$PATH"`. Use the CPU script below, never MLX or the bare `whisper` CLI.
- **Windows:** create a venv at `%USERPROFILE%\.consult-whisper`, then use that venv's `python.exe -m pip` to install `faster-whisper "ctranslate2<4.6" "setuptools<81" yt-dlp`. Install ffmpeg with `winget install --id Gyan.FFmpeg -e --source winget`. Reload PATH before checking again. Do not reinstall merely because the current terminal has not refreshed PATH.
- **Windows, if `import faster_whisper` still fails after installing:** Smart App Control is blocking an unsigned DLL. Never tell the student to turn security off. Walk them through the standalone Faster-Whisper-XXL instead: github.com/Purfview/whisper-standalone-win/releases → download the Windows build → unzip → run `faster-whisper-xxl.exe` with the same language / prompt / srt settings.
- **Windows or Intel Mac model:** use `medium`, not large, because large is too slow on CPU. Keep `condition_on_previous_text=False` (see the loop bug below) and write SRT output.
- **Never:** install Homebrew, ask for a password in the chat (passwords go only into the system's own pop-up), run `softwareupdate --install -a`, use `xattr -c`, or turn off any security setting.
- **Blocked by a sandbox?** Some apps (the ChatGPT desktop app, Codex) run commands in a sandbox. Two signs: MLX says `No Metal device available`, or Chrome finishes but the PDF is empty (0 bytes) or missing. That is the sandbox, not a broken install. Rerun the exact same command outside the sandbox (request escalated permission; if the app shows an allow prompt, tell the student in 繁中 to click allow). Never swap in a different tool to get around it: no torch, no openai-whisper, no LibreOffice or other PDF converters. If it is still blocked after that, follow the give-up and no-browser rules below.
- **A long transcription takes minutes, not seconds.** A 45-minute file takes about 5 to 10 minutes on Apple Silicon. On Mac, `transcribe_mac.sh` handles the waiting: after `start`, only run `status`. Tool messages like `Script completed` when you poll a background command do NOT mean transcription finished; only `status` saying `DONE` does. Never judge the run by a separate check inside the sandbox (a sandboxed `mlx_whisper --help` always says `No Metal device available`).
- **Give up cleanly.** If setup fails twice, or the time estimate for the file is over an hour, stop and ask for a transcript from Zoom, Loom, or any transcription app instead. Don't let the student try random fixes.

(These traps come from the ai-video-editor kit's installs on real student Mac and Windows machines.)

The venv is still named `.consult-whisper` on purpose: this skill used to be `consult-cutlist`, and students who installed then already have the tools there. Renaming it would force a second 1.5GB install.

**Apple Silicon Mac only.** Always go through `reference/transcribe_mac.sh`. Never call `mlx_whisper` directly, never write your own polling loop around it.

```bash
# 1. Start (run OUTSIDE the sandbox, MLX needs the GPU). Runs until the transcript is done.
zsh "<skill_dir>/reference/transcribe_mac.sh" start "<file>" "<opened_folder>/transcript"

# 2. Check progress (reads files only, works inside the sandbox, no approval needed).
zsh "<skill_dir>/reference/transcribe_mac.sh" status "<file>" "<opened_folder>/transcript"
```

- `start` prints `STARTED` and keeps running until the transcript is done (it ends with `DONE <path>`). If the app moves it to the background after a while, that is normal and it keeps going. If a transcription is already running or already finished, `start` says `RUNNING` or `DONE` and does not start a second one.
- After `STARTED`, only use `status`, about once a minute. `RUNNING 已轉到 12:30` means it is working (compare with the video length and tell the student in 繁中 roughly how far along it is). `DONE <path>` means the SRT is ready. `FAILED` prints the error. `STALE` means no progress for 10 minutes; only then run `start` again.
- The script uses the flags below (large-v3-turbo, zh, `--condition-on-previous-text False`, the 繁中 initial prompt, SRT output). Do not change them.

**CPU path, Windows and Intel Mac.** Use `reference/transcribe_cpu.py`, which writes the SRT itself. Do not write ad-hoc subtitle code. Pass the video or extracted audio file and the exact output path. Use `medium` and `--condition-on-previous-text False` through the script's defaults.

```bash
# Intel Mac
~/.consult-whisper/bin/python "<skill_dir>/reference/transcribe_cpu.py" \
  "<file>" --output "<opened_folder>/transcript/<file_stem>.srt"

# Windows PowerShell
& "$env:USERPROFILE\.consult-whisper\Scripts\python.exe" "<skill_dir>\reference\transcribe_cpu.py" "<file>" --output "<opened_folder>\transcript\<file_stem>.srt"
```
- **Why these flags:** on 2026-09-18 (學員E 教學課側錄) `whisper-medium-mlx` with default settings got stuck in a loop over long stretches with no talking, just background noise: one line repeated 315 times, and about 10 minutes of the recording disappeared. `--condition-on-previous-text False` breaks the loop, and large-v3-turbo transcribed the same file cleanly.
- **Hallucination check before 核心第 1 步, every time.** Count repeated lines in the SRT. If one line shows up dozens of times, or a random word (生抽, 字幕志愿者) repeats every ~30s, that stretch is noise with no talking, not speech. Treat it as a no-talking stretch: no clips come from it, and note it in the intro as usable B-roll. Service recordings have many of these (hair dryers, machines, quiet hands-on work), so expect them and don't treat them as a broken file.
- **Huge camera files** (4K teaching or event footage, several GB): extract audio first with `ffmpeg -i <file> -vn -ac 1 -ar 16000 <file>.m4a` and transcribe the m4a. On Mac, call ffmpeg after `export PATH="$HOME/.local/bin:$PATH"`. Keep the source video out of the repo, or delete it after delivery.

- A 60-minute recording takes a few minutes on Apple Silicon. Warn before running on anything over 90 minutes.
- Whisper leaks 簡體 sometimes. Convert to 繁體 in the cut-list, never paste raw text as captions. **If you convert with OpenCC, use `s2tw` (characters only), never `s2twp`.** `s2twp` also swaps whole words and changes what the speaker said: 腳本 → 指令碼, 用戶 → 使用者, 發布 → 釋出, 溢出 → 溢位 (2026-10-16). Fix wording by hand and list each fix in the 引用對照表.
- No speaker labels. Infer who is talking from content: 學員 explains, instructs, demonstrates, diagnoses; 客 describes their situation, asks, reacts; 員工 or 學生 in training or class recordings. Mark uncertain lines with（？）.
- **Transcripts that come with names (Zoom, Loom, a group Q&A) are hints, not facts.** Their speaker labels are often wrong: on 2026-10-15 Loom put the coach's lines under students' names, and two people's lines in one row. Judge the speaker from content, mark（？）when unsure, and say in the PDF that the editor should check the video.

## Step 1: Load the student's profile

Do this **before** transcribing, so the student is never asked questions after waiting through a long transcription.

Where the profile comes from, in this order:
1. **`我的資料.md`** in the folder the app opened (the same folder that holds `.agents` / `.claude`). If it exists, use it and don't ask again. Say one line in 繁中 so the student knows: 「用你上次存的資料：{我做什麼}，理想客戶是 {…}。要改的話直接跟我說。」
2. **教練's setup:** if the folder has `projects/<學員>/CLAUDE.md`, use that. Don't create `我的資料.md` there.
3. **Neither exists:** if the student already put the answers in their message, use those. Otherwise ask the three questions below. Then **write `我的資料.md` right away**, before transcribing, using the template at the end of this step. Tell the student in 繁中: 「已經幫你存成 我的資料.md，下次直接丟影片就好。」

Pull three things:

- **理想客戶** → the selection filter. Two-axis test: the customer (or staff member, or class participant) in the recording doesn't have to be the ideal customer, but the pain or mistake on screen must be the ideal customer's. If it matches, keep the clip, and write the 字卡 for the ideal customer, never about this person's individual situation. Solo recordings: the test is whether the mistake the student names is one the ideal customer makes.
- **事業體 + 重要背景** → the sensitivity list. Typical: customer identity, staff names, locations, amounts, internal pricing or numbers, anything the profile flags as not for public release (e.g. 獨家 info reserved for private lead nurturing).
- **陪跑主軸** → if it names a hook strategy (反差句型, 跨賽道鉤子), prefer hooks that fit it.

No profile? Ask three questions before running: 你做什麼（行業、店型或服務，不用名字）、理想客戶是誰、什麼不能公開. Never ask for the student's name; it isn't needed.

**Keep it up to date.** When the student corrects the profile (「理想客戶改成…」) or tells you a preference about the cut-list (「我不喜歡這種鉤子」「片段可以再長一點」「這個詞不要用」), update `我的資料.md` in the same turn and say so in one line. Read the 偏好 section on every run and follow it. Only write what the student actually said; never add guesses about them.

`我的資料.md` template:
```markdown
# 我的資料（長錄影選段會讀這份，可以自己改）

## 我做什麼
{行業、店型或服務（不用寫名字）}

## 理想客戶
{身分和狀態}

## 不能公開
{清單}

## 偏好
（還沒有。之後你說過的喜好會記在這裡。）
```

---

## The target: what a good clip looks like

- **Vertical 9:16, 30-90 秒 by default.** Under 30s feels thin. When fitting 90s would mean cutting the reasoning in the middle (核心第 4 步), let the clip run as long as the reasoning needs and add「（偏長，約 X 秒）」to its title. No hard limit: the student and their editor decide how to trim (教練 2026-10-18).
- **Framing:** the student is the focus. In service recordings the hands, the work, and the result can be on screen too. The customer's face and identity follow the student's choice and the customer's consent.
- **Captions:** big bold centered, burned-in, keyword reversed to yellow.
- **Opens cold** on the tension or the bold claim. No warm-up. No CTA outro on screen (CTA goes in the caption text).
- **The winning pattern:** a real situation → the stuck point or mistake gets named → the student reframes or corrects (often bluntly) → one concrete action → a reaction. Works because the viewer sees their own situation. In service recordings the same pattern shows up as: customer mentions a habit → student stops them → explains why → shows what to do instead.

## 核心方法：先讀 `reference/core-method.md`

**動手前先讀 `reference/core-method.md`，全部照做。** 裡面寫的「專家」＝學員本人，「理想客戶」＝Step 1 從學員檔案拿到的理想客戶。

學員版在核心上多這幾條：

- **批評別人的話只提醒，不砍。** 核心第 9 步：標出是哪一句、風險（被同行點名、被檢舉、客訴），附上同一段裡的正向替代句，由學員自己決定要不要用。這類話常常就是學員的差異化（例：「有的仲介做完就不管你」），直接砍會砍掉賣點。
- **客戶同意是每一支的必填欄。** 錄影裡有錄到客人同意就寫「有錄到」並附時間碼；有錄到客人**限制條件**（「不要露臉」「只能拍背影」）要寫進那支的「不可掃到」，而且整份最上面要警告；沒錄到寫「待確認」；沒有客人出現或出聲寫「不需要」。
- **專家戲份不夠的好段落**，列「要補一段」，寫出請學員補錄的**題目**（例：「為什麼眼皮鬆垂保養做不到」），不要替學員寫台詞。
- **旅程階段先分**：核心第 1 步切段落之前，先寫出這支錄影涵蓋哪些旅程階段（見上面的表），各在哪個時間碼。一支錄影常常有好幾個階段，每個階段分開切。
- **錄影裡對 AI 說的話＝學員的備忘，先找出來。** 學員錄影時可能會直接對 AI 講話，例如「AI 注意，剛剛那段是重點」「幫我注意這段，我想剪」「剛剛那段重點是什麼，幫我記一下」「這段不要用」。核心第 1 步整份讀的時候，先把這些句子全部找出來（關鍵：對 AI／剪輯／選段講話，或「幫我注意」「幫我記」「剛剛那段」「這段不要」）。處理方式：
  - 「剛剛那段」指這句話**前面**的那個段落；「接下來這段」指後面的。指到的段落優先評估，想剪的一定要在 PDF 裡交代結果：有剪成一支，或為什麼剪不成（例：太短、客人同意未確認），能補救就列「要補一段」。
  - 學員說「這段不要用」「這段不能公開」的，那段直接排除，並寫進「不可掃到」。
  - 這句備忘本身**不能進任何片段**：下刀點要避開它，字幕、鉤子、字卡都不能用它。
  - 整份文件最上面放「你在錄影裡交代的」表：時間碼、學員原話、處理結果（對應第幾支）。沒有的話整個表拿掉。
- **多個短檔**（學員或助理一次傳很多支手機短片）：先列一張檔案總表（檔名、長度、內容一句話、有沒有講話），再挑。同一段訪談拍了兩個角度的，挑轉錄較乾淨的當主檔。沒有講話的檔列進「空鏡和補畫面」表。

---

## Flow

照核心第 1-14 步走，順序：

1. 讀學員資料（Step 1）。沒有就先問、先存，再往下
2. 轉錄（Step 0，給檔案才需要）
3. 核心第 1 步：整份讀完、寫讀到第幾分鐘、找出學員對 AI 說的備忘、分旅程階段、切段落、標雜訊空檔、寫全場地圖（問題清單、重整清單）
4. 核心第 2-5 步：每支寫「這支在講什麼」、專家是主角、四段＋教育鐵律、先定收尾再往回拉
5. 核心第 6-10 步：鎖開頭（候選＋備案）、字卡、定格點、保留停頓、批評提醒、講者
6. 核心第 11-13 步：評分分級合併、原話、回 SRT 驗時間碼
7. 做 PDF（下面）
8. 核心第 14 步自檢，交件

### 做 PDF
1. Write the cut-list as HTML using `reference/cutlist-template.html` as the skeleton. Fill the header (學員, 來源檔名, 日期, 總長), one `<section class="clip">` per clip under 可以直接剪 / 要補一段, then the 引用對照表 and caveats. Keep the template CSS untouched.
2. Save next to the transcript: `<影片檔名>-選段.html` (the video's file name without the extension).
3. Print to PDF. Find a Chromium browser first, Chrome before Edge on both platforms.

**macOS**, in this order:
```
/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge
```

**Windows**, in this order:
```
C:\Program Files\Google\Chrome\Application\chrome.exe
C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
```

Whichever exists first, the flags are identical:

```bash
"<browser path>" --headless --disable-gpu \
  --no-pdf-header-footer \
  --print-to-pdf="<same folder>/<影片檔名>-選段.pdf" \
  "file:///<absolute path to the html>"
```

On Windows the file URL needs forward slashes: `file:///C:/Users/.../選段.html`.

**None of them found:** stop there, keep the HTML, and tell the student in 繁中 to open the .html and print it from their browser (Cmd/Ctrl+P, 另存為 PDF). The HTML is already written at this point, so no work is lost. Say this plainly instead of failing silently.

4. Open page 1 of the PDF to confirm CJK rendered and nothing overflowed. The PDF is the only thing that goes to the student.

**Keep the approvals few.** Every command that runs outside the sandbox or deletes a file shows the student an approval pop-up. Print with the command above, once. Use this skill's own steps, not an app's built-in PDF tool. Keep everything in the `transcript/` folder; do not create `output/` or `tmp/` folders, and do not delete files (preview images you made can stay in `transcript/`).


### 交件

給 PDF 路徑。講清楚：哪幾支卡在客戶同意待確認、哪幾支需要學員補錄一句（題目是什麼）、哪幾支有批評別人的話要學員自己決定。提醒：下刀以影片為準，不是 SRT 秒數。

---

## Per-clip fields（每個 `<section class="clip">`）

- 標題（一句話，要看得出這支的答案；超過 90 秒的加「（偏長，約 X 秒）」）
- **這支在講什麼**：一兩句，理想客戶帶走的那件事＋學員的答案
- 前三秒鉤子（逐字，訪談可用問句＋回答）＋時間碼
- 開頭備案：1-2 句，各附時間碼（找不到寫無）
- 位置：開始 → 結束（時間碼到 0.1 秒，例 `25:37.7 → 25:51.0`；沒有時間碼就用第一句／最後一句原話）＋約 X 秒，跳剪每一段都列。**所有時間碼都寫到 0.1 秒**（核心第 13 步），剪輯師照這個找位置，剪輯工具也直接讀
- 四段：① 開頭鉤子 ② 問題 ③ 方法 ④ 收尾，各附時間碼；缺的那段寫清楚缺什麼、要補錄什麼題目
- 字幕逐句：清理成繁中的原話，每句標講者：（學員）（客）（員工）（學生）；不確定的標（？）
- 開頭字卡：這支的主題句，講出答案，可以兩行
- 定格點：全片最利的一句原話＋時間碼（沒有寫無）
- 保留停頓：哪裡、為什麼不能剪（沒有寫無）
- 看完會改變什麼：教育鐵律那一句
- 批評別人的話：哪一句、風險、正向替代句，學員自己決定（沒有寫無）
- 不可掃到：這支的敏感資訊＋客戶代稱（一位客人、一位老闆）＋客人提過的限制條件
- 客戶同意：有錄到（時間碼）／待確認／不需要

整份文件最上面：來源（檔名、支數、總長）、讀到第幾分鐘、全場地圖（這場在講什麼、反覆出現的主題、問題清單和重整清單，附時間碼和對應第幾支）、旅程階段分布、客戶同意的警告（有客人限制條件的話）、「你在錄影裡交代的」表（有的話）。最後：空鏡和補畫面表、引用對照表（每一句引用 → 逐字稿原文和時間碼，改過的錯字標出來）、注意事項：時間碼到 0.1 秒，但自動轉錄會漂 0.2-0.5 秒，下刀以影片為準；簡體錯字已改繁體但仍要人工校對；客戶同意待確認的片先不剪；客戶的臉和身分照學員決定處理；講者標（？）的要看畫面確認；這份只讀逐字稿，沒有講出來的畫面可能沒被選到，剪輯師看到好畫面可以自己補。

## Writing rules

- **Every message to the student is in 繁體中文**, not only the PDF: progress updates, questions, error explanations, and especially the final handoff summary. The student may not read English. Keep tool names and file names as they are.
- 繁體中文. No emoji, no 破折號 (use commas or periods), no AI 罐頭語 (「其實」「說白了」「不是 X 而是 Y」openers).
- The PDF is read by a student and their editor: no coach jargon in visible text. Use 可以直接剪 / 要補一段, not Tier or Pattern.
