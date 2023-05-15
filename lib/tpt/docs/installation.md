# Installation

## SIM similarity test
- Compile SIM wrapper
- Install ....
    > pip install configparser
## Text extraction libraries

- phyton-docx

   * pre-requisites

        > sudo apt-get install libjpeg-dev mysql-dev

   * install

        > pip install python-docx

- textract (http://textract.readthedocs.io/en/latest/python_package.html)

    * prepare to install ffmpeg pre-requisite

        > sudo add-apt-repository ppa:mc3man/trusty-media
        > sudo apt-get update
        > sudo apt-get dist-upgrade

    * pre-requisites

        > sudo apt-get install python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils pstotext tesseract-ocr flac ffmpeg lame libmad0 libsox-fmt-mp3 sox

    * install

        > pip install textract

    * get more languages

        https://github.com/tesseract-ocr/tessdata


TODO: Describe all the installation steps
