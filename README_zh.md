# AutoSCI

<p align="center">
  <img src="assets/readme/autosci-hero-zh.png" alt="AutoSCI——面向科研绘图与学术汇报的开源 Codex Skills" width="100%">
</p>

<p align="center"><strong>把时间留给科研本身，把繁琐留给工具。</strong></p>

<p align="center">
  面向科研绘图、论文阅读、组会汇报、科研进展与学术表达工作的开源、本地优先 Codex Skills。
</p>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="#目前包含的-skills">Skills</a> ·
  <a href="#底层是怎么工作的">底层实现</a> ·
  <a href="skills/scientific-figure/scripts/">Python 工具</a> ·
  <a href="CONTRIBUTING.md">参与贡献</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Scientific%20Figure-v2.0%20stable-2ea44f" alt="Scientific Figure v2.0">
  <img src="https://img.shields.io/badge/Research%20Presentation-v3-blue" alt="Research Presentation v3">
  <img src="https://img.shields.io/badge/Python-tooling-3776AB" alt="Python tooling">
</p>

## AutoSCI 是什么？

AutoSCI **不只是一组提示词**。我们把科研工作经验组织成可检查、可修改的 Codex Skill，并把适合确定性解决的环节交给真正的程序工具。

```text
论文 / 方法 / 实验 / 研究结果
              │
              ↓
        Codex Skill 工作流
      (SKILL.md + references)
              │
       ┌──────┴──────┐
       ↓             ↓
  科研推理与表达    确定性工具链
  科研人员式决策    Python / QA / render
       └──────┬──────┘
              ↓
          科研产物
      科研图 / 汇报 / QA
```

核心思想是：**把科研判断沉淀为可检查的工作流，把机械、重复、可以确定性验证的部分交给代码。**

## 为什么做 AutoSCI？

科研时间很宝贵，但研究者每天仍然会被大量必要却重复的工作消耗：重画方法框架、对齐箭头、修改流程图、整理论文 Figure、重新排版 PPT，以及一遍遍检查最终展示效果。

**AutoSCI 想做的，就是尽可能降低这些科研生产中的机械成本。**

我们希望研究者把更多注意力留给真正需要创造力和判断力的事情：提出问题、设计方法、完成实验、理解结果、讨论局限，以及想清楚下一步值得探索什么。

这并不是让 AI 替代科研思考，而是减少一个好想法变成清晰科研表达之间的摩擦。

> **自动化繁琐工作，保持科学表达准确，把更多空间还给科研想象力。**

## 目前包含的 Skills

| Skill | 做什么 | 实现方式 |
| --- | --- | --- |
| [`scientific-figure`](skills/scientific-figure) | 从 Method、equation、code、data 或已有科研图创建/重构可编辑科研图 | Skill 工作流 + references + **Python 流程编排、审计、渲染、release 与 benchmark 工具链** |
| [`academic-research-presentation`](skills/academic-research-presentation) | 论文汇报、组会、科研进展与 technical talk 的 evidence-first 工作流 | Skill 工作流 + references + templates + source visual / diagram QA 规则 |

两个 Skill 可以独立安装，也可以串联使用：

```text
论文 / Method / Results
        │
        ├── 需要自定义科研图？
        │          ↓
        │   $scientific-figure
        │          ↓
        │      Editable SVG
        │
        └──────────┬──────────
                   ↓
      $academic-research-presentation
                   ↓
              科研汇报
```

## 底层是怎么工作的？

这个仓库有意把 **Agent 指令、科研领域知识、结构化模板和可执行代码** 放在一起，而不是把流程藏在一个黑盒在线服务后面。

### Scientific Figure：可执行的科研绘图流水线

```text
SKILL.md
   ↓
source-grounded figure_spec.json
   ↓
Python orchestration
   ↓
editable SVG master
   ↓
确定性 QA
   ├── source / claim audit
   ├── semantic traceability
   ├── geometry audit
   ├── notation audit
   ├── final-size legibility
   └── portability / release checks
   ↓
render → critique → targeted refinement
   ↓
SVG / PNG / PDF release package
```

真正的可执行代码集中在 [`skills/scientific-figure/scripts/`](skills/scientific-figure/scripts)：

```text
doctor.py              环境能力检查
orchestrate.py         工作流状态与 checkpoint 编排
validate_spec.py       semantic spec 校验
source_audit.py        claim-to-source grounding 审计
geometry_audit.py      SVG geometry 检查
notation_audit.py      数学符号与 notation 检查
preflight.py           profile-aware 确定性 QA
render_svg.py          SVG 渲染
render_package.py      inspection/render package
finalize_figure.py     release 打包
benchmark.py           单案例评测
benchmark_suite.py     多案例 Skill 评测
```

`academic-research-presentation` 则更偏 reasoning / workflow：其实现主要由 `SKILL.md` 中的科研汇报流程、`references/` 中的 source-visual 与 diagram safety 规则，以及 `templates/` 中可复用的 evidence / storyboard / preflight 结构组成。

## 我们希望自动化什么？又不希望自动化什么？

**适合交给工具的工作：**重复性的科研图构建、布局与 routing、Figure/Table 提取检查、汇报编排、notation/geometry/clipping/readability 等确定性 QA，以及反复的 render → inspect → refine。

