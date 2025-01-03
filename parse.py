from typing import IO, cast, TYPE_CHECKING
from lark import Lark
from pathlib import Path
import sys
from JeFormatter import JeTransformer, JeFormatter
import click
import re
from io import TextIOWrapper

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

if TYPE_CHECKING:
    sys.stdin = cast(TextIOWrapper, sys.stdin)
    sys.stdout = cast(TextIOWrapper, sys.stdout)
sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("input_file", type=click.File("r", encoding="utf-8"), default=sys.stdin)
@click.argument("output", type=click.File("w", encoding="utf-8"), default=sys.stdout)
@click.option(
    "-o",
    "--offset",
    type=int,
    default=0,
    help="整体音高偏移，以半音为单位，例如 12 表示整体上升一个八度",
)
@click.option("--debug", is_flag=True, default=False, help="输出调试信息")
def main(input_file: IO, output: IO, offset: int, debug: bool):
    lark = Lark(
        (Path(__file__).parent / "je.lark").read_text(encoding="utf-8"),
        start="sheet",
    )

    input_str = input_file.read()
    input_str = re.sub(
        r"[^1-7#b\(\)\[\]（）【】♯♭\n\t\r\xa0 ]+", " ", input_str
    ).strip()
    input_str = "\n".join([line.strip() for line in input_str.splitlines()])

    res = lark.parse(input_str)

    if debug:
        Path(".debuginfo").write_text(str(res.pretty()))

    tres = JeTransformer.set_offset(offset)().transform(res)
    format = JeFormatter(tres)
    format.analyse()
    output.write(format.output_sheet())


main()
