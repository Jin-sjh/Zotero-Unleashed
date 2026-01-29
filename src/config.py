import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

@dataclass
class ZoteroConfig:
    """Configuration for Zotero Controller"""
    
    # 优先从环境变量获取，否则尝试查找 Windows 默认路径
    zotero_data_dir: str = os.getenv("ZOTERO_DATA_DIR", os.path.expanduser(r"~\Zotero"))
    
    # 输出根目录
    output_root: str = os.getenv("EXPORT_OUTPUT_ROOT", os.path.join(os.getcwd(), "Zotero_Export"))
    
    # 默认导出的分类名称
    default_collection: str = os.getenv("DEFAULT_COLLECTION", "")

    # 数据库路径 (自动推导)
    @property
    def db_path(self):
        return os.path.join(self.zotero_data_dir, "zotero.sqlite")
    
    # Storage 路径 (自动推导)
    @property
    def storage_path(self):
        return os.path.join(self.zotero_data_dir, "storage")
    
    # 过滤规则
    filter_rules: dict = field(default_factory=lambda: {
        "PDF": [".pdf"],
        "Word": [".doc", ".docx"],
    })

class ConfigManager:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ZoteroConfig()
        return cls._instance

# Simple usage
config = ConfigManager.get_instance()
