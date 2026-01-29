import os
import shutil
import logging
from .config import ConfigManager
from .db_connector import ZoteroDB
from .utils import sanitize_filename, get_file_category, safe_path_join

# Set up simple logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class MirrorExporter:
    def __init__(self):
        self.config = ConfigManager.get_instance()
        self.db = ZoteroDB(self.config.db_path)
        
    def export_collection(self, top_collection_name):
        """
        入口点：导出指定名称的 Collection 及其子 Collection
        """
        logging.info(f"Starting export for collection: {top_collection_name}")
        logging.info(f"DB Path: {self.config.db_path}")
        logging.info(f"Output Root: {self.config.output_root}")
        
        # 1. 获取所有 Collection 构建树
        all_collections = self.db.get_all_collections()
        # 构建 ID -> Info 映射
        col_map = {c['collectionID']: c for c in all_collections}
        # 构建 Parent -> Children 映射
        children_map = {}
        for c in all_collections:
            pid = c['parentCollectionID']
            if pid not in children_map:
                children_map[pid] = []
            children_map[pid].append(c)
            
        # 2. 找到目标根 Collection 的 ID
        root_col = next((c for c in all_collections if c['collectionName'] == top_collection_name), None)
        if not root_col:
            logging.error(f"Collection '{top_collection_name}' not found!")
            return
            
        # 3. 递归处理
        self._process_collection(root_col, [], children_map)
        logging.info("Export completed.")

    def _process_collection(self, current_col, path_stack, children_map):
        """
        current_col: 当前处理的 Collection 字典
        path_stack:  当前 Collection 在输出目录中的相对路径层级 (不包含 Category)
                     例如: ['My Thesis', 'Chapter 1']
        children_map: 树结构
        """
        col_name = sanitize_filename(current_col['collectionName'])
        new_stack = path_stack + [col_name]
        
        logging.info(f"Processing collection: {'/'.join(new_stack)}")
        
        # A. 处理当前 Collection 下的文件
        items = self.db.get_collection_items(current_col['collectionID'])
        for item in items:
            self._process_item(item, new_stack)
            
        # B. 递归处理子 Collection
        col_id = current_col['collectionID']
        if col_id in children_map:
            for child in children_map[col_id]:
                self._process_collection(child, new_stack, children_map)

    def _process_item(self, item, path_stack):
        """
        处理单个 Item，找到其附件并导出
        """
        item_id = item['itemID']
        
        # 1. 获取元数据
        meta = self.db.get_item_metadata(item_id)
        
        # 2. 构建目标文件名 core: [YYYY] Author - Title
        # 截断 author 和 title 避免过长?
        # utils.sanitize_filename 已经处理了非法字符和总长度
        
        # 组合 components
        date_str = meta.get('date', '0000')
        author_str = meta.get('author', 'NoAuthor')
        title_str = meta.get('title', 'NoTitle')
        
        base_filename = f"[{date_str}] {author_str} - {title_str}"
        base_filename = sanitize_filename(base_filename)
        
        # 3. 获取附件
        attachments = self.db.get_child_attachments(item_id)
        
        for att in attachments:
            src_path = None
            
            if att['type'] == 'storage' and att['filename']:
                # 拼接 storage 路径: <ZoteroData>/storage/<key>/<filename>
                src_path = os.path.join(self.config.storage_path, att['key'], att['filename'])
            elif att['type'] == 'linked':
                src_path = att['path']
            
            # 检查源文件是否存在
            if not src_path or not os.path.exists(src_path):
                logging.warning(f"File not found: {src_path} (Item: {base_filename})")
                continue
                
            # 4. 确定分类
            ext = os.path.splitext(att['filename'])[1] # .pdf
            category = get_file_category(ext, self.config.filter_rules)
            
            # 5. 构建最终输出路径
            # OutputRoot / Category / ColPath / [YYYY] ... .ext
            # 需要处理重名
            
            final_filename = base_filename + ext
            
            # 目标目录
            dest_dir = os.path.join(self.config.output_root, category, *path_stack)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                
            dest_path = os.path.join(dest_dir, final_filename)
            
            # 重名处理 - 追加 _1, _2
            counter = 1
            while os.path.exists(dest_path):
                name, e = os.path.splitext(final_filename)
                dest_path = os.path.join(dest_dir, f"{name}_{counter}{e}")
                counter += 1
                
            # 6. 复制
            try:
                shutil.copy2(src_path, dest_path)
                logging.info(f"Copied: {src_path} -> {dest_path}")
            except Exception as e:
                logging.error(f"Failed to copy {src_path}: {e}")

