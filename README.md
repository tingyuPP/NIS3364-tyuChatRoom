## NIS3364-tyuChatRoom

### 项目简介

本项目是NIS3364的大作业，实现了一个本地的多对多聊天程序。本项目前端基于PyQt5，使用了qfluentwidgets库的前端组件。客户端和服务器之间通过socket进行通信。后端使用sqlite3管理数据库。

### 运行方法

本项目在Windows系统上开发。

- 安装Python，经测试在Python 3.11.7下可正常运行。

- 在项目根目录打开终端。
  **注意：路径不要含中文！有中文可能会出现qt相关报错**

- 创建虚拟环境并激活
在终端输入以下命令：

```shell
pip3 install virutalenv
virtualenv venv
venv/Scripts/activate
```

- 安装所需软件包

```shell
pip install "PyQt-Fluent-Widgets[full]" -i https://pypi.org/simple/
```

若还有提示缺少软件包，请自行下载。

- 运行服务器
点击server.bat，服务器即可自动运行。
或在终端中输入

```shell
venv/Scripts/activate
cd server
python server.py
```

- 运行客户端
点击login.bat即可。但是由于一些原因，login.bat直接点击运行python会找不到包。这时请在终端手动进入虚拟环境

```shell
venv/Scripts/activate
```

再运行`./login.bat`