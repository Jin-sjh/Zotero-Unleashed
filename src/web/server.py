from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import uvicorn
import logging
import tkinter as tk
from tkinter import filedialog
import threading
from ..core.config import ConfigManager
from ..core.db_connector import ZoteroDB
from ..features.exporter import MirrorExporter
from ..ai.ai_processor import ai_processor

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebServer")

app = FastAPI(title="Zotero Controller Web UI")

# Allow CORS for development (if frontend runs separately, though here we serve it statically)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def build_tree(flat_collections):
    """
    Convert flat list of collections to a nested tree structure.
    Each node: { id, name, children: [] }
    """
    id_map = {c['collectionID']: {'id': c['collectionID'], 'name': c['collectionName'], 'children': []} for c in flat_collections}
    tree = []
    
    for c in flat_collections:
        pid = c['parentCollectionID']
        node = id_map[c['collectionID']]
        if pid and pid in id_map:
            id_map[pid]['children'].append(node)
        else:
            tree.append(node)
            
    return tree

@app.get("/api/collections")
async def get_collections():
    try:
        config = ConfigManager.get_instance()
        db = ZoteroDB(config.db_path)
        flat = db.get_all_collections()
        tree = build_tree(flat)
        return {
            "tree": tree, 
            "default_collection": config.default_collection,
            "output_root": config.output_root
        }
    except Exception as e:
        logger.error(f"Error fetching collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/browse-folder")
async def browse_folder():
    """
    Open a folder selection dialog and return the selected path.
    This runs in a separate thread to avoid blocking the main event loop.
    """
    try:
        def select_folder():
            root = tk.Tk()
            root.withdraw()
            root.wm_attributes('-topmost', 1)
            folder_path = filedialog.askdirectory(title="Select Output Folder")
            root.destroy()
            return folder_path
        
        result = [None]
        exception = [None]
        
        def run_in_thread():
            try:
                result[0] = select_folder()
            except Exception as e:
                exception[0] = str(e)
        
        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join()
        
        if exception[0]:
            raise HTTPException(status_code=500, detail=exception[0])
        
        if not result[0]:
            return {"path": ""}
        
        return {"path": result[0]}
    except Exception as e:
        logger.error(f"Error browsing folder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export")
