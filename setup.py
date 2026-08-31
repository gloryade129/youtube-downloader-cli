from setuptools import setup, find_packages

setup(
    name="yt-downloader-cli",
    version="1.0.0",
    description="Interactive YouTube search and multi-format downloader CLI system with heuristic AI search refinement.",
    author="Antigravity",
    packages=find_packages(),
    install_requires=[
        "yt-dlp>=2024.3.10",
        "rich>=13.7.0",
        "questionary>=2.0.1",
        "mutagen>=1.47.0",
        "click>=8.1.7",
        "Pillow>=10.0.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "yt-downloader=yt_downloader.cli:main",
            "ytmp3=yt_downloader.cli:main",
        ],
    },
    python_requires=">=3.8",
)
