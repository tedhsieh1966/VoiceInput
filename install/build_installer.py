# VoiceInputInstaller/build.py
import os
import PyInstaller.__main__
import shutil


def build_installer():
    # 清理之前的构建
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

    # 复制主应用程序
    voiceinput_exe = "../dist/voiceinput.exe"
    if os.path.exists(voiceinput_exe):
        shutil.copy(voiceinput_exe, "src")

    filenames_needed = ["listen_128.png", "no_listen_128.png","languages.xlsx"]
    for filename_needed in filenames_needed:
        filepath_needed = f"../src/{filename_needed}"
        if os.path.exists(filepath_needed):
            shutil.copy(filepath_needed, "src")

    # 创建构建命令
    build_args = [
        'src/installer.py',
        '--onefile',
        '--windowed',
        '--name=VoiceInputInstaller',
        '--icon=src/listen_128.png',
        '--add-data=src/voiceinput.exe;.',
        '--add-data=src/listen_128.png;.',
        '--add-data=src/no_listen_128.png;.',
        '--add-data=src/languages.xlsx;.',
       # '--add-data=src/config.json;.',
       # '--distpath=dist',
       # '--workpath=build',
       # '--specpath=build'
    ]

    # 执行构建
    PyInstaller.__main__.run(build_args)
    print("安装程序构建完成！可执行文件在 dist 目录中")


if __name__ == '__main__':
    build_installer()