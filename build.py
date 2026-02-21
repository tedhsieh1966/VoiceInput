# VoiceInputApp/build.py
import os
import PyInstaller.__main__
import shutil


def build_app():
    # 清理之前的构建
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')

    # 创建构建命令
    build_args = [
        'src/VoiceInput.py',
        '--onefile',
        '--windowed',
        '--name=voiceinput',
        '--icon=src/no_listen_128.png',
        '--add-data=src/listen_128.png;.',
        '--add-data=src/no_listen_128.png;.',
        '--add-data=src/languages.xlsx;.',
        '--add-data=src/config.json;.',
       # '--distpath=dist',
       # '--workpath=build',
       # '--specpath=build'
    ]

    # 执行构建
    PyInstaller.__main__.run(build_args)

    # 复制配置文件（如果有）
    #if os.path.exists('src/config.json'):
    #    shutil.copy('src/config.json', 'dist')

    print("构建完成！可执行文件在 dist 目录中")


if __name__ == '__main__':
    build_app()