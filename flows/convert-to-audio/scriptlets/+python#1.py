from oocana import Context
from shared import NLP

def main(params: dict, context: Context):
  fragments: list[str] = params["fragments"]
  nlp = NLP()
  count: int = 0
  for i, fragment in enumerate(fragments):
    count += nlp.count_word(fragment)
    context.report_progress(
      progress=i/len(fragments) * 100.0,
    )
  context.preview({
    "type": "json",
    "data": {
      "fragments": len(fragments),
      "count": count,
    },
  })