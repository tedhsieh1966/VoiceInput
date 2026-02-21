# VoiceInputInstaller/src/installer.py
import os
import sys
import shutil
import win32com.client
import ctypes
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from py_libraries.LanguageOp import *

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

class VoiceInputInstaller:
    def __init__(self):
        self.translator = LanguageTranslator(get_full_path("languages.xlsx"))
        sys_lang = get_current_input_language().get("iso_code")
        if sys_lang in self.translator.get_languages():
            self.my_language = sys_lang
        else:
            self.my_language = self.translator.get_languages()[0]

        self.root = tk.Tk()
        self.root.title(self.translator.get_translation("voice_input_tool_install_app", self.my_language))
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        # 设置图标
        try:
            self.root.iconbitmap(sys._MEIPASS + '\\installer.ico')
        except:
            pass

        self.create_widgets()

    def create_widgets(self):
        # 标题
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=20)

        tk.Label(title_frame, text=self.translator.get_translation("voice_input_tool", self.my_language), font=("Arial", 16, "bold")).pack()
        tk.Label(title_frame, text=self.translator.get_translation("voice_input_solution", self.my_language)).pack(pady=5)

        # 安装选项
        options_frame = tk.LabelFrame(self.root, text=self.translator.get_translation("install_options", self.my_language), padx=10, pady=10)
        options_frame.pack(fill="x", padx=20, pady=10)

        self.create_shortcut_var = tk.BooleanVar(value=True)
        self.start_on_boot_var = tk.BooleanVar(value=True)

        tk.Checkbutton(options_frame, text=self.translator.get_translation("create_desktop_shortcut", self.my_language),
                       variable=self.create_shortcut_var).pack(anchor="w", pady=5)
        tk.Checkbutton(options_frame, text=self.translator.get_translation("startup", self.my_language),
                       variable=self.start_on_boot_var).pack(anchor="w", pady=5)

        # 进度条
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(fill="x", padx=20, pady=10)

        self.progress = ttk.Progressbar(progress_frame, orient="horizontal",
                                        length=460, mode="determinate")
        self.progress.pack()

        # 按钮
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text=self.translator.get_translation("install", self.my_language), width=10, command=self.install).pack(side="left", padx=10)
        tk.Button(button_frame, text=self.translator.get_translation("exit", self.my_language), width=10, command=self.root.destroy).pack(side="right", padx=10)

    def is_admin(self):
        """检查是否以管理员权限运行"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def request_admin(self):
        """请求管理员权限"""
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    def check_get_full_path(self, relative_path):
        full_path = get_full_path(relative_path)
        if not full_path:
            show_error_dialog(self.translator.get_translation("missing_document", self.my_language),
                              self.translator.get_translation("cannot_find_document", self.my_language)+f": {relative_path}")
            sys.exit(1)

    def install(self):
        """执行安装过程"""
        #if not self.is_admin():
        #    self.request_admin()
        #    return
#
        try:
            # 确定安装目录
            appdata_dir = Path(os.getenv('APPDATA'))
            install_dir = appdata_dir / "VoiceInput"

            # 创建安装目录
            install_dir.mkdir(exist_ok=True)
            self.progress["value"] = 20

            # 复制文件
            source_dir = Path(sys._MEIPASS) if hasattr(sys, '_MEIPASS') else Path(__file__).parent
            exe_path = source_dir / "voiceinput.exe"

            if not exe_path.exists():
                messagebox.showerror(self.translator.get_translation("error", self.my_language),
                                     self.translator.get_translation("cannot_find_app", self.my_language) + "voiceinput.exe")
                return

            # 复制主程序
            dest_path = install_dir / "voiceinput.exe"
           # shutil.copy(exe_path, dest_path)
           # shutil.copy(source_dir / "config.json", install_dir)
           # self.progress["value"] = 40

            # 复制图标文件
           # shutil.copy(source_dir / "listen_128.png", install_dir)
           # shutil.copy(source_dir / "no_listen_128.png", install_dir)
           # self.progress["value"] = 60

            # 创建桌面快捷方式
            if self.create_shortcut_var.get():
                desktop = Path(os.path.join(os.environ["USERPROFILE"], "Desktop"))
                shortcut_path = desktop / "VoiceInput.lnk"

                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.TargetPath = str(dest_path)
                shortcut.WorkingDirectory = str(install_dir)
                shortcut.IconLocation = str(install_dir / "listen_128.png")
                shortcut.Save()

            self.progress["value"] = 80

            # 添加到开机启动
            if self.start_on_boot_var.get():
                startup_dir = Path(
                    os.getenv('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
                shortcut_path = startup_dir / "VoiceInput.lnk"

                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.TargetPath = str(dest_path)
                shortcut.WorkingDirectory = str(install_dir)
                shortcut.WindowStyle = 7  # 最小化启动
                shortcut.Save()

            self.progress["value"] = 100
            messagebox.showinfo(self.translator.get_translation("install_finished", self.my_language),
                                self.translator.get_translation("voice_input_tool_install_ok", self.my_language))
            self.root.destroy()

            # 启动应用程序
            os.startfile(str(dest_path))

        except Exception as e:
            messagebox.showerror(self.translator.get_translation("install_error", self.my_language),
                                 self.translator.get_translation("install_with_error", self.my_language)+f":\n{str(e)}")
            self.progress["value"] = 0


if __name__ == "__main__":
    app = VoiceInputInstaller()
    app.root.mainloop()