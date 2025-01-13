import os
import zipfile

from oocana import Context
from lxml.etree import parse, tostring
from shared.epub import EpubContent

def main(params: dict, context: Context):
  epub_file_path: str = params["epub_file_path"]
  unzip_path = _unzip(
    file_path=epub_file_path,
    unzip_path=os.path.join(context.session_dir, context.job_id),
  )
  epub_content = EpubContent(unzip_path)
  ncx_path = epub_content.ncx_path

  if ncx_path is not None:
    tree = parse(ncx_path)
    root = tree.getroot()
    namespaces={ "ns": root.nsmap.get(None) }
    text_doms = []
    text_list = []

    for nav_dom in root.xpath("//ns:navPoint", namespaces=namespaces):
      text_dom = nav_dom.xpath(".//ns:text", namespaces=namespaces)[0]
      content_dom = nav_dom.xpath(".//ns:content", namespaces=namespaces)[0]
      if text_dom is not None and content_dom is not None:
        text: str = text_dom.text
        src = content_dom.get("src")
        print(text, src)

    for text_dom in root.xpath("//ns:text", namespaces=namespaces):
      text_doms.append(text_dom)
      text_list.append(tostring(text_dom))

  print(ncx_path)



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