# AutoSCI Installation / 安装指南

All nine AutoSCI Skills live in `skills/<name>/SKILL.md`. You can install them individually or together, without first publishing a package to the npm public registry.

## Recommended: standard Skills CLI (npx)

Requires Node.js/npm and network access to GitHub.

```bash
# Discover available skills
npx skills add Ethan-ai637/AutoSCI --list

# Install ALL skills for Codex (user-wide)
npx skills add Ethan-ai637/AutoSCI --skill '*' --agent codex --global --yes

# Install just one skill
npx skills add Ethan-ai637/AutoSCI --skill paper-reproduction --agent codex --global --yes

# Install in the current project
npx skills add Ethan-ai637/AutoSCI --skill scientific-figure --agent codex --yes
```

The external Skills CLI supports other agents and further management options: https://skills.sh/docs/cli.

## AutoSCI npm CLI directly from GitHub

This repo also ships a dependency-free Node.js 18+ `autosci` installer. npm can install and run packages directly from GitHub (Git required), even before npm-registry publication:

```bash
# Run without permanent installation
npm exec --yes --package=github:Ethan-ai637/AutoSCI -- autosci list
npm exec --yes --package=github:Ethan-ai637/AutoSCI -- autosci install --all
npm exec --yes --package=github:Ethan-ai637/AutoSCI -- autosci install scientific-figure --global

# Or install the CLI globally
npm install --global github:Ethan-ai637/AutoSCI
autosci list
autosci install --all --global
autosci install paper-reproduction --global --force
```

By default the installer copies into `.agents/skills/` for the current Codex project; `--global` uses `${CODEX_HOME:-~/.codex}/skills/`. Other choices: `--agent codex|claude-code|cursor`, `--dir PATH`, `--dry-run`, and `--force`. The `--force` option **replaces an existing Skill directory including any local edits**. Without it, existing installations are protected. The installer copies files and does not execute bundled scientific Python scripts.

`autosci-research-skills` is the package name reserved in this repository's metadata; no publication to the public npm registry is claimed. Only use `npm install -g autosci-research-skills` **after** a verified registry release.

## Clone / ZIP (manual)

```bash
git clone https://github.com/Ethan-ai637/AutoSCI.git
cd AutoSCI
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/scientific-figure "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Alternatively download the source ZIP from GitHub and copy the complete desired `skills/<name>` directory. Preserve accompanying scripts, references, templates, schemas, fixtures and assets.

## Available Skill names / Skill 名称

```text
academic-manuscript-writing
academic-research-presentation
experiment-execution
experiment-goal-design
literature-research
manuscript-reviewer
paper-reproduction
scientific-data-analysis
scientific-figure
```

## Maintainer checks

```bash
npm test
npm run check
npm pack --dry-run
```

CI checks the installer and confirms that the npm tarball contains every Skill entry point. The npm package version describes the distribution layer only: each scientific Skill retains its own version history and requirements.

## 中文速查

全量安装（推荐）：

```bash
npx skills add Ethan-ai637/AutoSCI --skill '*' -a codex -g -y
```

只安装一个 Skill：

```bash
npx skills add Ethan-ai637/AutoSCI --skill literature-research -a codex -g -y
```

也可通过 npm 直接从 GitHub 使用 AutoSCI 安装器：

```bash
npm exec --yes --package=github:Ethan-ai637/AutoSCI -- autosci install --all --global
```

这里的 npm 命令不依赖预先发布 npm 官方包。默认保护已有安装，`--force` 才会覆盖，并会丢失对原目录的本地修改。各 Skill 的运行依赖（如 Python 库、数据、渲染工具）仍需按对应 Skill 文档配置。
