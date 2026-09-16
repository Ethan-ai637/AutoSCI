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
  <a href="CONTRIBUTING.md">参与贡献</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Scientific%20Figure-v2.0%20stable-2ea44f" alt="Scientific Figure v2.0">
  <img src="https://img.shields.io/badge/Research%20Presentation-v3-blue" alt="Research Presentation v3">
</p>

## 为什么做 AutoSCI？

科研时间很宝贵，但研究者每天仍然会被大量必要却重复的工作消耗：重画方法框架、对齐箭头、修改流程图、整理论文截图、补齐 legend、重新排版 PPT、把同一张图改到不同尺寸，以及一遍遍检查最终展示效果。

**AutoSCI 想做的，就是尽可能降低这些科研生产中的机械成本。**

我们希望研究者把更多注意力留给真正需要创造力和判断力的事情：提出问题、设计方法、完成实验、理解结果、讨论局限，以及想清楚下一步值得探索什么；把绘图、排版、素材整理、重复检查和迭代修改中可以被规范化的部分，交给可复用的 Codex Skill。

这并不是让 AI 替代科研思考，而是减少一个好想法变成清晰科研表达之间的摩擦。

> **自动化繁琐工作，保持科学表达准确，把更多空间还给科研想象力。**

AutoSCI 不是新的基础模型，也不是某个在线 API 的套壳。它是一组可检查、可修改、可复用的科研工作流：结构化中间产物、source grounding、确定性 QA 脚本，以及 render → inspect → refine 的执行闭环。

## 目前包含的 Skills

| Skill | 适用场景 | 主要产物 |
| --- | --- | --- |
| [`scientific-figure`](skills/scientific-figure) | 方法总览、模型架构、机制图、pipeline、taxonomy、多面板科研图 | 可编辑、可追踪的 SVG；可选 PDF/PNG release 包 |
| [`academic-research-presentation`](skills/academic-research-presentation) | 论文汇报、组会、科研进展、technical talk | 证据优先的汇报工作流、页面规划、Figure/Table 使用与 QA |

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

## 我们希望自动化什么？又不希望自动化什么？

**适合交给工具的工作**

- 重复性的科研图构建、重绘与格式转换；
- diagram 的布局、对齐、连接、导出与尺寸调整；
- 论文 Figure/Table 的提取与完整性检查；
- 组会和论文汇报中的重复性页面编排；
- 数学符号、箭头、geometry、字号、裁切和 portability 等确定性检查；
- render → 检查 → 修改 → 再 render 的机械循环。

**仍然属于研究者的工作**

- 选择真正值得研究的问题；
- 决定假设、方法和实验设计；
- 判断证据是否充分；
- 解释结果与局限；
- 决定哪些 claim 在科学上成立；
- 做最终的科研表达与取舍。

AutoSCI 的目标很简单：**减少科研周边的机械劳动，但不减少研究者的判断权。**

## Scientific Figure v2.0

核心流程：

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

主要能力包括 source-grounded claims、semantic lock、Spec ↔ SVG traceability、anti-box-soup visual grammar、geometry / notation / 最终物理字号 / portability 检查、`draft / standard / release` 三种执行强度、checkpoint/resume，以及可选 blind benchmark。

对于折线图、柱状图、heatmap 等数值实验图，Skill 明确优先使用真实数据 + plotting code，而不是让模型“画一条看起来合理的曲线”。

详见 [`skills/scientific-figure/README.md`](skills/scientific-figure/README.md)。

## Academic Research Presentation V3

这个 Skill 的目标不是批量生产“漂亮模板 PPT”，而是帮助 Codex 做出更接近科研人员真正使用的汇报：**主图主表优先、信息密度足够、证据完整、方法关系正确。**

核心优先级是：

```text
科学正确性
    ↓
论文原始证据完整
    ↓
Figure / Table / Equation
    ↓
技术机制
    ↓
叙事与视觉表达
```

V3 重点处理两个自动生成汇报中非常常见的问题：AI 自己脑补或方向错误的流程图，以及从论文中截取不完整、被污染的 Figure/Table。默认强调 evidence-first、完整 source visual、一页一个 hero scientific visual、canvas-first，以及 render 后再做页面 QA。

它是科研汇报的 reasoning / QA Skill，不是独立 PPTX 渲染器，需要配合 Codex 环境中的 slides/PPTX 工具链。

详见 [`skills/academic-research-presentation/README.md`](skills/academic-research-presentation/README.md)。

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

Windows 和更完整的安装说明见 [`docs/installation.md`](docs/installation.md)。

## 设计原则

- **科学正确性优先于美观。**
- **证据优先于装饰性流程图。**
- **先确定结构，再处理坐标。**
- **优先保留可编辑源产物，而不是只有截图。**
- **先 render 再相信生成结果。**
- **能确定性检查的问题，尽量交给脚本而不是模型主观判断。**
- **只有可复现 failure 能证明必要时，才继续增加工作流复杂度。**

## 仓库结构

```text
AutoSCI/
├── assets/readme/
├── skills/
│   ├── scientific-figure/
│   └── academic-research-presentation/
├── docs/
├── examples/
├── scripts/
└── .github/
```

每个 Skill 都尽量保持 self-contained，可以单独复制到本地 Codex skills 目录使用。

## 项目状态

- `scientific-figure`: **v2.0.0 stable**。后续生产规则修改应由可复现 benchmark failure 驱动，而不是继续凭感觉堆功能。
- `academic-research-presentation`: **v3.0.0**。当前重点是 evidence-first、diagram safety 与 source visual completeness。

## 致谢与说明

Scientific Figure Skill 是独立实现，其 generate → render → evaluate → refine 思路部分受到公开科研绘图 agent 工作（如 [ResearAI/AutoFigure](https://github.com/ResearAI/AutoFigure) 与 [AutoFigure-Edit](https://github.com/ResearAI/AutoFigure-Edit)）的启发。AutoSCI 不包含这些项目的代码、模型、托管服务或 API Key，也与其没有官方隶属关系。

Academic Research Presentation Skill 使用到的公开参考资料列在 [`references/08-sources-and-rationale.md`](skills/academic-research-presentation/references/08-sources-and-rationale.md)。

AutoSCI 是独立社区项目，并非 OpenAI 官方项目。

## 参与贡献

欢迎 issue / PR。贡献规则见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。我们希望长期坚持一个简单原则：

> **新增一条规则，应当对应一个具体、可复现的失败模式。**

## License

MIT License，见 [`LICENSE`](LICENSE)。
