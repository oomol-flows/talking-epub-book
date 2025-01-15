import re
import os

def main(params: dict):
  name: str | None = params["name"]
  files: list[str] = params["files"]
  files = [
    file
    for file in files 
    if not file.startswith(".")
  ]
  if name is None and len(files) > 0:
    file_name = os.path.basename(files[0])
    name = re.sub(r"_\d+\.\w+$", "", file_name)

  return { 
    "files": files,
    "name": name,
  }
