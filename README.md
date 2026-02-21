🎙️ VoiceInput: 全域語音輸入助理 / Universal Voice Input Assistant
繁體中文 | English

<a name="繁體中文"></a>

📝 簡介
VoiceInput 是一款輕量級、高效的語音轉文字工具。它能讓你在 Windows 系統上的 任何編輯器、筆記軟體或通訊軟體 中，直接透過語音代替鍵盤輸入。

不再受限於特定的 App，只要能打字的地方，VoiceInput 就能幫你說話變文字！

✨ 核心特色
全域支援：支援 Notepad++, VS Code, Word, 瀏覽器, LINE, Discord 等任何文字輸入框。

背景監聽：一鍵開啟後即可在背景運行，不干擾工作流程。

剪貼簿模擬技術：採用穩定的剪貼簿模擬貼上技術，確保文字精準輸入且不影響原本的剪貼簿內容（輸入後會自動還原）。

智慧校準：內建麥克風環境噪音校準功能，提升在嘈雜環境下的辨識率。

多語系介面：自動偵測系統語系，支援多國語言介面與辨識。

系統托盤運行：簡潔的圖示狀態顯示，隨時掌握「聆聽中」或「已停止」狀態。

🛠️ 安裝與使用
環境需求：Python 3.x

安裝依賴庫：

```Bash
pip install speech_recognition keyboard pystray Pillow pywin32 psutil
```
執行程式：

```Bash
python VoiceInput.py
```
操作快捷鍵：

預設使用 熱鍵（可於 config.py 設定）來切換語音開啟/關閉。

在托盤圖示點擊右鍵可進行 麥克風校準。

💡 想要更多功能嗎？ 歡迎提交 Pull Request 或開 Issue 讓我們知道！

<a name="english"></a>

📝 Introduction
VoiceInput is a lightweight and efficient voice-to-text tool that allows you to use voice commands instead of keyboard typing in any editor, note-taking app, or messenger on Windows.

Break free from app-specific limitations—wherever you can type, VoiceInput can talk for you!

✨ Key Features
Global Compatibility: Works seamlessly with Notepad++, VS Code, Word, browsers, LINE, Discord, and any text input field.

Background Listening: Runs quietly in the background without interrupting your workflow.

Clipboard Simulation: Utilizes a stable "copy-paste" simulation to ensure accurate text entry while preserving your original clipboard history (restores automatically after typing).

Smart Calibration: Built-in ambient noise calibration to improve recognition accuracy in noisy environments.

Multi-language Support: Automatically detects system language and supports various languages for both UI and recognition.

System Tray Integration: Minimalist tray icon to quickly identify "Listening" or "Stopped" status.

🛠️ Installation & Usage
Requirement: Python 3.x

Install Dependencies:

```Bash
pip install speech_recognition keyboard pystray Pillow pywin32 psutil
```
Run the App:

```Bash
python VoiceInput.py
```
How to Use:

Use the Global Hotkey (configurable in config.py) to toggle voice input on/off.

Right-click the tray icon to perform Microphone Calibration for better accuracy.

📦 Project Structure
VoiceInput.py: Main application logic.

LanguageOp.py: Language processing and translation.

config.py: Configuration management (Hotkeys, thresholds, etc.).

languages.xlsx: Translation database.

💡 Want more features? Feel free to submit a Pull Request or open an Issue!