from lark import Lark
from pathlib import Path
import sys
from transform import JeTransformer, Format

l = Lark(Path('je.lark').read_text(), start='sheet')
text = Path(sys.argv[1]).read_text().strip()
text = '\n'.join([line.strip() for line in text.splitlines()])
res = l.parse(text)
Path('out.txt').write_text(str(res.pretty()))

# print(list(res.find_data('num_note')))

tres = JeTransformer().transform(res)
print(tres)
format = Format(tres)
format.analyse_sheet()
format.output()

