from .core import NoteSection, NoteLine, NoteChapter, Sheet


class JeFormatter:
    def __init__(self, sheet: 'Sheet') -> None:
        self.sheet = sheet

    def analyse(self):
        self.sheet.analyse_csharp()
        self.sheet.analyse_oct()

    @staticmethod
    def add_oct(s, oct):
        symbol = '[]' if oct > 0 else '()'
        count = abs(oct)
        return symbol[0]*count + s + symbol[1] * count

    @staticmethod
    def add_oct_multi_line(blocks, sep: str, oct):
        symbol = '[]' if oct > 0 else '()'
        count = abs(oct)
        if count != 0:
            body = sep.join(['  ' + line for line in blocks])
            return f'{symbol[0]*count}\n{body}\n{symbol[1]*count}'
        return sep.join(blocks)

    def output_sheet(self):
        if self.sheet.use_csharp and self.sheet.can_output_mark:
            prefix = '1=C#' + Sheet.sep
        else:
            prefix = ''
        chaps = [self.output_chapter(chap) for chap in self.sheet.chapters]
        return prefix + self.add_oct_multi_line(chaps, Sheet.sep, self.sheet.with_oct)

    def output_chapter(self, chapter: 'NoteChapter'):
        if chapter.use_csharp and chapter.can_output_mark:
            prefix = '1=C#' + NoteChapter.sep
        else:
            prefix = ''

        lines = [self.output_line(line) for line in chapter.lines]
        return prefix + self.add_oct_multi_line(lines, NoteChapter.sep, chapter.with_oct)

    def output_line(self, line: 'NoteLine'):
        sections = [self.output_section(section) for section in line.sections]
        oct_sections = self.add_oct(NoteLine.sep.join(sections), line.with_oct)
        if not line.use_csharp or not line.can_output_mark:
            return oct_sections

        if line.with_oct == 0:
            return f'#{{{oct_sections}}}'
        else:
            return f'#{oct_sections}'

    def output_section(self, section: 'NoteSection'):
        notes = [str(note) for note in section.notes]
        new_s: list[str] = []
        for s in ''.join(notes):
            if not new_s:
                new_s.append(s)
                continue
            if new_s[-1] + s in ('][', ')('):  # type: ignore
                del new_s[-1]
                continue
            new_s.append(s)
        oct_s = self.add_oct(NoteSection.sep.join(new_s), section.with_oct)

        if (not section.use_csharp) or (not section.can_output_mark):
            return oct_s

        if section.with_oct == 0:
            return f'#{{{oct_s}}}'
        else:
            return f'#{oct_s}'
