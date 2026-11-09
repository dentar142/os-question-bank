# 题目导入规范

数据文件是一个 JSON，包含 meta 与 questions 两部分。构建时 src/build.py 会做结构与内容校验，校验不过直接报错，不会生成半成品。

    {
      "meta": { ... },
      "questions": [ ... ]
    }

## 一、meta

| 字段 | 类型 | 说明 |
|---|---|---|
| course | string | 课程名，显示在标题与侧栏品牌 |
| subtitle | string | 副标题，显示在品牌下方 |
| dailyGoal | number | 侧栏「今日练习」的目标题数 |
| chapters | array | 章节列表，元素为 { id, name } |
| kinds | array | 题型定义，元素为 { key, label, short } |
| sources | array | 来源定义，元素为 { key, label } |

chapters 的 id 与题目里的 ch 对应，name 是显示名。题目里出现 meta 未声明的章节会被拒绝。

kinds 决定题型筛选与渲染方式。key 只影响内部比较，label 必须与题目的 kind 完全一致：

    { "key": "judge",  "label": "判断题", "short": "判断" }
    { "key": "single", "label": "单选题", "short": "单选" }
    { "key": "multi",  "label": "多选题", "short": "多选" }

sources 用于区分题目来源，例如真题与预测题：

    { "key": "real", "label": "真题" }
    { "key": "pred", "label": "预测" }

## 二、questions

每道题是一个对象：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| id | string | 是 | 全局唯一，进度按它记录，改动等于丢进度 |
| ch | number | 是 | 所属章节 id |
| kind | string | 是 | 题型标签，必须等于某个 meta.kinds 的 label |
| src | string | 否 | 来源 key，省略时按 real 处理 |
| q | string | 是 | 题干，英文（与考卷一致） |
| qzh | string | 否 | 题干中文译文，开启中英对照时显示 |
| opts | array | 是 | 选项数组，2-8 个 |
| ans | array | 是 | 正确选项的 key 数组，必须非空 |
| why | string | 否 | 解析，中文，20-80 字最佳 |

### 选项格式

每个选项是三元素数组：[key, 英文文本, 中文文本]

    [["A", "Physical layer", "物理层"],
     ["B", "Data link layer", "数据链路层"],
     ["C", "Network layer", "网络层"]]

- key 用大写字母 A 起，不能重复
- 中文文本留空字符串则不显示译文
- 判断题固定两个选项：A=是，B=非；中文与英文相同，页面上不会重复显示

### 答案规则

- ans 是数组，单选与判断长度为 1
- 判分用集合相等，顺序无关
- ans 里的 key 必须存在于 opts，否则构建失败

### 示例

    {
      "id": "s005",
      "ch": 2,
      "kind": "单选题",
      "src": "real",
      "q": "The binary number 1011 equals which decimal value?",
      "qzh": "二进制 1011 对应的十进制值是？",
      "opts": [["A", "9", "9"], ["B", "11", "11"], ["C", "13", "13"], ["D", "15", "15"]],
      "ans": ["B"],
      "why": "1×8 + 0×4 + 1×2 + 1×1 = 11。"
    }

## 三、从 Moodle 导出页转换

如果题库来自 Moodle 的「作答回顧」页面，实操路径如下。

第 1 步：在复习页保存 HTML，用脚本抽出题干、选项、正确答案与反馈。

Moodle 复习页的稳定选择器：

    .que                     一道题
    .que .qtext              题干
    .que .answer .r0/.r1     选项行，带 correct / incorrect 类名
    .que .rightanswer        形如：正確答案為"非"
    .que .info .state        答對 / 答錯
    .que .generalfeedback    教师反馈（有就拿来当解析）

第 2 步：把抽出的结构转成上面的 JSON。

要点：

- 题目顺序按页面顺序，但同一题可能在多页重复，用题干 + 选项做去重键
- 判断题的「是/非」直接映射成 A/B
- 解析优先用教师反馈，没有再用模型生成

第 3 步：跑构建，让校验器兜底。

    python src/build.py data/my-course.json

## 四、从 Markdown 题库转换

如果手上已经是 Markdown（每题一个小节、选项带勾选、答案另起一行），转换时注意：

- 答案不要取「答案：是」这类文字，直接取勾选标记对应的 key，避免中英文不一致
- 解析字段可能是 JSON 字符串（模型返回时常见的坑），先解析出 explanation / 解析 字段再写入 why
- 选项文本去掉开头的 a. / A. 前缀，key 单独存

## 五、构建期校验清单

build.py 会逐题检查，任何一条不过就中止：

1. 必填字段齐全
2. id 不重复
3. ch 在 meta.chapters 里
4. kind 在 meta.kinds 的 label 里
5. src 在 meta.sources 里
6. 选项数 2-8，key 不重复
7. 答案非空，且都能在选项里找到

## 六、常见坑

- 判断题若把答案写成「是/非」而不是 A/B，判分会失效
- 选项文本里的竖线不要紧，但题干里尽量避免连续竖线，聊天面板的表格解析会误判
- id 一旦发布就不要改，改了等于把用户进度清零
- 中文译文与英文完全相同时可以留空，页面会自动跳过，不要留着重复显示
