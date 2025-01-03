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
        return self.op(items, 'sharp')

    def flat(self, items):
        return self.op(items, 'flat')

    def oct_higher(self, items):
        return self.op(items, 'oct_up')

    def oct_lower(self, items):
        return self.op(items, 'oct_down')

    def section(self, items):
        return NoteSection(self.op(items, ''))

    def line(self, items):
        return NoteLine(self.op(items, ''))

    def chapter(self, items):
        return NoteChapter(self.op(items, ''))

    def sheet(self, items):
        return Sheet(self.op(items, ''))
