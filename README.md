# qianjin-child-art-to-living-world · 童画活化

把孩子的绘画（或任意照片）变成「**风格不变、有立体感、会动**」的鲜活小世界。

> 这是「前进（qianjin）」系列技能之一。把本目录放进支持 `SKILL.md` 的 Agent 平台（如 WorkBuddy、Claude）的技能目录即可使用。

## 它能做什么

| 你的诉求 | 用哪套工具 | 怎么保证「风格不变」 |
|----------|-----------|----------------------|
| 画的房子 → 立体实景 | **ImageGen 图生图** | `input_fidelity` 拉高，提示词锁死原画风，只加景深+光照，不写实 |
| 可旋转的 3D 模型 | **图生3D**（`scripts/gen3d_direct.py`，纯标准库） | 房子/每只动物单独生成可旋转 `.glb`，童趣低面数 |
| 画的动物活过来 | **VideoGen 图生视频** | 原图当首帧继承画风，轻柔动作；自动配乐并做响度归一化 |

**绘画和照片都支持**——照片走「同风格 3D 微缩景观」分支。

## 安装

把本仓库整个目录放到 Agent 的技能目录（如 `~/.workbuddy/skills/`），Agent 会在检测到相关意图时自动调用：

- 「把孩子的画变成 3D / 涂鸦变立体实景」
- 「让画里的小动物活过来 / 动起来」
- 「照片变成一个可以转着看的小世界 / 3D 模型」

## 目录结构

- `SKILL.md`：三阶段流水线 + 工具路由表 + 踩坑记录
- `references/prompts.md`：风格锁定提示词库（整幅 / 单主体 / 活过来 / 补色抠图）
- `scripts/gen3d_direct.py`：图生3D 直调脚本（纯标准库、跨平台、自动下载 `.glb` + 预览图）
- `scripts/make_viewer.py`：为 `.glb` 生成可旋转预览页（`viewer.html`）

## 前置依赖

- **Python 3.8+**：仅用标准库，无需 `pip install`。
- **ffmpeg**（可选）：视频音量归一化的必做后处理，以及多段视频拼接。
  - Windows：`winget install Gyan.FFmpeg`；macOS：`brew install ffmpeg`；Linux：`apt install ffmpeg`。
- **图生3D 需要临时 token**：通过 `connect_cloud_service` 获取，作为参数传入，每次重新获取、不硬编码。

## License

MIT © 前进 (ZOORO-NEW)