**仍然属于研究者的工作：**选择问题、决定假设与方法、验证实验和证据、解释结果、判断哪些 claim 成立，以及做最终的科研表达取舍。

AutoSCI 的目标很简单：**减少科研周边的机械劳动，但不减少研究者的判断权。**

## Scientific Figure v2.0

`scientific-figure` 是一个 structure-first 的可编辑科研绘图工作流，把 source-grounded semantic contract、traceable SVG 与确定性的 Python QA 组合在一起。

主要能力包括 semantic lock、Spec ↔ SVG traceability、anti-box-soup visual grammar、geometry / notation / legibility / portability audits、`draft / standard / release` 三种执行强度、checkpoint/resume、release packaging，以及可选 blind benchmark。

对于折线图、柱状图、heatmap 等数值实验图，Skill 明确优先使用真实数据 + plotting code，而不是让模型“画一条看起来合理的曲线”。

详见 [`SKILL.md`](skills/scientific-figure/SKILL.md)、[`STABILITY.md`](skills/scientific-figure/STABILITY.md) 和可执行的 [`scripts/`](skills/scientific-figure/scripts/) 目录。

## Academic Research Presentation V3

这个 Skill 的目标不是批量生产“漂亮模板 PPT”，而是帮助 Codex 做出更接近科研人员真正使用的汇报：**主图主表优先、信息密度足够、证据完整、方法关系正确。**

核心优先级是：科学正确性 → 原始证据完整 → Figure/Table/Equation → 技术机制 → 叙事与视觉表达。

V3 重点处理两个自动生成汇报中非常常见的问题：AI 自己脑补或方向错误的流程图，以及从论文中截取不完整、被污染的 Figure/Table。默认强调 evidence-first、完整 source visual、一页一个 hero scientific visual、canvas-first，以及 render 后再做页面 QA。

它是科研汇报的 reasoning / QA Skill，不是独立 PPTX 渲染器，需要配合 Codex 环境中的 slides/PPTX 工具链。

详见 [`SKILL.md`](skills/academic-research-presentation/SKILL.md)、[`references/`](skills/academic-research-presentation/references/) 和 [`templates/`](skills/academic-research-presentation/templates/)。

## 快速开始

```bash
git clone https://github.com/Ethan-ai637/AutoSCI.git
cd AutoSCI

mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/scientific-figure "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/academic-research-presentation "${CODEX_HOME:-$HOME/.codex}/skills/"
```

重新加载 Codex 后，可以直接调用：

```text
Use $scientific-figure to turn the Method section of paper.pdf into an editable Figure 1.
```

```text
Use $academic-research-presentation to build a paper-reading deck from paper.pdf.
```

Scientific Figure 还可以直接检查本地环境：

```bash
python skills/scientific-figure/scripts/doctor.py
```

## 仓库结构

```text
AutoSCI/
├── assets/readme/                      # README 视觉素材
├── skills/
│   ├── scientific-figure/
│   │   ├── SKILL.md                    # Codex Skill 入口
│   │   ├── agents/                     # Agent metadata
│   │   ├── assets/                     # 结构化模板
│   │   ├── references/                 # 工作流与领域知识
│   │   └── scripts/                    # 可执行 Python 工具链
│   └── academic-research-presentation/
│       ├── SKILL.md                    # Codex Skill 入口
│       ├── references/                 # 科研汇报规则
│       ├── templates/                  # evidence/storyboard/QA 模板
│       └── examples/                   # anti-pattern 示例
├── README.md
├── README_zh.md
└── LICENSE
```

每个 Skill 都尽量保持 self-contained，可以单独复制到本地 Codex skills 目录使用。

## 设计原则

- **科学正确性优先于美观。**
- **证据优先于装饰性流程图。**
- **先确定结构，再处理坐标。**
- **优先保留可编辑源产物，而不是只有截图。**
- **确定性 failure 尽量交给确定性代码。**
- **先 render 再相信生成结果。**
- **只有可复现 failure 能证明必要时，才继续增加工作流复杂度。**

## 项目状态

- `scientific-figure`: **v2.0.0 stable**。
- `academic-research-presentation`: **v3.0.0**，当前重点是 evidence-first、diagram safety 与 source visual completeness。

## 致谢与说明

Scientific Figure Skill 是独立实现，其 generate → render → evaluate → refine 思路部分受到公开科研绘图 agent 工作（如 [ResearAI/AutoFigure](https://github.com/ResearAI/AutoFigure) 与 [AutoFigure-Edit](https://github.com/ResearAI/AutoFigure-Edit)）的启发。AutoSCI 不包含这些项目的代码、模型、托管服务或 API Key，也与其没有官方隶属关系。

Academic Research Presentation Skill 使用到的公开参考资料列在 [`references/08-sources-and-rationale.md`](skills/academic-research-presentation/references/08-sources-and-rationale.md)。

AutoSCI 是独立社区项目，并非 OpenAI 官方项目。

## 参与贡献

欢迎 issue / PR。贡献规则见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

> **新增一条规则，应当对应一个具体、可复现的失败模式。**

## License

MIT License，见 [`LICENSE`](LICENSE)。
