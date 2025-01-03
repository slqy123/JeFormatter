from lark import Transformer, Token
from .core import Note, NoteSection, NoteLine, NoteChapter, Sheet


class JeTransformer(Transformer):
    offset = 0

    @classmethod
    def set_offset(cls, offset):
        cls.offset = offset
        return cls

    def num_note(self, items):
        assert len(items) == 1
        note = Note(int(items[0]))
        note.index += self.offset
        return note

    def op(self, items, func):
        res = []
        for item in items:
            if isinstance(item, list):
                res.extend(self.op(item, func))
            else:
                if func:
                    res.append(getattr(item, func)())
                else:
                    res.append(item)
        return res

    def sharp(self, items):
        return self.op(items, "sharp")

    def flat(self, items):
        return self.op(items, "flat")

    def oct_higher(self, items):
        return self.op(items, "oct_up")

    def oct_lower(self, items):
        return self.op(items, "oct_down")

    def section(self, items):
        return NoteSection(self.op(items, ""))

    def line(self, items):
        return NoteLine(self.op(items, ""))

    def chapter(self, items):
        return NoteChapter(self.op(items, ""))

    def sheet(self, items):
        return Sheet(self.op(items, ""))

    @staticmethod
    def flatten(items):
        """递归展开多层列表"""
        res = []
        for item in items:
            if isinstance(item, list):
                res.extend(JeTransformer.flatten(item))
            else:
                res.append(item)
        return res

    def part_extened_oct_section(self, items):
        flat_items = self.flatten(items)
        if len(flat_items) == 2 and all(
            isinstance(item, NoteLine) for item in flat_items
        ):
            return NoteLine(
                [
                    *flat_items[0].sections[:-1],
                    NoteSection(
                        flat_items[0].sections[-1].notes
                        + flat_items[1].sections[0].notes
                    ),
                    *flat_items[1].sections[1:],
                ]
            )

        for i, item in enumerate(flat_items):
            if isinstance(item, NoteLine):
                index = i
                break
        else:
            raise Exception("未找到 NoteLine")

        left_notes = flat_items[:index]
        right_notes = flat_items[index + 1 :]

        line: NoteLine = flat_items[index]
        line.sections[0] = NoteSection(left_notes + line.sections[0].notes)
        line.sections[-1] = NoteSection(line.sections[-1].notes + right_notes)

        return line
