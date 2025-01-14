import os

from oocana import Context
from shared import format_number

def main(params: dict, context: Context):
  fragments: list[str] = params["fragments"]
  save_dir_path: str = params["save_dir_path"]
  title: str | None = params["title"]

  for i, fragment in enumerate(fragments):
    audio_file: str = ""
    if len(fragments) > 0:
      audio_file = format_number(i, len(fragments))
    if title is not None:
      audio_file = f"{title}_{audio_file}"
    if audio_file == "":
      audio_file = "target"
    audio_file += ".mp3"
    audio_path = os.path.join(save_dir_path, audio_file)
    context.output("text", fragment)
    context.output("audio_path", audio_path)
