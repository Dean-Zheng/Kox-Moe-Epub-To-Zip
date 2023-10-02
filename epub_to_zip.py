# -*- coding: utf-8 -*-

"""
@author: dean
@software: PyCharm
@file: epub_to_zip.py
@time: 2023/2/6 23:22
"""
import os
import time
import shutil
import tkinter
import zipfile
from ebooklib import epub
from lxml import etree
from tkinter import *
from tkinter.filedialog import askdirectory


class Converter:
    def __init__(self, file_path, target_path):
        self.file_path = file_path
        self.target_path = target_path

    def get_epub_title(self):
        book = epub.read_epub(self.file_path)
        title = book.get_metadata('DC', 'title')[0][0]
        book_path = str(self.target_path + os.sep + title)
        return book_path, title

    def extract_img_from_epub(self):
        extract_path = self.get_epub_title()[0]
        # prepare to read from .epub file
        with zipfile.ZipFile(self.file_path, mode='r') as _zip:
            # 读取html文件
            for _name in _zip.namelist():
                if _name[-5:] == '.html':
                    text = _zip.read(_name)
                    xml = etree.HTML(text)
                    # 读取 img 对应的图片路径
                    img_path = xml.xpath('//img/@src')[0][3:]
                    img_ext = xml.xpath('//img/@src')[0][-4:]
                    # 读取页码信息
                    page_info = xml.xpath('/html/head/title/text()')[0]
                    if img_ext == '.jpg':
                        try:
                            # 解压缩图片
                            _zip.extract(img_path, extract_path)
                            # 按编号顺序改名
                            os.rename(extract_path + '/' + img_path, extract_path + '/' + page_info + '.jpg')
                        except Exception as e:
                            print(e)
                    elif img_ext == '.png':
                        try:
                            # 解压缩图片
                            _zip.extract(img_path, extract_path)
                            # 按编号顺序改名
                            os.rename(extract_path + '/' + img_path, extract_path + '/' + page_info + '.png')
                        except Exception as e:
                            print(e)
                    elif '.' not in img_ext:
                        pass
                    else:
                        print('不支持的图片格式！！')
            # 删除已经为空的image文件夹
            shutil.rmtree(extract_path + '/' + 'image')

    def zip_images(self):
        book_path, title = self.get_epub_title()
        filelist = os.listdir(book_path)
        _zip = zipfile.ZipFile(book_path + '.zip', 'w', zipfile.ZIP_DEFLATED)
        for file in filelist:
            file_full_path = os.path.join(book_path, file)
            # file_full_path是文件的全路径，file是文件名，这样压缩时不会带多层目录
            _zip.write(file_full_path, file)
        _zip.close()
        shutil.rmtree(book_path)
        print(title + '.zip  创建成功！')
        return title


class Application:
    def __init__(self, window):
        self.window = window
        self.epub_path = StringVar()
        self.zip_path = StringVar()
        self.epub_path_text = Entry(self.window, textvariable=self.epub_path, state='readonly', width=35)
        self.zip_path_text = Entry(self.window, textvariable=self.zip_path, state='readonly', width=35)
        self.log_message = Text(self.window, width=55, height=8)

    def window_box(self):
        """
        调节各部件在窗口中的位置
        :return:
        """
        # 标题和标签
        self.window.title('Mox.moe epub提取')
        Label(self.window, text='.epub文件存放路径', fg='grey').grid(row=0, sticky='w')
        Label(self.window, text='转换后.zip保存路径', fg='grey').grid(row=2, sticky='w')
        Label(self.window, text='详细信息', fg='grey').grid(row=5, sticky='w')

        # 文本框
        self.epub_path_text.grid(row=1, sticky='w')
        self.zip_path_text.grid(row=3, sticky='w')
        self.log_message.grid(row=6, padx=2, pady=2)
        self.log_message.config(state=tkinter.DISABLED)  # 默认禁用文本小部件响应键盘和鼠标事件

        # 按钮
        Button(self.window, text='选择路径', command=self.select_epub_path).grid(row=1, sticky='e')
        Button(self.window, text='选择路径', command=self.select_zip_path).grid(row=3, sticky='e')
        Button(self.window, text='开始转换', command=self.start_convert).grid(row=4)

    def select_epub_path(self):
        path_ = askdirectory()  # 使用askdirectory()方法返回文件夹的路径
        if path_ == "":
            self.epub_path.get()  # 当打开文件路径选择框后点击"取消" 输入框会清空路径，所以使用get()方法再获取一次路径
        else:
            path_ = path_.replace("/", os.sep)  # 替换为操作系统路径符
            self.epub_path.set(path_)

    def select_zip_path(self):
        path_ = askdirectory()  # 使用askdirectory()方法返回文件夹的路径
        if path_ == "":
            self.zip_path.get()  # 当打开文件路径选择框后点击"取消" 输入框会清空路径，所以使用get()方法再获取一次路径
        else:
            path_ = path_.replace("/", os.sep)  # 替换为操作系统路径符
            self.zip_path.set(path_)

    def log_show(self, message):
        self.log_message.config(state=tkinter.NORMAL)  # 启用文本小部件响应键盘和鼠标事件
        current_time = get_time()
        message_in = str(current_time) + " " + message + "\n"  # 换行
        self.log_message.insert(END, message_in)
        self.log_message.see(END)  # 滚动到末尾行
        self.log_message.config(state=tkinter.DISABLED)

    def error_log_show(self, message):
        self.log_message.config(state=tkinter.NORMAL)
        current_time = get_time()
        message_in = str(current_time) + " " + message + "\n"  # 换行
        self.log_message.insert(END, message_in, 'a')
        self.log_message.tag_config("a", foreground="red")
        self.log_message.see(END)
        self.log_message.config(state=tkinter.DISABLED)

    def start_convert(self):
        start_time = time.time()
        self.log_message.delete(1.0, END)
        self.window.update()
        Application.log_show(self, '格式转换中...')
        self.window.update()
        epub_path = self.epub_path_text.get()
        output_path = self.zip_path_text.get()
        if epub_path == '' or output_path == '':
            Application.error_log_show(self, '路径不能为空！')
            return False
        # 开始转换程序
        epub_names = os.listdir(epub_path)
        for epub_name in epub_names:
            try:
                root, _ext = os.path.splitext(epub_path + os.sep + epub_name)
                if _ext == '.epub':
                    file_dir = root + _ext
                    trans = Converter(file_dir, output_path)
                    trans.extract_img_from_epub()
                    success_title = trans.zip_images()
                    Application.log_show(self, f'{success_title}.zip 转换成功！')
                    self.window.update()
            except Exception as e:
                Application.error_log_show(self, str(e).strip("'") + f'! 出错文件名：“{epub_name}”')
        # 显示转换用时
        finish_time = time.time()
        time_used = "{:.2f}".format(finish_time - start_time)
        Application.log_show(self, f'耗时{time_used}s。')


def get_time():
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return current_time


def main():
    tk = Tk()
    app = Application(tk)
    app.window_box()
    tk.mainloop()


if __name__ == '__main__':
    main()
