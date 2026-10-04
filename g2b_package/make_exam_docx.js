// G2B exam pages -> DOCX (real tables, send-friendly; mirrors 考页.md/学习页.md,
// item 14 = ●1◆ per the registered answer key). Run: node make_exam_docx.js
// NOTE: column widths are set PER CELL as percentages (Word-compatible);
// the table-level width alone is not enough and WPS-only tolerance masked it.
const docx = require("../human_package/node_modules/docx");
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, BorderStyle, HeadingLevel, PageBreak } = docx;

const FONT = "SimSun";
const HEI = "SimHei";
const LN = { line: 312 };

function txt(t, o = {}) { return new TextRun({ text: t, font: { name: FONT }, size: 24, ...o }); }
function bd(t, o = {}) { return txt(t, { bold: true, ...o }); }
function p(kids, o = {}) { return new Paragraph({ spacing: LN, ...o, children: kids }); }
function h1(t) { return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { ...LN, before: 240, after: 120 }, children: [new TextRun({ text: t, font: { name: HEI }, bold: true, size: 32 })] }); }
function h2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { ...LN, before: 200, after: 100 }, children: [new TextRun({ text: t, font: { name: HEI }, bold: true, size: 28 })] }); }
function blank() { return new Paragraph({ spacing: LN, children: [] }); }

const MARGINS = { top: 60, bottom: 60, left: 120, right: 120 };
function td(t, wpct, center) {
  return new TableCell({
    margins: MARGINS,
    ...(wpct ? { width: { size: wpct, type: WidthType.PERCENTAGE } } : {}),
    children: [p([txt(t)], center ? { alignment: AlignmentType.CENTER } : {})],
  });
}
function table(rows) {
  return new Table({ width: { size: 100, type: WidthType.PERCENTAGE },
    margins: MARGINS, rows });
}

// ---------- 学习页 ----------
const study = [];
study.push(h1(`星语 · 学习页`));
study.push(p([txt(`外星球"星语"里，名词有单数和复数两种形式。下面 16 个单词展示了单数→复数的变化。`)]));
study.push(h2(`你的任务`));
study.push(p([txt(`通过这 16 个例子，弄懂星语名词变复数的方法。学完之后你要用同样的方法处理没见过的新单词。`)]));
study.push(h2(`学习方式`));
[`拿一张纸（或用手）遮住表格的右列，从上往下一行一行猜：这个词的复数是什么？`,
 `猜完一个，挪开遮住的东西对一下答案。对了他自己知道，错了就改过来；`,
 `可以反复过这 16 个词，直到你觉得自己摸到了门道；`,
 `时间最多 25 分钟，学会后就可以开始考试（考页另发）。`].forEach((t, i) =>
  study.push(p([txt(`${i + 1}. ${t}`)])));
study.push(h2(`例子（16 个）`));
const TRAIN = [["bab","babum"],["kad","kadum"],["pag","pagum"],["dab","dabum"],
  ["big","bigis"],["pid","pidis"],["gub","gubis"],["bud","budis"],
  ["kap","kapis"],["tap","tapis"],["bap","bapis"],["pak","pakis"],
  ["buk","bukok"],["dup","dupok"],["dik","dikok"],["tup","tupok"]];
study.push(table([
  new TableRow({ children: [td(`单数`, 50, 1), td(`复数`, 50, 1)] }),
  ...TRAIN.map(([s, pl]) => new TableRow({ children: [td(s, 50, 1), td(pl, 50, 1)] })),
]));
study.push(blank());
study.push(h2(`说明`));
study.push(p([txt(`星语的字母表只有这 9 个字母：b d g k p t a i u。所有单词（包括考试里的）都只用这些字母。`)]));
study.push(p([txt(`考试时没有反馈，也没有新的例子。祝顺利。`)]));

// ---------- 考页 ----------
const exam = [];
exam.push(h1(`星语 · 考页`));
exam.push(p([txt(`考试分两部分。答题前请不要翻学习页。把答案直接填在表格里；把握程度在两项中圈一项。`)]));
exam.push(h2(`第一部分（12 题）`));
exam.push(p([txt(`写出每个词的复数，并标注你的把握程度：`), bd(`有把握`), txt(` / `), bd(`在猜`), txt(`。`)]));
const EX1 = ["bad","gad","pad","dig","pud","bid","bat","tak","dat","bik","dip","kit"];
exam.push(table([
  new TableRow({ children: [td(`题号`, 12, 1), td(`单数`, 22, 1),
    td(`复数（填写）`, 36, 1), td(`把握程度（圈一项）`, 30, 1)] }),
  ...EX1.map((s, i) => new TableRow({ children: [
    td(String(i + 1), 12, 1), td(s, 22, 1), td(``, 36), td(`有把握 / 在猜`, 30, 1),
  ] })),
]));
exam.push(blank());
exam.push(p([bd(`第 13 题（文字题）`), txt(`：用一两句话回答——你刚才用的方法在什么情况下可能失灵？它适用的范围是什么？`)]));
exam.push(p([txt(`答：_______________________________________________`)]));
exam.push(p([txt(`_______________________________________________________________`)]));
exam.push(blank());
exam.push(new Paragraph({ children: [new PageBreak()] }));  // keep the cipher legend table on one page
exam.push(h2(`第二部分（8 题）`));
exam.push(p([txt(`星语还有一种"符号写法"。密码表如下（考试期间可以随时查看）：`)]));
const LEG = [["b","◆","k","▲","a","1"],["d","★","p","■","i","2"],["g","●","t","▼","u","3"]];
exam.push(table([
  new TableRow({ children: [td(`字母`, 17, 1), td(`符号`, 16, 1), td(`字母`, 17, 1),
    td(`符号`, 16, 1), td(`字母`, 17, 1), td(`符号`, 17, 1)] }),
  ...LEG.map(r => new TableRow({ children: r.map((x, i) => td(x, i % 2 ? 16 : 17, 1)) })),
]));
exam.push(blank());
exam.push(p([txt(`下面 8 个词是符号写法的新词。判断它们按照第一部分的方法该加哪个后缀，在表格里写下 `),
  bd(`um / is / ok`), txt(` 三者之一。`)]));
const EX2 = ["●1◆","★1■","▲3★","●2★","■1▼","★1●","■2▲","◆2▼"];
exam.push(table([
  new TableRow({ children: [td(`题号`, 12, 1), td(`单数（符号）`, 44, 1),
    td(`后缀（um/is/ok）`, 44, 1)] }),
  ...EX2.map((s, i) => new TableRow({ children: [
    td(String(i + 14), 12, 1), td(s, 44, 1), td(``, 44),
  ] })),
]));

function build(kids) {
  return new Document({ sections: [{ properties: {}, children: kids }] });
}
Promise.all([
  Packer.toBuffer(build(study)).then(b => fs.writeFileSync(`学习页.docx`, b)),
  Packer.toBuffer(build(exam)).then(b => fs.writeFileSync(`考页.docx`, b)),
]).then(() => console.log("written: 学习页.docx, 考页.docx"));
