from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zotero-ocr",
    version="0.1.0",
    author="Giovanni Maggi",
    author_email="giovanni.maggi45@gmail.com",
    description="Convert PDF files to Markdown using Mistral's OCR API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/giomagg/zotero-ocr",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "mistralai>=0.0.12",
        "tqdm>=4.62.0",
    ],
    entry_points={
        "console_scripts": [
            "mistral-ocr=mistral_ocr_tool:main",
        ],
    },
)