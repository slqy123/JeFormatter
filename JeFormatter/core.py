from itertools import chain
from typing import Any, List, Union, Dict, Literal, Set
from dataclasses import dataclass, field
from config import config


@dataclass
class NotesInfo:
    notes: List["Note"] = field(default_factory=list)
    notes_cate: Set["Note"] = field(default_factory=set)
    octs_count: Dict[int, int] = field(default_factory=dict)
    octs_cate: Dict[int, int] = field(default_factory=dict)
    markers_count: Dict[Literal["sharp", "flat", "none"], int] = field(
        default_factory=dict
    )
    markers_cate: Dict[Literal["sharp", "flat", "none"], int] = field(
        default_factory=dict
    )


# 跨行的升降八度
class Operation:
    sep = ""
    sub_type: Any

    def __init__(self, items: List["Operation"]) -> None:
        self.use_csharp = False
        self.can_output_mark = True
        self.with_oct = 0

        for item in items:
            if isinstance(item, self.__class__):
                self.sub_items.extend(item.sub_items)
                continue
            if isinstance(item, self.sub_type):  # type: ignore
                self.sub_items.append(item)
                continue

            print("unknow token", item, item.__dict__, type(item))

    @property
    def sub_items(self) -> List["Operation"]:
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

    def set_csharp(self):
        self.use_csharp = True
        for item in self.sub_items:
            item.can_output_mark = False
            item.set_csharp()
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
            info.markers_cate["sharp"] = (
                info.markers_cate.get("sharp", 0) + note.sharp_format
            )
            info.markers_cate["flat"] = (
                info.markers_cate.get("flat", 0) + note.flat_format
            )
            info.markers_cate["none"] = (
                info.markers_cate.get("none", 0) + note.none_format
            )
        return info

    def analyse_csharp(self):
        for item in self.sub_items:
            item.analyse_csharp()
        if all([item.use_csharp for item in self.sub_items]):
            self.use_csharp = True
            for item in self.sub_items:
                item.can_output_mark = False

    @staticmethod
    def get_oct(octs):
        if (res := min(octs)) > 0:
            r = res
        elif (res := max(octs)) < 0:
            r = res
        else:
            r = 0

        return r

    def analyse_oct(self):
        for item in self.sub_items:
            item.analyse_oct()
        octs = [item.with_oct for item in self.sub_items]
        self.with_oct = self.get_oct(octs)
        for item in self.sub_items:
            item.with_oct -= self.with_oct

    def __str__(self):
        return self.sep.join([item.__str__() for item in self.sub_items])


class Note:
    basic_index = [0, 2, 4, 5, 7, 9, 11]

    def __init__(self, note_num: int) -> None:
        self.index = self.basic_index[note_num - 1]
        self.use_csharp = False
        self.basic_out = True

    def __hash__(self) -> int:
        return self.index

    def __eq__(self, other) -> bool:
        return self.index == other.index

    def __str__(self) -> str:
        info = self.out_info()
        paren = "[]" if info["oct"] > 0 else "()"
        count = abs(info["oct"])
        note = paren[0] * count + info["prefix"] + info["base"] + paren[1] * count

        return note

    def out_info(self) -> Dict[Literal["base", "prefix", "oct"], Any]:
        """给定条件下输出指定的形式"""
        oct = self.index // 12
        if (note_index := self.index % 12) in self.basic_index:
            base = str(self.basic_index.index(note_index) + 1)
            prefix = ""
        else:
            base = str(self.basic_index.index(note_index - 1) + 1)
            prefix = "#"

        if self.use_csharp:
            if self.basic_out and base == "1" and prefix == "":
                base, prefix, oct = "7", "#", oct - 1
            elif self.basic_out and base == "4" and prefix == "":
                base, prefix = "3", "#"

            prefix = "" if prefix == "#" else "b"
        else:
            if (not self.basic_out) and base == "1" and prefix == "":
                base, prefix, oct = "7", "#", oct - 1
            elif (not self.basic_out) and base == "4" and prefix == "":
                base, prefix = "3", "#"

        return {"base": base, "prefix": prefix, "oct": oct}

    @property
    def sharp_format(self):
        return (self.index - 1) % 12 in self.basic_index

    @property
    def none_format(self):
        return self.index % 12 in self.basic_index

    @property
    def flat_format(self):
        return (self.index + 1) % 12 in self.basic_index

    @property
    def oct(self):
        o = self.index // 12
        return (o,) if self.index % 12 else (o, o - 1)

    @property
    def base_index(self):
        return self.index % 12

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

    def set_csharp(self):
        self.use_csharp = True
        return self

    @property
    def info(self):
        return NotesInfo(
            [self],
            set([self]),
            {oct: 1 for oct in self.oct},
            markers_count={
                "sharp": self.sharp_format,
                "flat": self.flat_format,
                "none": self.none_format,
            },
        )


class NoteSection(Operation):
    sep = ""
    sub_type = Note

    def __init__(self, notes: List[Any]):
        self.notes = []
        super().__init__(notes)

    def analyse_csharp(self):
        if (
            self.info.markers_count["sharp"]
            == len(self.info.notes)
            > self.info.markers_count["none"]
            >= 1
        ):
            self.set_csharp()

    def analyse_oct(self):
        grouped_notes = []
        last = None
        for note in self.notes:
            special = True if note.base_index in (0, 5) else False
            if last is None:
                last = special
                grouped_notes.append([note])
                continue

            if last == special:
                grouped_notes[-1].append(note)
            else:
                grouped_notes.append([note])
            last = special

        length = len(grouped_notes) - 1
        for i, notes in enumerate(grouped_notes):
            if notes[0].base_index not in (0, 5):
                continue

            if i > 0:
                prefix = grouped_notes[i - 1][-1].out_info()["prefix"]
            elif i < length:
                prefix = grouped_notes[i + 1][0].out_info()["prefix"]
            else:
                prefix = None  # 无用

            if prefix:
                for note in notes:
                    note.basic_out = False

        octs = [n.out_info()["oct"] for n in self.notes]
        self.with_oct = self.get_oct(octs)
        for note in self.notes:
            note.index -= self.with_oct * 12

    @property
    def sub_items(self):
        return self.notes


class NoteLine(Operation):
    sep = "  "
    sub_type = NoteSection

    def __init__(self, sections: List[Any]) -> None:
        self.sections = []
        super().__init__(sections)

    @property
    def sub_items(self):
        return self.sections


class NoteChapter(Operation):
    sep = "\n"
    sub_type = NoteLine

    def __init__(self, lines: List[Any]) -> None:
        self.lines = []
        super().__init__(lines)

    def analyse_csharp(self):
        info = self.info
        fit_count = (info.markers_count["sharp"] / len(info.notes)) >= (
            1 - config.csharp_percentage_threshold
        )
        fit_cate = (
            len(info.notes_cate) - info.markers_cate["sharp"]
        ) <= config.csharp_cate_threshold

        if fit_count and fit_cate:
            self.set_csharp()
            return

        super().analyse_csharp()

    @property
    def sub_items(self):
        return self.lines


class Sheet(Operation):
    sep = "\n\n"
    sub_type = NoteChapter

    def __init__(self, chapters: List[Any]) -> None:
        self.chapters = []
        super().__init__(chapters)

    @property
    def sub_items(self):
        return self.chapters
