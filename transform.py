from lark import Transformer, Token
from itertools import chain
from typing import Any, List, Union, Dict, Literal, Set
from dataclasses import dataclass, field


    

@dataclass
class NotesInfo:
    notes: List['Note'] = field(default_factory=list)
    notes_cate: Set['Note'] = field(default_factory=set)
    octs_count: Dict[int, int] = field(default_factory=dict)
    octs_cate: Dict[int, int] = field(default_factory=dict)
    markers_count: Dict[Literal['sharp', 'flat', 'none'], int] = field(default_factory=dict)
    markers_cate: Dict[Literal['sharp', 'flat', 'none'], int] = field(default_factory=dict)


# 跨行的升降八度
class Operation:
    sep = ''
    def __init__(self) -> None:
        self.use_csharp = False
        self.with_oct = 0

    @property
    def sub_items(self) -> List['Operation']:
        return []

    def sharp(self):
        for item in self.sub_items:
            item.sharp()
        return self

    def flat(self):
        for item in self.sub_items:
            item.flat()
        return self

    def oct_up(self):
        for item in self.sub_items:
            item.oct_up()
        return self

    def oct_down(self):
        for item in self.sub_items:
            item.oct_down()
        return self
    
    def set_csharp(self, value: bool):
        self.use_csharp = value
        for item in self.sub_items:
            item.set_csharp(value)
        return self
    
    @property
    def info(self) -> NotesInfo:
        info = NotesInfo()
        for item in self.sub_items:
            sub_info = item.info
            info.notes.extend(sub_info.notes)
            info.notes_cate |= sub_info.notes_cate
            for key, value in sub_info.octs_count.items():
                info.octs_count[key] = info.octs_count.get(key, 0) + value
            for key, value in sub_info.markers_count.items():
                info.markers_count[key] = info.markers_count.get(key, 0) + value
        for note in info.notes_cate:
            for oct in note.oct:
                info.octs_cate[oct] = info.octs_cate.get(oct, 0) + 1
            info.markers_cate['sharp'] = info.markers_cate.get('sharp', 0) + note.sharp_format
            info.markers_cate['flat'] = info.markers_cate.get('flat', 0) + note.flat_format
            info.markers_cate['none'] = info.markers_cate.get('none', 0) + note.none_format
        return info
    def __str__(self):
        return self.sep.join([item.__str__() for item in self.sub_items])

class Note:
    basic_index = [0, 2, 4, 5, 7, 9, 11]
    def __init__(self, note_num: int) -> None:
        self.index = self.basic_index[note_num-1]
        self.use_csharp = False
        self.basic_out = True
         
    
    def __hash__(self) -> int:
        return self.index
    def __eq__(self, other) -> int:
        return self.index == other.index
    def __str__(self) -> str:
        info = self.out_info()


        paren = '[]' if info['oct'] > 0 else '()'
        count = abs(info['oct'])
        note = paren[0] * count + info['prefix'] + info['base'] + paren[1]*count

        return note

    def out_info(self) -> Dict[Literal['base', 'prefix', 'oct'], Any]:
        """给定条件下输出指定的形式"""
        oct = self.index // 12
        if (note_index := self.index % 12) in self.basic_index:
            base = str(self.basic_index.index(note_index) + 1)
            prefix = ''
        else:
            base = str(self.basic_index.index(note_index-1) + 1)
            prefix = '#'
        
        if self.use_csharp:            
            if self.basic_out and base == '1' and prefix == '':
                base, prefix, oct = '7', '#', oct-1
            elif self.basic_out and base == '4' and prefix == '':
                base, prefix = '3', '#'

            prefix = '' if prefix == '#' else 'b'
        else:
            if (not self.basic_out) and base == '1' and prefix == '':
                base, prefix, oct = '7', '#', oct-1
            elif (not self.basic_out) and base == '4' and prefix == '':
                base, prefix = '3', '#'
        
        return {
            'base': base,
            'prefix': prefix,
            'oct': oct
        }

        
        

    @property
    def sharp_format(self):
        return ((self.index - 1) % 12 in self.basic_index)

    @property
    def none_format(self):
        return self.index % 12 in self.basic_index

    @property
    def flat_format(self):
        return ((self.index + 1) % 12 in self.basic_index)
    
    @property
    def oct(self):
        o = self.index // 12
        return (o,) if self.index % 12 else (o, o-1)
    
    def sharp(self):
        self.index += 1
        return self

    def flat(self):
        self.index -= 1
        return self

    def oct_up(self):
        self.index += 12
        return self

    def oct_down(self):
        self.index -= 12
        return self
    
    def set_csharp(self, value: bool):
        self.use_csharp = value
        return self
    
    @property
    def info(self):
        return NotesInfo([self], set([self]), {oct: 1 for oct in self.oct}, 
            markers_count={'sharp': self.sharp_format,
            'flat': self.flat_format, 'none': self.none_format})

