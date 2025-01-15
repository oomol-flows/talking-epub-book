import re

from lxml.etree import HTML
from html import escape

def create_node(node_str: str, parser):
  return HTML(node_str, parser=parser).find("body/*")

def escape_ascii(content: str) -> str:
  content = escape(content)
  content = re.sub(
    r"\\u([\da-fA-F]{4})", 
    lambda x: chr(int(x.group(1), 16)), content,
  )
  return content

def format_number(i: int, n: int) -> str:
  i_str = str(i)
  n_str = str(n)
  num_zeros = len(n_str) - len(i_str)
  formatted_i = "0" * num_zeros + i_str
  return formatted_i