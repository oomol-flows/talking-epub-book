def format_number(i: int, n: int) -> str:
  i_str = str(i)
  n_str = str(n)
  num_zeros = len(n_str) - len(i_str)
  formatted_i = "0" * num_zeros + i_str
  return formatted_i