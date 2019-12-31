import sys
import logging
from flask import Flask
from flask.logging import default_handler

# 字段/属性名称    使用格式               描述
# asctime         %(asctime)s           日志事件发生的时间--人类可读时间，如：2003-07-08 16:49:45,896
# created         %(created)f           日志事件发生的时间--时间戳，就是当时调用time.time()函数返回的值
# relativeCreated %(relativeCreated)d   日志事件发生的时间相对于logging模块加载时间的相对毫秒数（目前还不知道干嘛用的）
# msecs 	      %(msecs)d             日志事件发生事件的毫秒部分
# levelname       %(levelname)s         该日志记录的文字形式的日志级别（'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'）
# levelno 	      %(levelno)s           该日志记录的数字形式的日志级别（10, 20, 30, 40, 50）
# name            %(name)s              所使用的日志器名称，默认是'root'，因为默认使用的是 rootLogger
# message 	      %(message)s           日志记录的文本内容，通过 msg % args计算得到的
# pathname 	      %(pathname)s          调用日志记录函数的源码文件的全路径
# filename 	      %(filename)s          pathname的文件名部分，包含文件后缀
# module          %(module)s            filename的名称部分，不包含后缀
# lineno          %(lineno)d            调用日志记录函数的源代码所在的行号
# funcName        %(funcName)s          调用日志记录函数的函数名
# process         %(process)d           进程ID
# processName     %(processName)s       进程名称，Python 3.1新增
# thread          %(thread)d            线程ID
# threadName      %(thread)s            线程名称
#
# Usage: formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s')


def create_app(config=None):

    app = Flask(__name__)
    app.logger.info('before remove')
    app.logger.removeHandler(default_handler)

    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s %(pathname)s:%(lineno)s - %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    app.logger.info('after remove')

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
