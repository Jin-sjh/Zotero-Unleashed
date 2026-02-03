import argparse
from src.core.config import ConfigManager
from src.features.exporter import MirrorExporter

def start_web_server():
    import uvicorn
    import sys
    import os
    # Ensure current directory is in python path
    sys.path.append(os.getcwd())
    print("Starting Zotero Controller Web UI...")
    print("Open your browser at: http://127.0.0.1:8000")
    uvicorn.run("src.web.server:app", host="127.0.0.1", port=8000, reload=False)

def main():
    config = ConfigManager.get_instance()
    
    parser = argparse.ArgumentParser(description="Zotero Unleashed - Mirror Exporter")
    
    # Optional arguments for CLI mode override
    parser.add_argument("collection", nargs='?', default=config.default_collection, 
                        help="Name of the root Zotero collection to export (optional if set in .env)")
    parser.add_argument("--out", help="Output directory root (overrides config)")
    parser.add_argument("--zotero-data", help="Zotero Data Directory (contains zotero.sqlite)")
    parser.add_argument("--web", action='store_true', help="Force launch Web UI")
    
    # We parse known args to allow mixed usage, but if --web or config_source=frontend is set, we might ignore others.
    args, unknown = parser.parse_known_args()
    
    # Update config overrides
    if args.out: config.output_root = args.out
    if args.zotero_data: config.zotero_data_dir = args.zotero_data

    # Check mode
    # If explicitly requested via flag OR configured in .env as 'frontend'/'web'
    is_web_mode = args.web or config.config_source.lower() in ['frontend', 'web']

    if is_web_mode:
        start_web_server()
        return

    # --- CLI / Backend Mode ---
    
    if not args.collection:
        print("Error: No collection specified for CLI mode.")
        print("Usage: python main.py <collection_name>")
        print("Or set DEFAULT_COLLECTION in .env, or use --web to launch UI.")
        return

    print("=== Configuration (CLI Mode) ===")
    print(f"Zotero Data: {config.zotero_data_dir}")
    print(f"Database:    {config.db_path}")
    print(f"Output Root: {config.output_root}")
    print("================================")
    
    try:
        path_mask = None # Backend mode exports everything under the root
        exporter = MirrorExporter()
        exporter.export_collection(args.collection, path_mask=path_mask)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
