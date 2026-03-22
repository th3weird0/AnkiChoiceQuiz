import csv
import re
from pathlib import Path
from collections import OrderedDict

# =========================
# 配置
# =========================
INPUT_TXT = "input.txt"
OUTPUT_CSV = "output_anki_clean.csv"

FIELDNAMES = [
    "Stem", "A", "B", "C", "D", "E",
    "CorrectLetters", "Answer", "Type", "Tags"
]

# =========================
# 基础清理
# =========================

def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def normalize_spaces(text: str) -> str:
    text = text.replace("\u3000", " ")
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_trailing_punctuation(text: str) -> str:
    return re.sub(r"[。．\.；;：:，,\s]+$", "", text).strip()


def strip_question_number(text: str) -> str:
    text = text.strip()
    patterns = [
        r"^\d+\s*[\.、)]\s*",
        r"^[（(]\s*\d+\s*[）)]\s*",
        r"^【\s*\d+\s*】\s*",
    ]
    for p in patterns:
        text = re.sub(p, "", text)
    return text.strip()


# =========================
# 行类型判断
# =========================

def is_comment_line(line: str) -> bool:
    """
    忽略注释/出处/页码/资料等说明性行
    例如：
    【注释】: 动画简史第13页xxxx
    【出处】: xxx
    【来源】: xxx
    """
    line = line.strip()
    if not line:
        return False

    explicit_patterns = [
        r"^【注释】",
        r"^【说明】",
        r"^【出处】",
        r"^【来源】",
        r"^【参考】",
        r"^【资料】",
        r"^【页码】",
        r"^【提示】",
        r"^【补充】",
        r"^【拓展】",
        r"^【教材】",
        r"^【链接】",
    ]
    if any(re.match(p, line) for p in explicit_patterns):
        return True

    # 更通用：短标签型的【xxx】说明行
    # 避免把【答案】吞掉，因为【答案】要参与解析
    if re.match(r"^【(?!答案】)[^】]{1,10}】", line):
        return True

    return False


def looks_like_question_start(line: str) -> bool:
    line = line.strip()
    if not line:
        return False

    patterns = [
        r"^\d+\s*[\.、)]\s*.+",
        r"^[（(]\s*\d+\s*[）)]\s*.+",
        r"^【\s*\d+\s*】\s*.+",
    ]
    return any(re.match(p, line) for p in patterns)


def is_option_line(line: str) -> bool:
    return bool(re.match(r"^\s*[A-E]\s*[\.．、)]\s*.+", line, flags=re.I))


def parse_option_line(line: str):
    m = re.match(r"^\s*([A-E])\s*[\.．、)]\s*(.+?)\s*$", line, flags=re.I)
    if not m:
        return None
    return m.group(1).upper(), normalize_spaces(m.group(2))


def is_answer_line(line: str) -> bool:
    return bool(re.match(
        r"^\s*(正确答案|参考答案|答案|【答案】|Answer)\s*[:：]?\s*.*$",
        line,
        flags=re.I
    ))


# =========================
# 答案处理
# =========================

def normalize_correct_letters(raw: str) -> str:
    raw = (raw or "").upper().strip()

    raw = re.sub(
        r"(正确答案|参考答案|答案|【答案】|ANSWER|ANSWER\s*KEY)\s*[:：]?\s*",
        "",
        raw,
        flags=re.I
    )

    raw = raw.replace("（", "(").replace("）", ")")
    raw = raw.strip("()")
    raw = raw.replace("，", ",").replace("、", ",").replace("；", ",")
    raw = raw.replace(" ", "")

    # 只保留 A-E 和逗号
    raw = re.sub(r"[^A-E,]", "", raw)

    if not raw:
        return ""

    # AC / ABD / ABCDE -> A,C / A,B,D / A,B,C,D,E
    if "," not in raw:
        letters = re.findall(r"[A-E]", raw)
        seen = []
        for ch in letters:
            if ch not in seen:
                seen.append(ch)
        return ",".join(seen)

    parts = [x for x in raw.split(",") if x]
    seen = []
    for p in parts:
        if re.fullmatch(r"[A-E]", p) and p not in seen:
            seen.append(p)
    return ",".join(seen)


