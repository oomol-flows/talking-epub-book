import os

from oocana import Context
from shared import format_number
from .spine_finder import Spines

def main(params: dict, context: Context):
  epub_file_path: str = params["epub_file_path"]
  output_path: str | None = params["output_path"]

  if output_path is None:
    output_path = os.path.join(context.session_dir, context.job_id)
    os.makedirs(output_path, exist_ok=True)

  with Spines(epub_file_path) as spines:
    current_title: str | None = None
    for i, (title, lines) in enumerate(spines.read()):
      if title is not None:
        current_title = title
      if current_title is None and spines.has_nav:
        continue # nav 是存在的，却无法被导航到，可能是 styles 之类的页面

      file_name = format_number(i, spines.spines_len)
      if current_title is not None:
        file_name += f"_{current_title}"
      file_name += ".txt"
      file_path = os.path.join(output_path, file_name)

      with open(file_path, mode="w", encoding="utf-8") as file:
        for line in lines:
          file.write(line)
          file.write("\n")

  return { "output_path": output_path }