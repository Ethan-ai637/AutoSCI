# AutoSCI

**面向科研绘图与学术汇报的本地 Codex Skills。**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Scientific Figure](https://img.shields.io/badge/Scientific%20Figure-v2.0%20stable-2ea44f)](skills/scientific-figure)
[![Research Presentation](https://img.shields.io/badge/Research%20Presentation-v3-blue)](skills/academic-research-presentation)

[English](README.md)

AutoSCI 不是新的基础模型，也不是某个在线 API 的套壳。它是一组面向本地 Codex 的科研工作流 Skill：把科研语义约束、结构化中间产物、可执行 QA、render/critique/refine 闭环和开源脚本组织起来，让 Codex 在处理科研图和科研汇报时更可靠。

目前包含两个彼此独立、又可以组合使用的 Skill：

| Skill | 主要用途 | 核心产物 |
| --- | --- | --- |
| [`scientific-figure`](skills/scientific-figure) | 方法总览、模型架构、机制图、pipeline、taxonomy、多面板概念图 | 可编辑且可追踪的 SVG；可选 PDF/PNG release 包 |
| [`academic-research-presentation`](skills/academic-research-presentation) | 论文汇报、组会、科研进展、technical talk | 面向 PPT/Slides 工具链的科研叙事、素材与 QA 工作流 |

## 为什么做 AutoSCI

AI 做科研视觉材料最危险的问题，往往不是“不够漂亮”，而是：

- 箭头方向错了；
- 把并行关系画成顺序关系；
- 为了简洁丢掉 side input / feedback / training-only component；
- 数学符号被偷偷改写；
- 论文主图截图缺坐标轴、legend 或 panel；
- 高清预览看起来正常，缩到论文/幻灯片实际尺寸后根本看不清；
- PPT 变成一堆卡片和文字框，真正的 figure/table 反而被缩小。

AutoSCI 的共同原则是：

> **科学正确性优先于美观；证据优先于装饰性流程图；结构优先于坐标；先 render 再相信结果。**

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

主要能力包括 source-grounded claims、semantic lock、Spec ↔ SVG traceability、geometry/notation/最终物理字号/portability 检查、`draft / standard / release` 三种执行强度、checkpoint/resume 与可选 blind benchmark。它不要求额外再接一个图像或 LLM API，本地 Codex 本身承担 planner / generator / critic。

## Academic Research Presentation V3

这个 Skill 的目标不是“做漂亮 PPT”，而是让科研汇报更接近研究者真正使用的 slide：主图主表优先、信息密度足够、证据完整、方法关系正确。

V3 重点处理两个高风险问题：AI 自己脑补/方向错误的流程图，以及从论文中截取不完整、被污染的 Figure/Table。核心约束包括 evidence before diagrams、显式 node/edge spec、render 后检查箭头方向、完整保留 axes/ticks/legend/panel、默认一页一个 hero scientific visual，以及 canvas-first 而不是 box/card-first。

它是科研汇报的 reasoning/QA Skill，不是独立 PPTX 渲染器，需要配合 Codex 环境中已有的 slides/PPTX 工具。

## 安装

```bash
git clone https://github.com/Ethan-ai637/AutoSCI.git
cd AutoSCI

mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/scientific-figure "${CODEX_HOME:-$HOME/.codex}/skills/"
cp -R skills/academic-research-presentation "${CODEX_HOME:-$HOME/.codex}/skills/"
```

然后重启/重新加载 Codex，会话中可以明确调用：

```text
Use $scientific-figure to turn the Method section of paper.pdf into an editable Figure 1.
```

```text
Use $academic-research-presentation to build a paper-reading deck from paper.pdf.
```

Windows 和更完整的安装说明见 [`docs/installation.md`](docs/installation.md)。

## 版本状态

- `scientific-figure`: **v2.0.0 stable**。之后不再凭感觉堆功能，生产规则修改应由可复现 benchmark failure 驱动。
- `academic-research-presentation`: **v3.0.0**。当前重点是 diagram safety 与 source visual completeness。

## 致谢与说明

Scientific Figure Skill 是独立实现，其 generate → render → evaluate → refine 思路部分受到公开科研绘图 agent 工作（如 [ResearAI/AutoFigure](https://github.com/ResearAI/AutoFigure) 与 [AutoFigure-Edit](https://github.com/ResearAI/AutoFigure-Edit)）的启发。AutoSCI 不包含这些项目的代码、模型、托管服务或 API Key，也与其没有官方隶属关系。

Academic Research Presentation Skill 使用到的公开参考资料列在 [`references/08-sources-and-rationale.md`](skills/academic-research-presentation/references/08-sources-and-rationale.md)。AutoSCI 是独立社区项目，并非 OpenAI 官方项目。

## 贡献与 License

欢迎 issue / PR。贡献规则见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

MIT License，见 [`LICENSE`](LICENSE)。
