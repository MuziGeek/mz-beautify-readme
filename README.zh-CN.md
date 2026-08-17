<p align="right"><a href="README.md">English</a></p>

<p align="center">
  <img src="docs/readme/hero.svg" width="100%" alt="MZ Beautify README 先锁定项目证据与核心设计决定，再应用经过校验的公共视觉 Brief">
</p>

# MZ Beautify README

证据优先、项目原生设计、只接受显式视觉扩展。

MZ Beautify README 是用于审查、重构、本地化和制作 GitHub README 首页的公共身份中立 Skill。它固定 `oil-oil/beautify-github-readme` 设计核心，先锁定仓库事实与真实证明，再应用经过校验的 `mz.visual-brief/1`，且不改变核心设计决定。

## 职责边界

| README 核心负责 | Visual Brief 可以改变 |
| --- | --- |
| 项目声明、信息顺序、真实证明、第一次成功操作 | 公共语义色彩与渲染处理 |
| 主题判断与构图 | 兼容的线条、纹理和材质角色 |
| SVG / Hybrid / Raster 技术路线 | 显式传入且哈希有效的 Extension |
| 多语言、响应式、可访问性与 GitHub 安全 | 仅限公共 Profile 允许的 Extension 能力 |

仓库所有者不会触发任何身份。直接调用固定解析为 `readme-visual + mz-readme-project-native-v1`；私人或品牌视觉必须显式提供 Extension。

## 安装与使用

```text
Use $skill-installer to install:
https://github.com/MuziGeek/mz-beautify-readme/tree/main/mz-beautify-readme
```

```text
Use $mz-beautify-readme 围绕这个仓库最有力的真实证明重构 README，生成英文和简体中文资产，在本地完成校验，不要发布。
```

支持直接公共请求、经过校验的 `mz.visual-brief/1`，或 Visual Brief 加显式 Extension 路径。

## 契约与评审边界

- `mz.readme-brief/3` 将 Visual Brief 与不可变的 `coreDecision` 分开记录。
- `mz.readme-asset/3` 记录 README Brief、Visual Brief、来源、语言、视口、输出及可选 Extension 哈希。
- 公共版与 Extension 版在生产前必须只允许 `visualBrief` 和评审状态不同。
- GIF 只能显式启用。所有路线止于 `READY_FOR_REVIEW`，发布需要另行授权。

## 验证

```text
python scripts/verify_upstream_snapshot.py
python scripts/test_mz_beautify_readme.py
python scripts/validate_visual_brief.py path/to/visual-brief.json
python scripts/validate_brief.py path/to/readme-brief.json
python scripts/validate_asset_manifest.py path/to/hero-manifest.json
python scripts/audit_readme.py path/to/README.md
```

代码与文档使用 MIT；固定的上游快照继续保留原 MIT 归属。