async def run_export(payload: Dict[str, Any] = Body(...)):
    """
    Payload: {
        "root_collection": "My Library",
        "mask": { ... },
        "output_root": "C:/Target" (Optional)
    }
    """
    try:
        root_collection = payload.get("root_collection")
        mask = payload.get("mask")
        output_root = payload.get("output_root")
        
        if not root_collection:
             raise HTTPException(status_code=400, detail="root_collection is required")
             
        # Update Output Root if provided
        if output_root:
            config = ConfigManager.get_instance()
            config.output_root = output_root
            logger.info(f"Updated output root to: {output_root}")
             
        logger.info(f"Received export request for '{root_collection}'")
        
        exporter = MirrorExporter()
        exporter.export_collection(root_collection, path_mask=mask)
        
        return {"status": "success", "message": f"Export of '{root_collection}' completed."}
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/auto-tag")
async def auto_tag_literature(payload: Dict[str, Any] = Body(...)):
    """
    Automatically tag literature based on content analysis
    
    Payload: {
        "collection_id": "string",
        "options": {} (optional)
    }
    """
    try:
        collection_id = payload.get("collection_id")
        options = payload.get("options", {})
        
        if not collection_id:
            raise HTTPException(status_code=400, detail="collection_id is required")
        
        # Initialize ai_processor with database path
        config = ConfigManager.get_instance()
        ai_processor.set_db_path(config.db_path)
        
        logger.info(f"Received auto-tag request for collection: {collection_id}")
        
        results = await ai_processor.auto_tag_literature(collection_id, options)
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        logger.error(f"Auto-tag failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/classify-field")
async def classify_literature_field(payload: Dict[str, Any] = Body(...)):
    """
    Classify literature by research field based on content analysis
    
    Payload: {
        "collection_id": "string",
        "options": {} (optional)
    }
    """
    try:
        collection_id = payload.get("collection_id")
        options = payload.get("options", {})
        
        if not collection_id:
            raise HTTPException(status_code=400, detail="collection_id is required")
        
        # Initialize ai_processor with database path
        config = ConfigManager.get_instance()
        ai_processor.set_db_path(config.db_path)
        
        logger.info(f"Received classify-field request for collection: {collection_id}")
        
        results = await ai_processor.classify_by_research_field(collection_id, options)
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        logger.error(f"Classify field failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/duplicate-detection")
async def detect_duplicates(payload: Dict[str, Any] = Body(...)):
    """
    Detect potential duplicate literature entries
    
    Payload: {
        "collection_id": "string",
        "options": {"threshold": 0.8} (optional)
    }
    """
    try:
        collection_id = payload.get("collection_id")
        options = payload.get("options", {})
        
        if not collection_id:
            raise HTTPException(status_code=400, detail="collection_id is required")
        
        # Initialize ai_processor with database path
        config = ConfigManager.get_instance()
        ai_processor.set_db_path(config.db_path)
        
        logger.info(f"Received duplicate detection request for collection: {collection_id}")
        
        results = await ai_processor.detect_duplicates(collection_id, options)
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        logger.error(f"Duplicate detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/content-cluster")
async def cluster_content(payload: Dict[str, Any] = Body(...)):
    """
    Cluster literature based on content similarity
    
    Payload: {
        "collection_id": "string",
        "options": {"algorithm": "kmeans", "n_clusters": null} (optional)
    }
    """
    try:
        collection_id = payload.get("collection_id")
        options = payload.get("options", {})
        
        if not collection_id:
            raise HTTPException(status_code=400, detail="collection_id is required")
        
        # Initialize ai_processor with database path
        config = ConfigManager.get_instance()
        ai_processor.set_db_path(config.db_path)
        
        logger.info(f"Received content clustering request for collection: {collection_id}")
        
        results = await ai_processor.cluster_content(collection_id, options)
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        logger.error(f"Content clustering failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/enhanced-summarize")
async def enhanced_summarize_literature(payload: Dict[str, Any] = Body(...)):
    """
    使用大语言模型进行文献摘要
    
    Payload: {
        "collection_id": "string",
        "options": {} (optional)
    }
    """
    try:
        collection_id = payload.get("collection_id")
        options = payload.get("options", {})
        
        if not collection_id:
            raise HTTPException(status_code=400, detail="collection_id is required")
        
        # Initialize ai_processor with database path
        config = ConfigManager.get_instance()
        ai_processor.set_db_path(config.db_path)
        
        logger.info(f"Received enhanced summarize request for collection: {collection_id}")
        
        results = await ai_processor.enhanced_summarize_literature(collection_id, options)
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        logger.error(f"Enhanced summarize failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/process-batch")
async def process_batch_ai_tasks(payload: Dict[str, Any] = Body(...)):
    """
    Process multiple AI tasks in batch
    
    Payload: {
        "collection_id": "string",
        "tasks": ["auto-tag", "classify-field", "duplicate-detection", "content-cluster"],
        "options": {} (optional)
    }
    """
    try:
        collection_id = payload.get("collection_id")
        tasks = payload.get("tasks", [])
        options = payload.get("options", {})
        
        if not collection_id:
            raise HTTPException(status_code=400, detail="collection_id is required")
        
        if not tasks:
            raise HTTPException(status_code=400, detail="tasks list is required")
        
        # Initialize ai_processor with database path
        config = ConfigManager.get_instance()
        ai_processor.set_db_path(config.db_path)
        
        logger.info(f"Received batch AI processing request for collection: {collection_id}, tasks: {tasks}")
        
        results = {}
        
        for task in tasks:
            if task == "auto-tag":
                results["auto_tag"] = await ai_processor.auto_tag_literature(collection_id, options)
            elif task == "classify-field":
                results["classify_field"] = await ai_processor.classify_by_research_field(collection_id, options)
            elif task == "duplicate-detection":
                results["duplicate_detection"] = await ai_processor.detect_duplicates(collection_id, options)
            elif task == "content-cluster":
                results["content_cluster"] = await ai_processor.cluster_content(collection_id, options)
            else:
                logger.warning(f"Unknown task: {task}")
                results[task] = {"error": f"Unknown task: {task}"}
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        logger.error(f"Batch AI processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files (Frontend)
# We assume the 'web' folder is in the project root, one level up from 'src' if running from root.
# Actually, if we run `python web_server.py` from root, `web` is just `./web`.
import os
web_path = os.path.join(os.getcwd(), "web")
if os.path.exists(web_path):
    app.mount("/", StaticFiles(directory=web_path, html=True), name="static")
else:
    logger.warning(f"Web directory not found at {web_path}. Frontend will not be served.")