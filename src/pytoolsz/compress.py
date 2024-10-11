#  ____       _____           _
# |  _ \ _   |_   _|__   ___ | |___ ____
# | |_) | | | || |/ _ \ / _ \| / __|_  /
# |  __/| |_| || | (_) | (_) | \__ \/ /
# |_|    \__, ||_|\___/ \___/|_|___/___|
#        |___/

# Copyright (c) 2024 Sidney Zhang <zly@lyzhang.me>
# PyToolsz is licensed under Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#          http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.

from pathlib import Path
import zipfile
import py7zr
import shutil
import os


def _get_extname(name:str|Path) -> str :
    txt = name if isinstance(name, str) else name.name
    return txt.split(".")[-1]

class compression(object):
    """
    快捷文件压缩解压缩。
    """
    MODES = ['7z','zip']
    __all__ = ["compress","extract","get_filenames",
               "append_file", "extract_file"]
    def __init__(self, mode:str = "7z",
                 password:str|None = None, 
                 keep_data:bool = True) -> None:
        if mode not in self.MODES :
            raise ValueError("mode must be in {}".format(self.MODES))
        self.__keep_data = keep_data
        self.__mode = mode
        if password :
            if mode == 'zip' :
                print("`zip` mode does not support encryption compression packaging!\n\n")
            else:
                txt = ["Encryption is performed using the AES-256 algorithm.",
                    "Compression algorithms generally do not support high-security encryption.",
                    "If a secure encryption scheme is needed,",
                    "please use a dedicated encryption program."]
                print("\n".join(txt))
        self.__password = password
    def _do7zcompress(self, filename:str, src:list[str|Path]) -> None :
        if self.__password is None :
            with py7zr.SevenZipFile(filename, 'w', dereference=True, 
                                    header_encryption = True) as archive:
                for xf in src:
                    if Path(xf).is_dir() :
                        archive.writeall(xf)
                    else :
                        archive.write(xf)
                    if not self.__keep_data :
                        try :
                            os.remove(xf)
                        except :
                            shutil.rmtree(xf)
        else :
            with py7zr.SevenZipFile(filename, 'w', dereference=True, 
                                    header_encryption = True, 
                                    password = self.__password) as archive:
                for xf in src:
                    if Path(xf).is_dir() :
                        archive.writeall(xf)
                    else :
                        archive.write(xf)
                    if not self.__keep_data :
                        try :
                            os.remove(xf)
                        except :
                            shutil.rmtree(xf)
    def _dozipcompress(self, filename:str, src:list[str|Path]) -> None :
        with zipfile.ZipFile(filename, 'w', compression=zipfile.ZIP_BZIP2,
                             compresslevel = 9) as archive:
            for xf in src:
                if Path(xf).is_dir() :
                    for xfi in Path(xf).glob('**/*.*'):
                        archive.write(xfi)
                else :
                    archive.write(xf)
                if not self.__keep_data :
                    try :
                        os.remove(xf)
                    except :
                        shutil.rmtree(xf)
    def compress(self, cfilename:str, 
                 src:str|Path|list[str|Path] = '.', 
                 dst:str|Path = '.') -> None :
        """
        压缩文件。
        cfilename:压缩后的文件名。
        src:源文件路径。
        dst:目标文件路径。
        """
        notChange = isinstance(src, list)
        soures = src if notChange else [src]
        tarPath = Path(dst)
        if tarPath.is_dir() :
            if not tarPath.exists() :
                tarPath.mkdir(parents=True)
        else :
            raise ValueError("dst must be a directory!")
        if not notChange :
            oriPath = os.getcwd()
            switchPath = Path(src).absolute().parent
            os.chdir(switchPath)
        xfname = '.'.join([cfilename, self.__mode])
        if self.__mode == '7z' :
            self._do7zcompress(tarPath/xfname, soures)
        else :
            self._dozipcompress(tarPath/xfname, soures)
        if not notChange :
            os.chdir(oriPath)
    def extract(self, src:str|Path, dst:str|Path) -> None :
        """
        解压缩文件。
        src:源文件路径。
        dst:目标文件路径。
        """
        self.__mode = _get_extname(src)
        if self.__mode == '7z' :
            with py7zr.SevenZipFile(src, 'r',
                                    password = self.__password) as archive:
                archive.extractall(path=dst)
        else:
            with zipfile.ZipFile(src, 'r') as archive:
                archive.extractall(path=dst, pwd=self.__password)
    def get_filenames(self, src:str|Path) -> list[str] :
        """
        获取压缩包内的文件列表。
        src:源文件路径。
        """
        self.__mode = _get_extname(src)
        if self.__mode == '7z' :
            with py7zr.SevenZipFile(src, 'r',
                                    password = self.__password) as archive:
                return archive.getnames()
        else:
            with zipfile.ZipFile(src, 'r') as archive:
                if self.__password :
                    archive.setpassword(self.__password)
                return archive.namelist()
    def append_file(self, src:str|Path, dst:str|Path) -> None :
        """
        追加文件到压缩包。
        src:待补充压缩的文件路径。
        dst:目标压缩文件路径。
        """
        self.__mode = _get_extname(dst)
        if self.__mode == '7z' :
            with py7zr.SevenZipFile(dst, 'a', dereference=True,
                                    header_encryption = True,
                                    password = self.__password) as archive:
                if Path(src).is_dir() :
                    archive.writeall(src)
                else :
                    archive.write(src)
        else :
            with zipfile.ZipFile(dst, 'a') as archive:
                if self.__password :
                    archive.setpassword(self.__password)
                if Path(src).is_dir() :
                    for xfi in Path(src).glob('**/*.*'):
                        archive.write(xfi)
                else :
                    archive.write(src)
        if not self.__keep_data :
            try :
                os.remove(src)
            except :
                shutil.rmtree(src)
    def extract_file(self, targets:str|list[str], src:str|Path, 
                     dst:str|Path = '.') -> None :
        """
        提取压缩包内的文件。
        targets:待提取的文件名。
        src:源压缩文件路径。
        dst:加压目标文件路径。
        """
        self.__mode = _get_extname(src)
        output = Path(dst)
        if output.is_dir() :
            if not output.exists() :
                output.mkdir(parents=True)
        else :
            raise ValueError("dst must be a directory!")
        if self.__mode == '7z' :
            with py7zr.SevenZipFile(src, 'r',
                                    password = self.__password) as archive:
                archive.extract(targets=targets, path=output, recursive=True)
        else :
            with zipfile.ZipFile(src, 'r') as archive:
                if isinstance(targets, str) :
                    archive.extract(targets, path=output, pwd=self.__password)
                else :
                    for xfi in targets:
                        archive.extract(xfi, path=output, pwd=self.__password)