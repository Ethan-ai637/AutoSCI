# AutoSCI

**面向科研绘图、组会汇报与科研表达工作的开源 Codex Skills。**

> **把时间留给科研本身，而不是消耗在画图、排版和反复改 PPT 上。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Scientific Figure](https://img.shields.io/badge/Scientific%20Figure-v2.0%20stable-2ea44f)](skills/scientific-figure)
[![Research Presentation](https://img.shields.io/badge/Research%20Presentation-v3-blue)](skills/academic-research-presentation)

[English](README.md) · **中文**

## 为什么做 AutoSCI？

科研人的时间很宝贵，但现实中仍然有大量时间消耗在一些**重要、必须做，却高度重复和繁琐**的工作上：画方法框架图、调箭头和文字、重画论文示意图、从 PDF 里截 Figure、检查 legend 和坐标轴、排组会 PPT、对齐元素、修改字号，以及在汇报前一晚反复调整页面。

这些工作并非不重要。恰恰因为**科研表达本身很重要**，我们才希望把其中机械、重复、可以流程化的部分交给更可靠的工具，而不是让它持续占用研究者最宝贵的注意力。

**AutoSCI 希望做的事情很简单：用一组开源、可复用、可修改的 Codex Skills，帮助大家处理科研表达中的繁琐生产工作。**

我们并不希望 AI 替代科研思考，更不希望它替研究者做科学判断。我们希望它承担的是另一部分工作——让研究者能够把更多精力放回真正重要的事情：

- 提出更好的问题；
- 构思和推翻新的想法；
- 设计更扎实的实验；
- 理解意料之外的结果；
- 和合作者讨论科学问题；
- 思考怎样更准确、更有创造力地表达自己的工作。

而不是把同样的时间花在移动两个像素的文本框、重画已经想清楚的方法流程、修一条方向错误的箭头，或者为了第二天的组会重新排十几页 PPT。

**我们希望工具降低科研表达的机械成本，让科研想象力不再受限于“会不会画图”“有没有时间做 PPT”这些事情。**

## AutoSCI 是什么？

AutoSCI 不是新的基础模型，也不是某个在线 API 的套壳。它是一组面向本地 Codex 的**科研工作流 Skills**：把科研语义约束、结构化中间产物、参考资料、可执行 QA、render/critique/refine 闭环和开源脚本组织起来，让 Codex 在完成科研生产任务时更加可靠。

目前包含两个彼此独立、又可以组合使用的 Skill：

| Skill | 能帮你做什么 | 主要产物 |
| --- | --- | --- |
| [`scientific-figure`](skills/scientific-figure) | 方法总览、模型架构、机制图、pipeline、taxonomy、多面板概念图 | 可编辑、可追踪 SVG；可选 PDF/PNG release 包 |
| [`academic-research-presentation`](skills/academic-research-presentation) | 论文汇报、组会、科研进展、technical talk | 面向 PPTX/Slides 工具链的 evidence-first 科研汇报工作流 |

两个 Skill 可以单独安装，也可以组合使用：

```text
                      论文 / 项目 / 科研想法
                              │
               ┌──────────────┴──────────────┐
               │                             │
               ▼                             ▼
      $scientific-figure        $academic-research-presentation
               │                             │
        方法 / 机制 / 架构              论文汇报 / 组会
        pipeline / overview             科研进展 / technical talk
               │                             │
               ▼                             ▼
         可编辑科研 Figure                 科研汇报
               │                             ▲
               └──────────────┬──────────────┘
                              │
                            科研表达
```

## 我们坚持什么？

AI 可以把一张图、一页 PPT 做得很漂亮，同时把科学内容画错。因此 AutoSCI 不把科研材料当成普通的平面设计任务。

两个 Skill 共享一些基本原则：

- **科学正确性优先于美观；**
- **证据优先于装饰性流程图；**
- **结构优先于坐标；**
- **Figure / Table / Equation / Result 优先于通用卡片式排版；**
- **能保留可编辑源文件，就尽量不只留下截图；**
- **先 render、再检查，而不是生成完成就默认正确；**
- **能够确定性检查的问题尽量交给脚本，而不是完全依赖模型自评；**
- **自动化应该减少重复劳动，而不是拿走研究者的控制权。**

AutoSCI 追求的不是“一键科研”，而是更合理的人机分工：

```text
研究者
├── 科学问题
├── 假设与判断
├── 方法与实验
├── 结果解释
└── 最终科研决策

AutoSCI + Codex
├── 科研图构建
├── 重复性排版
├── 汇报页面生产
├── 论文视觉素材处理
├── 确定性 QA
└── 迭代式表达优化
```

## Scientific Figure — v2.0 Stable

`scientific-figure` 是一个 structure-first 的科研绘图工作流，用来创建和重构可编辑科研 Figure，同时尽量保护原始科研语义不被视觉优化过程偷偷改变。

```text
论文 / Method / equation / code
              ↓
      source-grounded spec
              ↓
        semantic freeze
              ↓
     scientific visual grammar
              ↓
       traceable SVG master
              ↓
 deterministic QA + render
              ↓
 semantic critic + visual critic
              ↓
       targeted refinement
              ↓
       SVG / PDF / PNG
```

主要能力包括：

- source-grounded claims / entities / relations / notation / invariants；
- semantic lock，避免后续美化过程中悄悄改变 Method；
- Spec ↔ SVG traceability；
- 专门面向科研图的 visual patterns，减少典型 AI “框框 + 箭头”式 box soup；
- geometry、relation endpoint、notation、最终物理字号、portability 和 release audit；
- `draft / standard / release` 三种执行强度；
- checkpoint/resume，方便较长工作流中断后继续；
- 可选 blind benchmark、regression suite 与 ablation 工具；
- 不要求额外再接一个图像生成或 LLM API，本地 Codex 可以承担 planning、SVG generation 与 critique。

对于折线图、柱状图、热图等定量实验图，Skill 明确优先使用真实数据 + plotting code，而不是让生成模型“画出一条看起来合理的曲线”。

详细说明见 [`skills/scientific-figure/README.md`](skills/scientific-figure/README.md) 和 [`STABILITY.md`](skills/scientific-figure/STABILITY.md)。

## Academic Research Presentation — V3

`academic-research-presentation` 面向研究者真正经常遇到的场景：论文汇报、实验室组会、科研进展汇报、proposal discussion 和 technical talk。

它首先关心的是科研内容，而不是套一个通用的“漂亮 PPT 模板”：

```text
scientific fidelity
      ↓
source visual integrity
      ↓
figures / tables / equations
      ↓
technical mechanism
      ↓
narrative and visual polish
```

V3 重点处理自动做 PPT 时最常见的两个高风险问题：

1. AI 自己脑补、或者箭头方向错误的流程图；
2. 从论文里截取不完整、被污染的 Figure/Table。

核心约束包括：

- evidence before custom diagrams；
- 有向机制图先建立显式 node/edge spec；
- render 后再检查真正的箭头方向；
- 检查 axes、ticks、legend、panel label 和完整科学内容；
- 默认一页一个 hero scientific visual；
- canvas-first，而不是 box/card-first；
- 不为了满足页数而裁掉重要科学含义；
- 论文汇报、组会进展、technical talk 使用不同的 reasoning mode。

它是一个**科研汇报 reasoning / QA Skill**，不是独立的 PPTX 渲染器，需要配合 Codex 环境中的 slides/PPTX 工具链使用。

详细说明见 [`skills/academic-research-presentation/README.md`](skills/academic-research-presentation/README.md)。

## 快速开始

克隆仓库：

```bash
git clone https://github.com/Ethan-ai637/AutoSCI.git
cd AutoSCI
```

将需要的 Skill 复制到 Codex skills 目录。常见位置是 `$CODEX_HOME/skills/`；如果没有设置 `CODEX_HOME`，很多本地环境使用 `~/.codex/skills/`。

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/scientific-figure "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/academic-research-presentation "${CODEX_HOME:-$HOME/.codex}/skills/"
```

重新加载 Codex 后，可以直接调用：

```text
Use $scientific-figure to turn the Method section of paper.pdf into an editable Figure 1.
Use standard mode, preserve the mathematical notation, and deliver SVG + target-size PNG.
```

或者：

```text
Use $academic-research-presentation to build a 15-slide paper-reading presentation from paper.pdf.
Prioritize the paper's main figures and tables, and explain the evidence instead of filling slides with generic cards.
```

Windows 与更完整的安装说明见 [`docs/installation.md`](docs/installation.md)。

## 适合谁？

AutoSCI 面向研究生、科研人员、工程师，以及所有经常需要把技术工作整理成 Figure 和 Slides 的人。你不需要接受整套工作流：两个 Skill 都是自包含的，里面的 references 和 scripts 也可以单独修改、复用。

如果你经常有这些想法，它可能正适合你：

- “方法我已经想清楚了，但我不想再花一晚上重画 Figure 1。”
- “明天要组会汇报这篇论文，现在还没开始做 PPT。”
- “这一页最重要的明明是实验主图，为什么自动生成的 PPT 把它缩得这么小？”
- “我想让 AI 帮我完成生产工作，但不希望它自己发明方法关系。”
- “我有一个新的科研想法，但表达它不应该首先取决于我会不会画一个漂亮的框架图。”

## 仓库结构

```text
AutoSCI/
├── skills/
│   ├── scientific-figure/
│   │   ├── SKILL.md
│   │   ├── STABILITY.md
│   │   ├── references/
│   │   ├── assets/
│   │   ├── scripts/
│   │   └── agents/
│   └── academic-research-presentation/
│       ├── SKILL.md
│       ├── references/
│       ├── templates/
│       ├── examples/
│       └── agents/
├── docs/
├── examples/
├── scripts/
└── .github/
```

顶层仓库会尽量保持简单。每个 Skill 都自包含，因此可以只复制一个 Skill 到本地使用，而不需要安装整个 AutoSCI。

## 本地验证

运行仓库级检查：

```bash
python scripts/validate_repo.py
```

检查 Scientific Figure 所需的本地 render/export 环境：

```bash
python skills/scientific-figure/scripts/doctor.py
```

Scientific Figure 的多数 audit script 只依赖 Python 标准库。SVG render/export 可以使用 CairoSVG 或 Inkscape；grayscale QA 可以使用 Pillow 或 ImageMagick。`doctor.py` 会报告当前环境可用能力。

## 开源方向

AutoSCI 会刻意从小做起。我们更希望维护少量**真正能够减轻科研重复劳动**的 workflow，而不是快速堆出几十个只有几段 Prompt 的 Skill。

未来如果增加新的 Skill，希望它同样解决一个具体、真实、反复出现的科研工作流问题。

长期目标可以概括成一句话：

> **降低科研生产中的机械成本，把更多空间还给科研创造力。**

对于已有 Skill，也不会为了功能数量持续膨胀。一个新规则最好能够对应一个可复现 failure；Scientific Figure 的生产行为修改尤其应该由 benchmark 证据驱动。

## 致谢与说明

Scientific Figure Skill 是独立实现，其 **generate → render → evaluate → refine** 思路部分受到公开科研绘图 agent 工作（如 [ResearAI/AutoFigure](https://github.com/ResearAI/AutoFigure) 与 [AutoFigure-Edit](https://github.com/ResearAI/AutoFigure-Edit)）的启发。AutoSCI 不包含这些项目的代码、模型权重、托管服务或 API Key，也与这些项目没有官方隶属关系。

Academic Research Presentation Skill 使用的公开参考资料列在 [`references/08-sources-and-rationale.md`](skills/academic-research-presentation/references/08-sources-and-rationale.md)。

AutoSCI 是独立社区项目，并非 OpenAI 官方项目。

## 贡献

欢迎提交 Issue、实际使用案例、benchmark case、workflow 改进和 Pull Request。详细规则见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

如果 AutoSCI 确实帮你省下了时间，一个很有价值的贡献就是告诉我们：**你用它完成了什么、它在哪里失败、真实科研场景下怎样做会更好。**

我们希望这个项目最终不是由“还能加什么 Prompt”驱动，而是由研究者真实遇到的问题驱动。

## License

MIT License，见 [`LICENSE`](LICENSE)。
