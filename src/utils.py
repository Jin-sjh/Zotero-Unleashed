import re
import os

def sanitize_filename(filename: str) -> str:
    """
    清洗文件名，移除 Windows/Linux 文件系统不支持的字符。
    保留中文、数字、字母、点、下划线、短横线、空格。
    """
    if not filename:
        return "Untitled"
        
    # 定义非法字符集合: \ / : * ? " < > |
    illegal_chars = r'[\\/:*?"<>|]'
    
    # 替换为空格
    sanitized = re.sub(illegal_chars, ' ', filename)
    
    # 去除多余空格和首尾空格
    sanitized = " ".join(sanitized.split())
    
    # 限制长度 (防止路径过长)
    if len(sanitized) > 150:
        sanitized = sanitized[:150]
        
    return sanitized

def get_file_category(extension: str, rules: dict) -> str:
    """
    根据文件扩展名确定分类 (PDF, Word, Other)
    extension 应该包含点，例如 '.pdf'
    """
    ext = extension.lower()
    for category, extensions in rules.items():
        if ext in extensions:
            return category
    return "Other"

def safe_path_join(*args):
    """
    安全地连接路径
    """
    return os.path.join(*args)
