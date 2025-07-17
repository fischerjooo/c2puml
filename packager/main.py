import os
import json
import shutil
from packager.packager import package_puml_files

def main():
    # Always use test_config.json as the config file
    config_path = os.path.join(os.path.dirname(__file__), '..',  'test_config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    output_dir = config.get('output_dir', './uml_output')
    output_dir_packaged = config.get('output_dir_packaged', './uml_packaged_output')
    project_roots = config.get('project_roots', [])
    # Clean output_dir_packaged before packaging
    if output_dir_packaged and os.path.exists(output_dir_packaged):
        shutil.rmtree(output_dir_packaged)
    os.makedirs(output_dir_packaged, exist_ok=True)
    package_puml_files(output_dir, output_dir_packaged, project_roots) 

if __name__ == "__main__":
    main()