import sys
import os
import json
from packager.packager import package_puml_files

if __name__ == "__main__":
    from c_to_plantuml.main import main as c2puml_main
    # Run the PlantUML generation
    c2puml_main()
    # Also call the packager main for restructure and cleanup
    from packager.main import main as packager_main
    packager_main() 