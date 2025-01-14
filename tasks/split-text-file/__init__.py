import re

from oocana import Context
from io import StringIO
from .read import read
from .nlp import NLP

def main(params: dict, context: Context):
  file_path: str = params["file_path"]
  encoding: str | None = params["encoding"]
  chars_limit: int = params["chars_limit"]
  text = read(file_path, encoding)
  text = clean_text(text)
  fragments = list(split_text(text, chars_limit))
  return { "fragments": fragments }

def clean_text(text: str):
  text = re.sub(r"(\s*\n)+", "\n", text)
  text = re.sub(r"[^\S\r\n]+", " ", text)
  return text

def split_text(text: str, chars_limit: int):
  buffer = StringIO()
  buffer_len: int = 0

  for sent in NLP().split_into_sents(text):
    sent_len = len(sent)
    if buffer_len + sent_len > chars_limit and buffer_len > 0:
      yield buffer.getvalue()
      buffer = StringIO()
      buffer_len = 0
    buffer.write(sent)
    buffer_len += sent_len

  if buffer_len > 0:
    yield buffer.getvalue()
