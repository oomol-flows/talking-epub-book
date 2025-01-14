import re
import os
import shutil
import zipfile

from tempfile import mkdtemp
from typing import Generator
from lxml.etree import parse
from .epub_content import EpubContent

class Spines:
  def __init__(self, file_path: str) -> None:
    self._unzip_path: str = mkdtemp()
    _unzip(file_path, self._unzip_path)
    epub_content = EpubContent(self._unzip_path)
    self._nav_list: list[tuple[str, str]] = _nav_list(epub_content)
    self._spines: list[tuple[str | None, str]] = _gen_spines(epub_content, self._nav_list)

  @property
  def has_nav(self) -> bool:
    return len(self._nav_list) > 0

  @property
  def spines_len(self) -> int:
    return len(self._spines)

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    shutil.rmtree(self._unzip_path)

  def read(self) -> Generator[tuple[str | None, list[str]], None, None]:
    for title, path in self._spines:
      yield title, list(parse(path).xpath("//text()"))

def _unzip(file_path: str, unzip_path: str):
  with zipfile.ZipFile(file_path, "r") as zip_ref:
    for member in zip_ref.namelist():
      target_path = os.path.join(unzip_path, member)
      if member.endswith("/"):
        os.makedirs(target_path, exist_ok=True)
      else:
        target_dir_path = os.path.dirname(target_path)
        os.makedirs(target_dir_path, exist_ok=True)
        with zip_ref.open(member) as source, open(target_path, "wb") as file:
          file.write(source.read())

def _nav_list(epub_content: EpubContent) -> list[tuple[str, str]]:
  ncx_path = epub_content.ncx_path
  if ncx_path is None:
    return []

  tree = parse(ncx_path)
  root = tree.getroot()
  namespaces={ "ns": root.nsmap.get(None) }
  nav_list: list[tuple[str, str]] = []

  for nav_dom in root.xpath("//ns:navPoint", namespaces=namespaces):
    text_dom = nav_dom.xpath(".//ns:text", namespaces=namespaces)[0]
    content_dom = nav_dom.xpath(".//ns:content", namespaces=namespaces)[0]
    if text_dom is not None and content_dom is not None:
      text: str = text_dom.text
      href = _standardize_href(content_dom.get("src"))
      nav_list.append((href, text))
  
  return nav_list

def _gen_spines(epub_content: EpubContent, nav_list: list[tuple[str, str]]) -> list[tuple[str | None, str]]:
  result: list[tuple[str | None, str]] = []
  for spine in epub_content.spines:
    if spine.media_type != "application/xhtml+xml":
      continue
    href = _standardize_href(spine.href)
    title = _nav_title(nav_list, href)
    result.append((title, spine.path))
  return result

def _nav_title(nav_list: list[tuple[str, str]], checked_href: str):
  for href, title in nav_list:
    if checked_href == href:
      return title
  return None

def _standardize_href(href: str) -> str:
  return re.sub(r"^\./", "", href)