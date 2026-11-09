# -*- coding: utf-8 -*-
"""把课程数据注入模板，生成可直接双击打开的 题库.html

用法:
    python src/build.py                     # 用 data/course.sample.json
    python src/build.py data/my-course.json # 用你自己的题库
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "题库.html")


def die(msg):
    sys.stdout.write("构建失败: " + msg + "\n")
    sys.exit(1)


def check(cfg):
    meta = cfg.get("meta") or {}
    qs = cfg.get("questions") or []
    for k in ("course", "chapters", "kinds", "sources"):
        if not meta.get(k):
            die("meta 缺少字段 " + k)
    if not qs:
        die("questions 为空")

    ch_ids = set(str(c["id"]) for c in meta["chapters"])
    kind_labels = set(k["label"] for k in meta["kinds"])
    kinds_by_label = {k["label"]: k["key"] for k in meta["kinds"]}
    src_keys = set(s["key"] for s in meta["sources"])

    seen = set()
    for i, q in enumerate(qs, 1):
        tag = "第 %d 题" % i
        for f in ("id", "ch", "kind", "q", "opts", "ans"):
            if f not in q:
                die(tag + " 缺少字段 " + f)
        if q["id"] in seen:
            die(tag + " id 重复: " + str(q["id"]))
        seen.add(q["id"])
        if str(q["ch"]) not in ch_ids:
            die(tag + " 章节 " + str(q["ch"]) + " 不在 meta.chapters 里")
        if q["kind"] not in kind_labels:
            die(tag + " 题型 " + q["kind"] + " 不在 meta.kinds 里")
        if q.get("src") and q["src"] not in src_keys:
            die(tag + " 来源 " + q["src"] + " 不在 meta.sources 里")
        opts = q["opts"]
        if not (2 <= len(opts) <= 8):
            die(tag + " 选项数应为 2-8，实际 " + str(len(opts)))
        keys = [o[0] for o in opts]
        if len(set(keys)) != len(keys):
            die(tag + " 选项 key 重复")
        for a in q["ans"]:
            if a not in keys:
                die(tag + " 答案 " + a + " 不在选项里")
        if not q["ans"]:
            die(tag + " 没有答案")
    return meta, qs


def main():
    rel = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "course.sample.json")
    path = rel if os.path.isabs(rel) else os.path.join(ROOT, rel)
    if not os.path.exists(path):
        die("找不到数据文件 " + path)

    cfg = json.load(io.open(path, encoding="utf-8"))
    meta, qs = check(cfg)

    tpl = io.open(os.path.join(ROOT, "src", "template.html"), encoding="utf-8").read()
    html = (tpl.replace("__META__", json.dumps(meta, ensure_ascii=False))
               .replace("__QUESTIONS__", json.dumps(qs, ensure_ascii=False))
               .replace("__COURSE__", meta["course"]))
    io.open(OUT, "w", encoding="utf-8").write(html)
    sys.stdout.write("已生成 %s\n" % OUT)
    sys.stdout.write("  课程: %s | 题数: %d | 章节: %d\n" % (meta["course"], len(qs), len(meta["chapters"])))


if __name__ == "__main__":
    main()