def count_correct_letters(correct: str) -> int:
    if not correct:
        return 0
    return len([x for x in correct.split(",") if x])


def parse_answer_line(line: str) -> str:
    return normalize_correct_letters(line)


def extract_embedded_answer_anywhere(stem: str):
    """
    从题干任意位置提取括号中的答案字母，并保留空括号。
    例如：
    设计师对于（BE）日常生活设计策略层
    -> 设计师对于（）日常生活设计策略层, B,E
    """
    if not stem:
        return stem, ""

    collected = []

    def repl(match):
        left = match.group(1)
        letters = match.group(2)
        right = match.group(3)

        normalized = normalize_correct_letters(letters)
        if normalized:
            for x in normalized.split(","):
                if x and x not in collected:
                    collected.append(x)

        # 保留括号，清空里面内容
        return f"{left}{right}"

    # 只匹配括号中纯 A-E 组合的情况，避免误伤普通括号说明
    pattern = re.compile(r"([（(])\s*([A-E]{1,5})\s*([）)])", flags=re.I)
    new_stem = pattern.sub(repl, stem)

    new_stem = re.sub(r"\s+", " ", new_stem).strip()
    return new_stem, ",".join(collected)


def extract_embedded_answer_from_stem(stem: str):
    """
    1. 提取题干任意位置括号中的答案，如（AB）、(C)
    2. 再处理题干末尾裸露答案，如 ' xxx AC'
    返回：
    (清洗后的stem, CorrectLetters)
    """
    original = stem.strip()

    # 第一步：提取任意位置括号答案，并保留空括号
    stem_after_brackets, bracket_correct = extract_embedded_answer_anywhere(original)

    # 第二步：处理末尾裸露答案，如 "xxx AC"
    tmp = remove_trailing_punctuation(stem_after_brackets)

    tail_correct = ""
    m = re.match(r"^(.*?)\s+([A-E]{1,5})\s*$", tmp, flags=re.I)
    if m:
        prefix = m.group(1).strip()
        ans = normalize_correct_letters(m.group(2))
        if prefix and ans:
            stem_after_brackets = prefix
            tail_correct = ans

    # 合并答案，去重保序
    merged = []
    for source in [bracket_correct, tail_correct]:
        if source:
            for ch in source.split(","):
                if ch and ch not in merged:
                    merged.append(ch)

    return stem_after_brackets.strip(), ",".join(merged)


# =========================
# 文本标准化，防重复
# =========================

def standardize_stem(stem: str) -> str:
    stem = strip_question_number(stem)
    stem = normalize_spaces(stem)

    # 去掉题干内嵌答案，但保留空括号
    stem, _ = extract_embedded_answer_from_stem(stem)

    # 去掉尾部“答案/解析”残留
    stem = re.sub(
        r"(正确答案|参考答案|答案|解析|【答案】)\s*[:：]?\s*$",
        "",
        stem,
        flags=re.I
    )

    stem = normalize_spaces(stem)
    stem = remove_trailing_punctuation(stem)
    return stem


# =========================
# 断行合并
# =========================

def join_wrapped_lines(lines: list[str]) -> list[str]:
    """
    把被硬换行切碎的题干/解析尽量拼回去。
    遇到：
    - 新题开始
    - 选项
    - 答案
    - 注释行
    时切开。
    """
    merged = []
    buffer = ""

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            if buffer:
                merged.append(buffer.strip())
                buffer = ""
            continue

        if not buffer:
            buffer = line
            continue

        if (
            looks_like_question_start(line)
            or is_option_line(line)
            or is_answer_line(line)
            or is_comment_line(line)
        ):
            merged.append(buffer.strip())
            buffer = line
        else:
            buffer += " " + line.strip()

    if buffer:
        merged.append(buffer.strip())

    return merged


# =========================
# 拆题
# =========================

def split_into_question_blocks(text: str) -> list[list[str]]:
    text = normalize_newlines(text)
    raw_lines = [x for x in text.split("\n")]
    raw_lines = [x for x in raw_lines if x.strip()]
    lines = join_wrapped_lines(raw_lines)

    blocks = []
    current = []

    for line in lines:
        if looks_like_question_start(line):
            if current:
                blocks.append(current)
            current = [line]
        else:
            if not current:
                current = [line]
            else:
                current.append(line)

    if current:
        blocks.append(current)

    return blocks


