const docx = require("docx");
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  WidthType, AlignmentType, BorderStyle, HeadingLevel, PageBreak
} = docx;

const FONT = "SimSun";
const HEI = "SimHei";
const LN = { line: 312 };

function txt(t, o = {}) { return new TextRun({ text: t, font: { name: FONT }, size: 24, ...o }); }
function bd(t, o = {}) { return txt(t, { bold: true, ...o }); }
function p(kids, o = {}) { return new Paragraph({ spacing: LN, ...o, children: kids }); }
function h1(t) { return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { ...LN, before: 240, after: 120 }, children: [new TextRun({ text: t, font: { name: HEI }, bold: true, size: 32 })] }); }
function h2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { ...LN, before: 200, after: 100 }, children: [new TextRun({ text: t, font: { name: HEI }, bold: true, size: 28 })] }); }
function blank() { return new Paragraph({ spacing: LN, children: [] }); }

const BT = { style: BorderStyle.SINGLE, size: 1, color: "888888" };
const TO = { width: { size: 100, type: WidthType.PERCENTAGE }, margins: { top: 60, bottom: 60, left: 120, right: 120 } };
function td(t) { return new TableCell({ ...TO, children: [p([txt(t)])] }); }

const kids = [];

kids.push(h1(`直觉机制 · 人类被试实验`));
kids.push(p([txt(`时间：约 20 分钟　　要求：按顺序作答，不要跳题`, { italics: true, color: "666666" })]), blank());

// Part 1
kids.push(h2(`第一题：找规律`));
kids.push(p([txt(`下面表中，有些编号的结果是一个整数，有些不是。`)], { indent: { firstLine: 480 } }));
kids.push(new Table({ ...TO, rows: [
  new TableRow({ children: [td(`编号`), td(`结果`)] }),
  ...[[`1`,`8`],[`3`,`12`],[`5`,`20`],[`7`,`32`],[`13`,`104`],[`17`,`200`]].map(([a,b]) => new TableRow({ children: [td(a), td(b)] })),
] }));
kids.push(blank());
kids.push(p([bd(`第 1 题`), txt(`：你发现什么规律了吗？用自己的话写下来。`)], { indent: { firstLine: 480 } }));
kids.push(p([txt(`答：_______________________________________________`)], { indent: { firstLine: 480 } }));
kids.push(p([bd(`第 2 题`), txt(`：你有没有把握？为什么？`)], { indent: { firstLine: 480 } }));
kids.push(p([txt(`答：_______________________________________________`)], { indent: { firstLine: 480 } }));
kids.push(blank());

kids.push(p([txt(`下面是另一组数据的判定结果：`)], { indent: { firstLine: 480 } }));
kids.push(new Table({ ...TO, rows: [
  new TableRow({ children: [td(`编号`), td(`判定`)] }),
  ...[[`4`,`整数`],[`8`,`整数`],[`12`,`不是整数`],[`20`,`不是整数`],[`140`,`不是整数`],[`220`,`不是整数`]].map(([a,b]) => new TableRow({ children: [td(a), td(b)] })),
] }));
kids.push(blank());
kids.push(p([bd(`第 3 题`), txt(`：根据这组新数据，你之前发现的规律还成立吗？`)], { indent: { firstLine: 480 } }));
kids.push(p([txt(`□ 成立　　□ 不成立　　□ 不确定`)], { indent: { firstLine: 480 } }));
kids.push(p([bd(`第 4 题`), txt(`：预测以下新行的判定（同族数据）：`)], { indent: { firstLine: 480 } }));
[[`52`],[`68`],[`308`],[`9`],[`18`],[`27`],[`45`],[`63`]].forEach(([d]) => {
  kids.push(p([txt(`${d}: ______________`)], { indent: { left: 480 } }));
});
kids.push(new Paragraph({ children: [new PageBreak()] }));

// Part 2
kids.push(h2(`第二题：看数据猜类别`));
kids.push(p([txt(`下面 8 个数对来自特殊的和普通的两类对象。但你不知道哪些是哪些。`)], { indent: { firstLine: 480 } }));
kids.push(new Table({ ...TO, rows: [
  new TableRow({ children: [td(`序号`), td(`第一个数`), td(`第二个数`)] }),
  ...[[`1`,`0.005`,`0.181`],[`2`,`0.010`,`0.200`],[`3`,`0.031`,`0.238`],[`4`,`0.050`,`0.250`],
      [`5`,`0.083`,`0.250`],[`6`,`0.125`,`-9.681`],[`7`,`0.017`,`0.218`],[`8`,`0.000`,`0.025`]]
    .map(([a,b,c]) => new TableRow({ children: [td(a), td(b), td(c)] })),
] }));
kids.push(blank());
kids.push(p([bd(`第 5 题`), txt(`：你觉得哪些序号的对象是特殊的？`)], { indent: { firstLine: 480 } }));
kids.push(p([txt(`答：_______________________________________________`)], { indent: { firstLine: 480 } }));
kids.push(p([bd(`第 6 题`), txt(`：你为什么这样判断？`)], { indent: { firstLine: 480 } }));
kids.push(p([txt(`答：_______________________________________________`)], { indent: { firstLine: 480 } }));
kids.push(p([bd(`第 7 题`), txt(`：如果让你再多看一个信息（比如每个对象原来对应的编号），你觉得会有帮助吗？为什么？`)], { indent: { firstLine: 480 } }));
kids.push(p([txt(`答：_______________________________________________`)], { indent: { firstLine: 480 } }));
kids.push(new Paragraph({ children: [new PageBreak()] }));

// Part 3
kids.push(h2(`第三题：检查自己`));
kids.push(p([bd(`第 8 题`), txt(`：回到第一题。假设另一个同学完全按照你在第一题里写的规律去判断一套全新的数据。你觉得他的结果和你的判断会一样吗？`)], { indent: { firstLine: 480 } }));
kids.push(p([txt(`□ 完全一样　　□ 大概差不多　　□ 可能会有出入`)], { indent: { firstLine: 480 } }));
kids.push(p([bd(`第 9 题`), txt(`：如果可能有出入，你觉得会是什么样的数据让他出错？`)], { indent: { firstLine: 480 } }));
kids.push(p([txt(`答：_______________________________________________`)], { indent: { firstLine: 480 } }));
kids.push(blank());
kids.push(p([txt(`（答完了，交给施测者）`, { italics: true, color: "999999" })], { alignment: AlignmentType.CENTER }));

// Document
const doc = new Document({
  styles: { default: { document: { run: { font: { name: FONT }, size: 24 } } } },
  sections: [{ properties: {}, children: kids }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("exam_cn.docx", buf);
  console.log("exam_cn.docx written");
});
