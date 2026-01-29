import argparse
from src.config import ConfigManager
from src.exporter import MirrorExporter

def main():
    config = ConfigManager.get_instance()
    
    parser = argparse.ArgumentParser(description="Zotero Unleashed - Mirror Exporter")
    parser.add_argument("collection", nargs='?', default=config.default_collection, 
                        help="Name of the root Zotero collection to export (optional if set in .env)")
    parser.add_argument("--out", help="Output directory root (overrides config)")
    parser.add_argument("--zotero-data", help="Zotero Data Directory (contains zotero.sqlite)")
    
    args = parser.parse_args()
    
    if not args.collection:
        parser.error("The 'collection' argument is required either as a command line argument or in the .env file (DEFAULT_COLLECTION).")

    if args.out:
        config.output_root = args.out
    
    if args.zotero_data:
        config.zotero_data_dir = args.zotero_data
        
    print("=== Configuration ===")
    print(f"Zotero Data: {config.zotero_data_dir}")
    print(f"Database:    {config.db_path}")
    print(f"Output Root: {config.output_root}")
    print("====================")
    
    try:
        exporter = MirrorExporter()
        exporter.export_collection(args.collection)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