# =========================
# 行内挤压题解析
# =========================

def parse_inline_options(text: str) -> dict:
    """
    处理这种：
    1. xxx A. aa B. bb C. cc D. dd 答案：B
    """
    normalized = text

    # 统一选项前缀为换行
    normalized = re.sub(r"\s*([A-E])\s*[\.．、)]\s*", r"\n\1. ", normalized)

    # 统一答案前缀为换行
    normalized = re.sub(
        r"\s*(正确答案|参考答案|答案|【答案】|Answer)\s*[:：]?\s*",
        r"\n答案：",
        normalized,
        flags=re.I
    )

    # 去掉注释行
    lines = []
    for x in normalized.split("\n"):
        x = x.strip()
        if not x:
            continue
        if is_comment_line(x):
            continue
        lines.append(x)

    options = {}
    answer = ""
    stem_parts = []

    for line in lines:
        if is_option_line(line):
            parsed = parse_option_line(line)
            if parsed:
                options[parsed[0]] = parsed[1]
        elif is_answer_line(line):
            answer = parse_answer_line(line)
        else:
            stem_parts.append(line)

    return {
        "stem": normalize_spaces(" ".join(stem_parts)),
        "options": options,
        "correct": answer
    }


# =========================
# 单题解析
# =========================

def parse_question_block(block: list[str]) -> dict:
    result = {
        "Stem": "",
        "A": "",
        "B": "",
        "C": "",
        "D": "",
        "E": "",
        "CorrectLetters": "",
        "Answer": "",
        "Type": "",
        "Tags": ""
    }

    stem_lines = []
    options = {}
    correct = ""
    answer_lines = []

    joined_text = " ".join(block).strip()

    for line in block:
        line = line.strip()
        if not line:
            continue

        # 忽略注释/出处/来源等
        if is_comment_line(line):
            continue

        if is_option_line(line):
            parsed = parse_option_line(line)
            if parsed:
                options[parsed[0]] = parsed[1]
            continue

        if is_answer_line(line):
            parsed_answer = parse_answer_line(line)
            if parsed_answer:
                correct = parsed_answer
            else:
                # 主观题答案
                plain = re.sub(
                    r"^\s*(正确答案|参考答案|答案|【答案】|Answer)\s*[:：]?\s*",
                    "",
                    line,
                    flags=re.I
                ).strip()
                if plain and not is_comment_line(plain):
                    answer_lines.append(plain)
            continue

        if not options and not stem_lines:
            stem_lines.append(line)
        elif not options:
            stem_lines.append(line)
        else:
            if not is_comment_line(line):
                answer_lines.append(line)

    # 如果没正常拆出来，尝试整块 inline 解析
    if not stem_lines and not options:
        inline = parse_inline_options(joined_text)
        stem_lines = [inline["stem"]] if inline["stem"] else []
        options = inline["options"]
        correct = inline["correct"]

    stem = normalize_spaces(" ".join(stem_lines))
    stem = strip_question_number(stem)

    # 题干嵌入答案
    stem, embedded_correct = extract_embedded_answer_from_stem(stem)
    if embedded_correct:
        if not correct or correct in {"A,B,C,D,E", "A,B,C,D"}:
            correct = embedded_correct
        else:
            merged = []
            for source in [correct, embedded_correct]:
                for ch in normalize_correct_letters(source).split(","):
                    if ch and ch not in merged:
                        merged.append(ch)
            correct = ",".join(merged)

    correct = normalize_correct_letters(correct)

    # 仍没有选项的话，再从整块文本强行抽一次
    if not options:
        inline = parse_inline_options(joined_text)
        if inline["options"]:
            options = inline["options"]
            if not stem and inline["stem"]:
                stem = strip_question_number(inline["stem"])
                stem, embedded2 = extract_embedded_answer_from_stem(stem)
                if embedded2 and not correct:
                    correct = embedded2
            if inline["correct"] and not correct:
                correct = inline["correct"]

    # 写入结果
    if options:
        for letter in ["A", "B", "C", "D", "E"]:
            result[letter] = options.get(letter, "")

        result["Stem"] = standardize_stem(stem)
        result["CorrectLetters"] = correct

        n = count_correct_letters(correct)
        result["Type"] = "single" if n <= 1 else "multiple"
        result["Answer"] = ""
    else:
        # 非选择题
        stem_text = stem if stem else strip_question_number(joined_text)
        stem_text = standardize_stem(stem_text)

        answer_text = normalize_spaces(" ".join(answer_lines))
        if is_comment_line(answer_text):
            answer_text = ""

        result["Stem"] = stem_text
        result["CorrectLetters"] = ""
        result["Answer"] = answer_text
        result["Type"] = "text"

    # 再次修复一些异常
    if result["Type"] != "text":
        # CorrectLetters 异常
        if result["CorrectLetters"] in {"A,B,C,D,E", "A,B,C,D"}:
            fixed_stem, embedded3 = extract_embedded_answer_from_stem(result["Stem"])
            if embedded3:
                result["Stem"] = standardize_stem(fixed_stem)
                result["CorrectLetters"] = embedded3

        # 单选/多选自动纠正
        if count_correct_letters(result["CorrectLetters"]) > 1:
            result["Type"] = "multiple"
        elif count_correct_letters(result["CorrectLetters"]) == 1:
            result["Type"] = "single"

    return result


