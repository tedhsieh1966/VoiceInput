# uninstaller.py
import os
import shutil
import win32com.client
from pathlib import Path
import tkinter as tk
from tkinter import messagebox


def uninstall():
    """卸载语音输入工具"""
    try:
        # 删除安装目录
        appdata_dir = Path(os.getenv('APPDATA'))
        install_dir = appdata_dir / "VoiceInput"
        if install_dir.exists():
            shutil.rmtree(install_dir)

        # 删除启动项
        startup_dir = Path(os.getenv('APPDATA')) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        shortcut_path = startup_dir / "VoiceInput.lnk"
        if shortcut_path.exists():
            os.remove(shortcut_path)

        # 删除桌面快捷方式
        desktop = Path(os.path.join(os.environ["USERPROFILE"], "Desktop"))
        desktop_shortcut = desktop / "语音输入工具.lnk"
        if desktop_shortcut.exists():
            os.remove(desktop_shortcut)

        messagebox.showinfo("卸载完成", "语音输入工具已成功卸载")
        return True
    except Exception as e:
        messagebox.showerror("卸载错误", f"卸载过程中发生错误:\n{str(e)}")
        return False


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    if uninstall():
        root.destroy()
    else:
        root.mainloop()