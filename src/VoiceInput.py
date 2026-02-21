import sys
import os
import json
import threading
import keyboard
import speech_recognition as sr
from pathlib import Path
import time
import queue
import win32con
import win32api
import psutil
import pystray
from PIL import Image, ImageDraw
from typing import List,  Optional, Any
#from py_library.FileOp import get_full_path
#from py_libraries.LanguageOp import *
#sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
from LanguageOp import *
from config import ConfigManager


PHRASE_TIME_LENGTH=10
# 狀態視窗位置和大小 (x, y, width, height)
STATUS_INDICATOR_GEOMETRY=(10, 10, 150, 40)
INPUT_GAP = 0.05

STATUS_DURATION = 2  # 狀態顯示持續時間

def get_full_path(relative_path):
    """获取资源的绝对路径"""
    try:
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        full_path = os.path.join(base_path, relative_path)
        return full_path
    except:
        return None

translator = LanguageTranslator(get_full_path("languages.xlsx"))
sys_lang = get_current_input_language().get("iso_code")
if sys_lang in translator.get_languages():
    my_language = sys_lang
else:
    my_language = translator.get_languages()[0]
#my_language = "zh-TW"


def translate(text):
    return translator.get_translation(text, my_language)

def show_error_dialog(title, message):
    """显示错误对话框"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(title, message)
    except Exception as e:
        print(f"无法显示错误对话框: {str(e)}")
        print(f"原始错误: {title} - {message}")

def check_get_full_path(relative_path):
    full_path = get_full_path(relative_path)
    if full_path:
        return full_path
    else:
        show_error_dialog(translate("missing_document"),
                          translate("cannot_find_document")+f": {relative_path}")
        sys.exit(1)

# 加载资源文件
try:
    excel_path = check_get_full_path("languages.xlsx")
    print(f"资源文件找到: {excel_path}")
except Exception as e:
    #if IS_LOG:
    #    logging.error(f"资源文件加载失败: {str(e)}")
    show_error_dialog(translate("resource_error"),
                      translate("cannot_load_resource")+f": {str(e)}")
    sys.exit(1)




class VoiceInput:
    def __init__(self):

        self.recognizer = sr.Recognizer()
        #self.microphone = None
        self.is_listening = False
        self.is_toggling = False
        self.stop_listening = None
       # self.status_window = None
        self.status_queue = queue.Queue()
        self.running = True

        self.tray_icon = None
        # 加载图标图像
        self.listen_image = self._load_image("listen_128.png")
        self.no_listen_image = self._load_image("no_listen_128.png")
        self.default_image = self._load_image("no_listen_128.png")  # 默认使用 no_listen 图标
        self.config_mgr = ConfigManager()
        self.setup()
        self.status_thread = threading.Thread(target=self._status_manager, daemon=True)
        self.status_thread.start()
        print("連續語音輸入程式已啟動")



    def _load_image(self, filename):
        """加载图像文件，如果找不到则创建默认图像"""
        try:
            script_dir = Path(__file__).parent
            image_path = script_dir / filename

            # 如果图像文件存在，加载它
            if image_path.exists():
                image = Image.open(image_path)

                # 调整大小为64x64（系统托盘图标的标准大小）
                if image.size != (64, 64):
                    image = image.resize((64, 64), Image.LANCZOS)
                return image
        except Exception as e:
            print(f"加载图像 {filename} 失败: {str(e)}")

        # 创建默认图像作为后备
        print(f"创建 {filename} 的替代图像")
        image = Image.new('RGB', (64, 64), (128, 128, 128))
        dc = ImageDraw.Draw(image)
        dc.text((20, 20), "?", fill=(255, 255, 255))
        return image

    def setup(self):
        # 檢查並載入麥克風校準設定
        self.calib_file = Path.home() / ".voice_input_calib.json"
        if self.calib_file.exists():
            try:
                with open(self.calib_file, 'r') as f:
                    calib_data = json.load(f)
                self.recognizer.dynamic_energy_threshold = calib_data.get("dynamic_threshold", True)
                self.recognizer.energy_threshold = calib_data.get("energy_threshold", 300)
                self.recognizer.pause_threshold = calib_data.get("pause_threshold", 0.8)
            except:
                self.calibrate_mic()
        else:
            self.calibrate_mic()

    #    self.initialize_microphone()

    #def initialize_microphone(self):
    #    """初始化麦克风对象，确保每次使用都是新的实例"""
    #    try:
    #        if self.microphone:
    #            try:
    #                self.microphone.__exit__(None, None, None)
    #            except:
    #                pass
    #        self.microphone = sr.Microphone()
    #        print("麥克風已初始化")
    #    except Exception as e:
    #        print(f"麥克風初始化失敗: {str(e)}")
    #        self.microphone = None
#
    def calibrate_mic(self):
        print("正在校準麥克風，請保持安靜...")

        try:
            with sr.Microphone() as source:
                # 增加校準時間和次數
                self.recognizer.adjust_for_ambient_noise(source, duration=5)
                # 二次校準確保準確性
                time.sleep(1)
                self.recognizer.adjust_for_ambient_noise(source, duration=3)

            # 調整閾值更靈敏
            self.recognizer.energy_threshold = max(200, self.recognizer.energy_threshold - 100)
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.6  # 降低暫停閾值

            calib_data = {
                "energy_threshold": self.recognizer.energy_threshold,
                "dynamic_threshold": self.recognizer.dynamic_energy_threshold,
                "pause_threshold": self.recognizer.pause_threshold
            }
            with open(self.calib_file, 'w') as f:
                json.dump(calib_data, f)
            print(f"麥克風校準完成: 能量閾值={self.recognizer.energy_threshold}")
            self.status_queue.put((translate("calib_done"), "green"))
        except Exception as e:
            print(f"校準失敗: {str(e)}")
            self.status_queue.put((translate("calib_fail"), "red"))

    def toggle_listening(self):
        if self.is_toggling:
            return
        self.is_toggling = True

        if self.is_listening:
            self.status_queue.put((translate("stopped"), "red"))
            threading.Thread(target=self.stop_continuous_listening, daemon=True).start()

        else:
            #self._update_active_window()
            self.status_queue.put((translate("starting"), "orange"))
            threading.Thread(target=self.start_continuous_listening, daemon=True).start()
       # if self.is_listening:
       #     self.stop_continuous_listening()
       # else:
       #     self.start_continuous_listening()
        self._update_tray_icon()
        self.is_toggling = False



    def start_continuous_listening(self):
        if self.is_listening:
            return

        print("開始連續語音識別...")
        self.is_listening = True
        #self.show_status_indicator("🟢 正在聆聽...", geometry=STATUS_INDICATOR_GEOMETRY)
        self.status_queue.put((translate("listening"), "green"))

        #if not self.microphone:
        #    self.initialize_microphone()
        ## 在背景線程中啟動連續語音識別
        #threading.Thread(target=self._start_background_listening, daemon=True).start()

        try:
            # 在背景線程中啟動連續語音識別
            threading.Thread(target=self._start_background_listening, daemon=True).start()
        except Exception as e:
            print(f"啟動連續語音識別失敗: {str(e)}")
            self.is_listening = False
            self.status_queue.put((translate("start_fail"), "red"))

    def _start_background_listening(self):
        try:
            # 每次使用新的麦克风实例
            source = sr.Microphone()
            print(f"使用麦克风: {source}")
            self.stop_listening = self.recognizer.listen_in_background(
                source,
                self._process_audio,
                phrase_time_limit=PHRASE_TIME_LENGTH  # 每段語音最長10秒
            )
            # 保持线程运行
            while self.is_listening:
                time.sleep(0.1)
        except Exception as e:
            print(f"背景聆聽錯誤: {str(e)}")
            self.is_listening = False
            self.status_queue.put(("❌" + translate("listen_error"), "red"))
            #self.hide_status_indicator()

    def _process_audio(self, recognizer, audio):
        try:
            text = recognizer.recognize_google(audio, language=my_language)
            if text:
                send_text_via_clipboard(text)
        except sr.UnknownValueError:
            print("無法識別語音")
        except sr.RequestError as e:
            print(f"語音服務錯誤: {str(e)}")
            if self.is_listening:
                self.status_queue.put(("⚠️"+ translate("network_error"), "red"))
                self.stop_continuous_listening()
        except Exception as e:
            print(f"處理音訊時發生錯誤: {str(e)}")

    def stop_continuous_listening(self):
        if not self.is_listening:
            return

        print("停止連續語音識別")
        self.is_listening = False

        if self.stop_listening:
            try:
                self.stop_listening(wait_for_stop=False)
            except:
                pass
            self.stop_listening = None

        self.status_queue.put(("🔴"+translate("stopped"), "gray"))

        #time.sleep(2)
        #self.hide_status_indicator()

       # self.initialize_microphone()
    def _status_manager(self):
        """狀態管理線程，使用系統托盤圖標"""
        # 創建初始圖示
        self.tray_icon = pystray.Icon(
            "voice_input",
            #self._create_icon("就緒", "gray"),
            self.default_image,  # 使用加载的图像
            translate("voice_input_tool"),
          #  action=self.toggle_listening,
            menu=pystray.Menu(
                pystray.MenuItem(translate("toggle"), self.toggle_listening),
                pystray.MenuItem(translate("calib_microphone"), self.calibrate_mic),
                pystray.MenuItem(translate("exit"), self.quit_app)
            )
        )
        # 在當前線程中運行托盤圖示
        self.tray_icon.run_detached()
        # 啟動托盤圖標
        #threading.Thread(target=self.tray_icon.run, daemon=True).start()

        while self.running:
            try:
                # 檢查是否有新狀態
                if not self.status_queue.empty():
                    text, color = self.status_queue.get()
                    new_icon = self._create_icon(text, color)

                    # 更新圖示和標題
                    self.tray_icon.icon = new_icon
                    self.tray_icon.title = translate("voice_input")+f": {text}"
                    self.tray_icon.update_menu()

                time.sleep(0.1)
            except Exception as e:
                print(f"狀態管理器錯誤: {str(e)}")
                time.sleep(1)

        # 退出時移除托盤圖標
        #self.tray_icon.stop()

    def _update_tray_icon(self):
        """更新托盘图标"""
        if self.tray_icon:
            if self.is_listening:
                self.tray_icon.icon = self.listen_image
                self.tray_icon.title = translate("voice_input")+": "+translate("listening")
            else:
                self.tray_icon.icon = self.no_listen_image
                self.tray_icon.title = translate("voice_input")+": "+translate("stopped")
            self.tray_icon.update_menu()

    def _create_icon(self, text, color):
        if color == "green" and self.is_listening:
            return self.listen_image
        else:
            return self.no_listen_image


    def quit_app(self):
        """退出應用程序"""
        self.running = False
        self.stop_continuous_listening()
        self.tray_icon.stop()
        os._exit(0)

    def run(self):
        # 註冊全局快捷鍵
        hot_key = self.config_mgr.get_hot_key()
        keyboard.add_hotkey(hot_key, self.toggle_listening)

        print(f"程式運行中，按 {hot_key} 開始/停止語音輸入")
        print("按 Ctrl+C 退出程式")

        try:
            # 主循環保持程式運行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_continuous_listening()
            print("\n程式已退出")


def is_already_running():
    """檢查程式是否已在運行"""
    current_pid = os.getpid()
    current_script = Path(__file__).resolve().name

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.pid == current_pid:
                continue

            if 'python' in proc.name().lower() or 'pythonw' in proc.name().lower():
                cmdline = " ".join(proc.cmdline())
                if current_script in cmdline and "run" in cmdline:
                    return True
        except:
            continue

    return False


import win32clipboard
def send_text_via_clipboard(text):
    try:
        # 保存当前剪贴板内容
        win32clipboard.OpenClipboard()
        try:
            old_text = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        except:
            old_text = None
        win32clipboard.CloseClipboard()

        # 设置新文本到剪贴板
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()

        # 模拟粘贴
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        win32api.keybd_event(ord('V'), 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.1)

        # 恢复剪贴板内容
        if old_text is not None:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(old_text, win32con.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
        return True
    except Exception as e:
        print(f"剪贴板方法失败: {str(e)}")
        return False





if __name__ == "__main__":
    # 檢查是否已運行
    if is_already_running():
        print("程式已在運行中")
        sys.exit(0)


    app : VoiceInput = VoiceInput()
    app.run()
