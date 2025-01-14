import re
import io
import os
import zipfile

from oocana import Context
from lxml.etree import parse
from shared.epub import EpubContent

def main(params: dict, context: Context):
  epub_file_path: str = params["epub_file_path"]
  unzip_path = _unzip(
    file_path=epub_file_path,
    unzip_path=os.path.join(context.session_dir, context.job_id),
  )
  epub_content = EpubContent(unzip_path)
  nav_list = _nav_list(epub_content)
  spines = _gen_spines(epub_content, nav_list)
  output_dir_path = os.path.join(context.session_dir, context.job_id)
  os.makedirs(output_dir_path, exist_ok=True)

  titles: list[str | None] = []
  spine_paths: list[str] = []
  current_title: str | None = None

  for i, (title, content) in enumerate(spines):
    if title is not None:
      current_title = title
    no = _format_number(i, len(spines))
    file_path = os.path.join(output_dir_path, f"{no}.txt")
    with open(file_path, mode="w", encoding="utf-8") as file:
      for line in parse(content).xpath("//text()"):
        file.write(line)
        file.write("\n")
    titles.append(current_title)
    spine_paths.append(file_path)
  
  return {
    "titles": titles,
    "spine_paths": spine_paths,
    "output_dir_path": output_dir_path,
  }

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
  return unzip_path

def _nav_list(epub_content: EpubContent):
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

def _gen_spines(epub_content: EpubContent, nav_list: list[tuple[str, str]]):
  spines = epub_content.spines
  result: list[tuple[str | None, str]] = []

  for index, spine in enumerate(spines):
    if spine.media_type == "application/xhtml+xml":
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

def _format_number(i: int, n: int) -> str:
  i_str = str(i)
  n_str = str(n)
  num_zeros = len(n_str) - len(i_str)
  formatted_i = "0" * num_zeros + i_str
  return formatted_i