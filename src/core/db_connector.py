import sqlite3
import os
import shutil
import tempfile
import logging
from contextlib import contextmanager

class ZoteroDB:
    def __init__(self, db_path):
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database not found at: {db_path}")
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        # Always create a temporary copy to avoid database locking issues
        # and to ensure a consistent snapshot while Zotero is running.
        fd, temp_path = tempfile.mkstemp(suffix=".sqlite", prefix="zotero_mirror_")
        os.close(fd)
        conn = None
        
        try:
            try:
                shutil.copy2(self.db_path, temp_path)
                # logging.info(f"Using temporary database copy: {temp_path}")
                
                # Connect to the temporary copy
                conn = sqlite3.connect(temp_path)
                conn.row_factory = sqlite3.Row
            except Exception as e:
                logging.error(f"Failed to copy or connect to database: {e}")
                if temp_path and os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                raise e

            yield conn
            
        finally:
            if conn:
                conn.close()
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception as e:
                    logging.warning(f"Failed to remove temp db {temp_path}: {e}")

    def get_all_collections(self):
        """
        获取所有 Collection 信息，构建 ID 到 Name 的映射，以及父子关系。
        返回: 字典列表 [{'collectionID': 1, 'collectionName': 'Name', 'parentCollectionID': None/ID}]
        """
        query = """
        SELECT collectionID, collectionName, parentCollectionID
        FROM collections
        ORDER BY collectionName
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def get_collection_items(self, collection_id):
        """
        获取指定 Collection 下的所有 Item (不包含子 Collection 的 Item)。
        只获取顶级 Item (非附件，非笔记)。
        """
        # collectionItems 表关联了 collection 和 item
        # items 表包含了 itemID 和 itemTypeID
        # itemTypes 表可以帮助我们过滤掉不想导出的类型（如 note, attachment），
        # 但我们需要找到 item 自身，然后再找它的 attachment。
        # 这里我们先只找 "常规条目" (isRegularItem usually means it has metadata)
        
        # Zotero schema:
        # items: itemID, itemTypeID
        # collectionItems: collectionID, itemID
        
        # 排除 note (1) 和 attachment (2) 类型? 具体的 ID 需要确认，但通常:
        # 我们可以查询 itemTypes 表，或者假设主要关注的是用来挂载附件的条目 (Document, Book, etc.)
        # 简单起见，我们选择所有在 collectionItems 中的 item，但这通常包含了 parent item。
        # 附件通常是 item 的子项 (parentItemID)。
        # 我们的逻辑是：找到 Collection 中的 Parent Items -> 找到这些 Parent Items 的 Attachments。
        
        query = """
        SELECT i.itemID, i.key, it.typeName
        FROM items i
        JOIN collectionItems ci ON i.itemID = ci.itemID
        JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
        WHERE ci.collectionID = ?
          AND it.typeName != 'note' 
          AND it.typeName != 'attachment'
        """
        # 注意：有时候 attachment 也可以直接在 collection 中吗？通常 attachment 依附于 item。
        # 如果有独立的 attachment (snapshot?) 在 collection 中，我们可能忽略或处理。
        # 这里的策略是：只导出 "父条目" 的附件。
        
        with self.get_connection() as conn:
            cursor = conn.execute(query, (collection_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_item_metadata(self, item_id):
        """
        获取 Item 的 Title, Date, Author。
        Zotero 使用 EAV 模型 (itemData, itemDataValues, fields)。
        这是一个简化的查询，可能需要根据 fieldName 动态聚合。
        """
        
        # 我们需要查找 fields 表来对应 fieldID
        # Common fields: 'title', 'date', 'publicationTitle', 'creators' (separate table)
        
        meta = {'title': 'No Title', 'date': '0000', 'author': 'NoAuthor'}
        
        # 1. Get Title and Date
        # Zotero 的某些字段 ID 是固定的吗？最好通过名字 join。
        query_data = """
        SELECT f.fieldName, v.value
        FROM itemData id
        JOIN itemDataValues v ON id.valueID = v.valueID
        JOIN fields f ON id.fieldID = f.fieldID
        WHERE id.itemID = ?
        """
        
        with self.get_connection() as conn:
            rows = conn.execute(query_data, (item_id,)).fetchall()
            for row in rows:
                name = row['fieldName']
                val = row['value']
                if name == 'title':
                    meta['title'] = val
                elif name == 'date':
                    # 提取年份
                    import re
                    match = re.search(r'\d{4}', val)
                    if match:
                        meta['date'] = match.group(0)
                        
        # 2. Get Dictionary/Author (Creators)
        # itemCreators table map itemID to creatorID
        # creators table has creatorData
        query_creator = """
        SELECT c.lastName
        FROM itemCreators ic
        JOIN creators c ON ic.creatorID = c.creatorID
        WHERE ic.itemID = ?
        ORDER BY ic.orderIndex
        LIMIT 1
        """
        with self.get_connection() as conn:
            cursor = conn.execute(query_creator, (item_id,))
            res = cursor.fetchone()
            if res:
                meta['author'] = res['lastName']
                
        return meta

    def get_child_attachments(self, parent_item_id):
        """
        查找属于该 item 的 attachment 文件。
        在新版 Zotero 中，附件信息主要在 itemAttachments 表中。
        """
        
        # Query itemAttachments for children of this parent
        # We also join items to get the key and potentially other info if needed (though path is often in itemAttachments now)
        # Note: itemAttachments has 'path' which is usually "storage:filename" or an absolute path
        query_attachments = """
        SELECT ia.itemID, i.key, ia.path, ia.contentType
        FROM itemAttachments ia
        JOIN items i ON ia.itemID = i.itemID
        WHERE ia.parentItemID = ?
        """
        
        attachments = []
        with self.get_connection() as conn:
            rows = conn.execute(query_attachments, (parent_item_id,)).fetchall()
            
            for row in rows:
                key = row['key']
                raw_path = row['path']
                
                # If path is None, sometimes it means it's just a database entry without a specific file path linked in this table?
                # or maybe it relies on standard storage location.
                
                if not raw_path:
                    # Fallback: check if we can infer or if it's a different type of attachment.
                    # Sometimes snapshots might not have a path listed here?
                    # Let's verify 'itemData' if path is missing, just in case (legacy support).
                    # But for now, let's assume raw_path is the source.
                     attachments.append({
                        'type': 'unknown',
                        'key': key,
                        'filename': None
                    })
                     continue

                if raw_path.startswith("storage:"):
                    filename = raw_path.split(":", 1)[1]
                    attachments.append({
                        'type': 'storage',
                        'key': key,
                        'filename': filename
                    })
                else:
                    # Absolute path (Linked File)
                    attachments.append({
                        'type': 'linked',
                        'path': raw_path,
                        'filename': os.path.basename(raw_path)
                    })
                    
        return attachments
