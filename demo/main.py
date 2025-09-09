import sys
from pathlib import Path

# 获取项目根目录 (sanic-demo)
BASE_DIR = Path(__file__).resolve().parent.parent

# 将项目根目录添加到系统路径
sys.path.insert(0, str(BASE_DIR))

from sanic import Sanic
from sanic.worker.loader import AppLoader

from internal.handler.routes import register_handlers


def create_app(name="hello"):

    app = Sanic(name)
    # 注册路由
    register_handlers(app)
    # 添加配置
    app.config.ACCESS_LOG = True
    app.config.DEBUG = True
    return app

app = create_app()

def main():
    # 使用 AppLoader 加载应用
    loader = AppLoader(factory=lambda: app)  # 使用 lambda 返回已创建的应用

    # 获取应用实例
    app_instance = loader.load()

    # 启动应用
    app_instance.prepare(
        host="0.0.0.0",
        port=8000,
        workers=4,
        auto_reload=True
    )

    # 启动 Sanic 服务器
    Sanic.serve(app_instance)


if __name__ == "__main__":
    main()