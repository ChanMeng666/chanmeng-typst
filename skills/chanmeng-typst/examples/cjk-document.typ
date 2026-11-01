// CJK (Chinese) document — compile with: typst compile cjk-document.typ
#set document(title: "中文文档示例", author: "作者")
#set page(paper: "a4", margin: 2.5cm)
// Each chain lists Adobe, Google, macOS and Windows fonts, so it works on any of
// them. Typst warns once for each name it cannot find. That is expected here, as
// long as `pdffonts` shows the fonts you meant to use.
// Many Chinese system fonts (SimSun, SimHei, KaiTi) have no bold or italic face,
// so *bold* would look like body text. Bold uses a sans font and italics use Kai.
#let cjk-serif = ("Source Han Serif SC", "Noto Serif CJK SC", "Songti SC", "SimSun")
#let cjk-sans = ("Source Han Sans SC", "Noto Sans CJK SC", "PingFang SC", "Microsoft YaHei")
#let cjk-kai = ("Kaiti SC", "KaiTi")
#set text(lang: "zh", region: "cn", font: cjk-serif, size: 11pt)
#set heading(numbering: "1.1")
// `all: true` also indents the first paragraph after a heading, as Chinese expects.
#set par(justify: true, leading: 1em, first-line-indent: (amount: 2em, all: true))
#show strong: set text(font: cjk-sans)
#show emph: set text(font: cjk-kai, style: "normal")
#show heading: set text(font: cjk-sans, weight: "bold")

= 文档标题

这是一个中文文档模板，展示了正确的中文排版设置。

== 字体说明

宋体和黑体等系统字体没有粗体和斜体字重，所以本模板把 *粗体* 映射到无衬线字体，把 _强调_ 映射到楷体。Typst 会对回退链里没装上的字体名各发一条 `unknown font family` 提示，只要用 `pdffonts` 确认实际用到的字体符合预期即可。

中文段落请写在同一行源码里，因为源码换行会在两个汉字之间留下一个可见的空格。

== 数学公式

欧拉公式：$ e^(i pi) + 1 = 0 $

== 列表

- 第一项
- 第二项
  - 嵌套项

+ 编号一
+ 编号二
