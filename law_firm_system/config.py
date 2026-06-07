import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据库配置
DB_PATH = os.path.join(BASE_DIR, "db", "law_db.sqlite")
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 安全配置
SECRET_KEY = "lawfirm2026syskey"

# 上传文件配置
UPLOAD_FOLDER = os.path.join(BASE_DIR, "upload")
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "jpg", "jpeg", "png", "xls", "xlsx"}

# 分页配置
ITEMS_PER_PAGE = 15

# 提醒配置
REMIND_DAYS_BEFORE = 3  # 提前3天提醒