# =========================
# 去重
# =========================

def count_nonempty_options(row: dict) -> int:
    return sum(1 for k in ["A", "B", "C", "D", "E"] if (row.get(k) or "").strip())


def row_score(row: dict) -> tuple:
    option_count = count_nonempty_options(row)
    correct_count = count_correct_letters(row.get("CorrectLetters", ""))
    answer_len = len((row.get("Answer") or "").strip())
    type_score = {"text": 0, "single": 1, "multiple": 2}.get(row.get("Type", ""), 0)
    return (option_count, correct_count, answer_len, type_score)


def deduplicate_rows(rows: list[dict]) -> list[dict]:
    dedup = OrderedDict()

    for row in rows:
        key = standardize_stem(row["Stem"])
        if not key:
            continue

        row["Stem"] = key

        if key in dedup:
            if row_score(row) >= row_score(dedup[key]):
                dedup[key] = row
        else:
            dedup[key] = row

    return list(dedup.values())


# =========================
# 主流程
# =========================

def parse_txt_to_anki_csv(input_txt: str, output_csv: str) -> None:
    text = Path(input_txt).read_text(encoding="utf-8", errors="ignore")
    text = normalize_newlines(text)

    blocks = split_into_question_blocks(text)

    rows = []
    for block in blocks:
        row = parse_question_block(block)
        if not row["Stem"]:
            continue

        # 如果被误判成 text，但整块明显有选项，再修一次
        if row["Type"] == "text":
            joined = " ".join(block)
            if re.search(r"[A-E]\s*[\.．、)]", joined):
                inline = parse_inline_options(joined)
                if inline["options"]:
                    repaired_stem = standardize_stem(strip_question_number(inline["stem"] or row["Stem"]))
                    repaired_correct = normalize_correct_letters(inline["correct"])

                    row = {
                        "Stem": repaired_stem,
                        "A": inline["options"].get("A", ""),
                        "B": inline["options"].get("B", ""),
                        "C": inline["options"].get("C", ""),
                        "D": inline["options"].get("D", ""),
                        "E": inline["options"].get("E", ""),
                        "CorrectLetters": repaired_correct,
                        "Answer": "",
                        "Type": "single",
                        "Tags": ""
                    }
                    if count_correct_letters(repaired_correct) > 1:
                        row["Type"] = "multiple"

        rows.append(row)

    rows = deduplicate_rows(rows)

    # 重排标签
    for i, row in enumerate(rows, start=1):
        row["Tags"] = f"Q{i}"

    with open(output_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Parsed {len(rows)} questions.")
    print(f"Output: {output_csv}")


if __name__ == "__main__":
    parse_txt_to_anki_csv(INPUT_TXT, OUTPUT_CSV)