class NoteSection(Operation):
    sep = ''
    def __init__(self, tokens: List[Union[Note, 'NoteSection']]) -> None:
        self.notes: List[Note] = []
        for token in tokens:
            if isinstance(token, Note):
                self.notes.append(token)
                continue
        
            if isinstance(token, self.__class__):
                self.notes.extend(token.notes)
                continue
            
            print('unknow token', token, token.__dict__, type(token))
            raise
        super().__init__()
        
    
    @property
    def sub_items(self):
        return self.notes



class NoteLine(Operation):
    sep = ' '
    def __init__(self, sections: List[NoteSection]) -> None:
        self.sections = sections
        super().__init__()
    @property
    def sub_items(self):
        return self.sections
            
class NoteChapter(Operation):
    sep = '\n'
    def __init__(self, lines: List[NoteLine]) -> None:
        self.lines = lines
        super().__init__()
    @property
    def sub_items(self):
        return self.lines

class Sheet(Operation):
    sep = '\n\n'
    def __init__(self, chapters: List[NoteChapter]) -> None:
        self.chapters = chapters
        super().__init__()
    @property
    def sub_items(self):
        return self.chapters

class JeTransformer(Transformer):
    def num_note(self, items):
        assert len(items) == 1
        return Note(int(items[0]))
    
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

@dataclass
class Config:
    csharp_cate_threshold: int = 2  # 可以容忍的不能用C#记谱的音符种类数
    csharp_percentage_threshold: float = 0.15  # 可以容忍的不能用C#记谱的音符出现次数占比

class Format:
    def __init__(self, sheet: Sheet) -> None:
        self.sheet = sheet
        self.config = Config()
    
    def analyse_sheet(self):
        for chapter in self.sheet.chapters:
            self.analyse_chapter(chapter)
        if all([chapter.use_csharp for chapter in self.sheet.chapters]):
            self.sheet.use_csharp = True
        octs = [s.with_oct for s in self.sheet.chapters]
        self.sheet.with_oct = self.get_oct(octs)
    
    def analyse_chapter(self, chapter: NoteChapter):
        info = chapter.info
        fit_count = (info.markers_count['sharp']/len(info.notes)) >= (1-self.config.csharp_percentage_threshold)
        fit_cate = (len(info.notes_cate) - info.markers_cate['sharp']) <= self.config.csharp_cate_threshold

        if fit_count and fit_cate:
            chapter.set_csharp(True)

        for line in chapter.lines:
            self.analyse_line(line)
        
        octs = [s.with_oct for s in chapter.lines]
        chapter.with_oct = self.get_oct(octs)
    
    def analyse_line(self, line: NoteLine):
        for section in line.sections:
            self.analyse_section(section)
        octs = [s.with_oct for s in line.sections]
        line.with_oct = self.get_oct(octs)

    def analyse_section(self, section: NoteSection):
        grouped_notes = []
        last = None
        for note in section.notes:
            special = True if note.index in (1,5) else False
            if last is None:
                last = special
                grouped_notes.append([note])
                continue
            
            if last == special:
                grouped_notes[-1].append(note)
            else:
                grouped_notes.append([note])
            last = special

        length = len(grouped_notes)-1
        for i, notes in enumerate(grouped_notes):
            if notes[0].index not in (1,5):
                continue
            
            if i > 0:
                prefix = grouped_notes[i-1][-1].out_info()['prefix']
            elif i < length:
                prefix = grouped_notes[i+1][0].out_info()['prefix']
            else: prefix = None  # 无用

            if prefix:
                for note in notes:
                    note.basic_out = False
        
        octs = [n.out_info()['oct'] for n in section.notes]
        section.with_oct = self.get_oct(octs)
    
    @staticmethod
    def get_oct(octs):
        if (res := min(octs)) > 0:
            r = res
        elif (res := max(octs)) < 0:
            r = res
        else:
            r = 0

        return r
    
    def output(self):
        print(self.sheet)
