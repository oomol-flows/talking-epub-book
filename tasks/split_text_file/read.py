from charset_normalizer import from_bytes

def read(file_path: str, encoding: str | None) -> str:
  if encoding is None:
    with open(file_path, mode="rb") as file:
      content = file.read()
      results = from_bytes(content).best()
      if results is None:
        encoding = "utf_8"
      else:
        encoding = results.encoding
      return content.decode(encoding)
  else:
    # https://docs.python.org/3.10/library/codecs.html#standard-encodings
    with open(file_path, mode="r", encoding=encoding) as file:
      return file.read()