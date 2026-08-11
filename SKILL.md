---
name: qianjin-child-art-to-living-world
slug: qianjin-child-art-to-living-world
displayName: 童画活化 · 把孩子的画变成立体鲜活的小世界（qianjin）
version: 1.0.0
summary: 把孩子的绘画或照片变成风格不变、有立体感、会动的鲜活小世界——3D 实景渲染、可旋转 3D 模型、让画里动物活过来的动画。绘画和照片都支持。
license: MIT
description: >
  把孩子的绘画（或任意照片）变成「立体、真实、鲜活」的小世界：保持原画风不变，
  生成有景深与光照的 3D 实景渲染，并把画里的动物/角色「活过来」做动画。
  当用户说：孩子的画变成 3D / 涂鸦变立体实景 / 画风不变但变立体 / 让画里的动物活过来 /
  儿童画转 3D 场景 / 照片变 3D 小世界 / 手绘变立体动画 / 把画做成可旋转的 3D 模型 时使用。
  核心能力：风格锁定的 3D 化（ImageGen 图生图）、单主体真 3D 模型（图生3D）、
  让画面活起来（VideoGen 图生视频）。绘画和照片都支持。
agent_created: true
---

# 童画活化 · 把画变成立体鲜活的小世界

把一张儿童画（或照片）变成 **「风格不变、有立体感、会动」** 的鲜活世界。
这是一套三阶段流水线，组合使用三套生成工具，关键原则是 **「只加立体与生命，不改画风」**。

## 一、何时触发

- 「把孩子的画变成 3D / 立体实景，但风格不变」
- 「让画里的小动物活过来 / 动起来」
- 「照片（或涂鸦）变成一个可以转着看的小世界 / 3D 模型」
- 任意「2D → 立体 + 鲜活」的创意需求，**绘画和照片都支持**

## 二、核心原则：风格不变（最重要）

用户要的是「同一个孩子的画」变立体，**不是变成写实照片**。因此：

1. **保风格优先于保真实**。所有提示词第一句都要写死画风约束（见 references/prompts.md）。
2. **图生图用 `input_fidelity` 拉高**（0.75–0.92），越高越贴近原画。
3. **图生视频用原图当首帧**（`image=原图`），模型天然继承画风；prompt 里再强调「保持原画风」。
4. **区别两个词**：
   - 「立体 / 实景」= 有景深、有光照、有材质体积感（diorama / papercraft / claymation 风），**不是照片级写实**。
   - 「活过来」= 让角色产生温柔的生命动作（眨眼、呼吸、摇尾、转头）+ 缓慢镜头推移露出空间感。

## 三、工具路由表（用对工具）

| 子目标 | 用哪个工具 | 关键参数 |
|--------|-----------|---------|
| 整幅画 → 风格锁定的 3D 立体渲染（diorama 实景感） | **ImageGen 图生图** | `image=[原图]`, `input_fidelity` 高, `prompt` 见 prompts.md |
| 单个主体（房子/某只动物）→ 真正可旋转的 3D 模型 | **图生3D**（技能自带 `scripts/gen3d_direct.py`，纯标准库、跨平台） | `<image> <token> --generate-type LowPoly/Normal --enable-pbr` |
| 让画里的动物/角色「活过来」做动画 | **VideoGen 图生视频** | `image=原图或渲染图`, `prompt` 写动作+镜头, `seconds`, `aspect_ratio`, **`enable_audio=true` 默认开（自动按氛围配乐）** |
| （不用于本技能）视频特效模板 | 不用 | 与本需求无关，避免误用 |

> 工具发现：ImageGen / VideoGen 是延迟工具，先 `ToolSearch` 拿到 schema，再 `DeferExecuteTool` 调用。
> 图生3D 走本技能自带的 `scripts/gen3d_direct.py`（纯标准库，无第三方依赖，自动下载结果到本地，无需手动 curl）。

## 四、三阶段流水线（默认执行顺序）

### 阶段 0 · 收图与拆解
- 拿到用户的图（本地路径或 URL）。若是照片且背景杂乱，先确认是否要保留背景。
- 用一句话描述画面主体：**房子？几只动物？树/太阳/云？** 这些决定后面拆不拆主体。
- 问用户想要哪种产出（可多选，默认全做）：
  1. 一张「立体实景渲染图」（最省力，出图快）
  2. 可旋转的 3D 模型（房子 + 每只动物各一个）
  3. 一段「活过来」的动画视频

### 阶段 1 · 风格锁定的 3D 立体渲染（ImageGen 图生图）
- 调用 ImageGen，`image=[原图]`，`input_fidelity=0.85`，`quality=high`。
- `prompt` 用 prompts.md 的 **「整幅画 → 立体实景」** 模板（diorama / papercraft 风，保画风）。
- 这一步产出一张「看起来能拿在手里的小世界」图，是后续视频的首帧候选。
- 若用户原图已是照片且想「变 3D 小世界」，同样流程，prompt 改为「把这张照片变成同风格的 3D 微缩景观」。

### 阶段 2 · 单主体真 3D 模型（图生3D，可选）
- 对 **房子** 和 **每只主要动物** 单独生成可旋转 3D 模型：
  - 图生3D 对「干净背景的单个主体」效果最好。若原图主体多，先裁出单个主体（用 ImageGen 图生图做去背景/抠图，或请用户给单主体图）。
  - 用本技能脚本 `scripts/gen3d_direct.py`（纯标准库，跨平台，自动下载 glb + 预览图到本地）：
    ```bash
    # 先取一次性临时 token（绝不复用/硬编码）
    #   → 通过 connect_cloud_service 获取，管道/参数传入
    python scripts/gen3d_direct.py "<单主体图路径>" "<token>" \
      --generate-type LowPoly --enable-pbr --out-dir "./3d_out"
    ```
  - 推荐：`--generate-type LowPoly`（童趣低面数，配默认 `--model 3.0`）或 `Normal`；`--enable-pbr` 开材质。脚本自带轮询（最多 10 分钟），**不要在外层加 sleep 重试**。
  - 输出 JSON 到 stdout（含 `local_path`），进度/信息在 stderr；脚本已自动把 `.glb` 和预览图下载到 `--out-dir`。
  - `prompt` 用 prompts.md 的 **「单主体 → 3D 模型」** 模板（注：纯图生成时模型不需文字 prompt）。
- 生成后用 `scripts/make_viewer.py` 为每个 `.glb` 生成 `viewer.html` 并起本地 HTTP 服务预览（rotate/缩放）。

### 阶段 3 · 让画面活过来（VideoGen 图生视频）
- 选首帧：优先用阶段 1 的立体渲染图；想要「画本身活了」的纯粹感则用原图。
- 调用 VideoGen：`image=首帧`, `prompt` 用 prompts.md 的 **「动物活过来」** 或 **「整幅世界活起来」** 模板。
- 参数：`seconds=5~8`，`aspect_ratio` 与原图一致（如 `1:1`/`4:3`），`resolution=1080P`，`watermark=false`（如允许），**`enable_audio=true`（默认开，平台自动按童话氛围生成背景乐，已验证可用：AAC 双声道）**。
- **关于「自动声音」**：VideoGen 的 `enable_audio` 已能自动生成贴合情绪的通用水晶乐/环境音，省心且风格统一；但它是「通用氛围乐」，**不是**针对这幅画定制的 Foley（如风吹落叶、蝴蝶振翅、小鸟啁啾这类和画面动作一一对应的音效）。若要更贴合，见下方「进阶：定制音效」。
- 多主体分别活：若动物很多，可对每一只单独跑「动物活过来」，再用 ffmpeg 拼成同一画面（可选，进阶）。

### 阶段 3.5 · 进阶：定制音效（可选，让声音真正「贴画」）
- **目标**：把「通用氛围乐」升级为「针对这幅画」的定制声景——如 8 秒水晶音乐盒旋律 + 轻柔风声 + 蝴蝶/小鸟点缀，按画面动作对齐（落叶时风声起、蝴蝶段加振翅）。
- **做法**（有 ffmpeg 即可，零素材）：
  1. 用合成器/现成免版权儿童音效，按 8 秒时间轴做一条音轨（或用 `enable_audio` 的原声做底，叠定制音效）。
  2. `ffmpeg -i <video.mp4> -i <soundtrack.wav> -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 <out.mp4>` 混流。
- **权衡**：默认 `enable_audio` 已够「自动适配」；只有用户明确想要「画面动作和声音严丝合缝」时才走此路径，避免每次都加重活。

### 阶段 4 · 交付
- 图片 → `present_files` 展示本地渲染图。
- 3D 模型 → 展示 `.glb` 并给出 viewer 本地预览地址（说明关闭服务器的命令）。
- 视频 → `present_files` 展示本地 `.mp4`。
- 一句话告诉用户每个文件在哪、能做什么（旋转 / 播放）。

## 五、执行细节（参数与坑）

### ImageGen 图生图
- 通过 `ToolSearch` → `DeferExecuteTool` 调用。
- 必带 `image`（1–3 张，本地路径或 URL）和 `input_fidelity`（高保风格）。
- `size` 与原图比例一致；`quality=high`；`background` 默认即可。
- 不要开 `revise`（会改提示词，可能破坏风格锁定）。

### VideoGen 图生视频
- 通过 `ToolSearch` → `DeferExecuteTool` 调用。
- `image` 传首帧（本地路径或 URL）；`prompt` 详细写动作+镜头+画风。
- `seconds` 默认 5，最多按需；`resolution` 只接受 `720P`/`1080P`；`aspect_ratio` 用 `16:9`/`9:16`/`1:1` 等。
- `negative_prompt` 写：「photorealistic, realistic photo, deformed, extra limbs, jitter, style change」（防跑偏/破画风）。
- **音量为何偏轻 + 必做后处理**：平台 `enable_audio` 自动生成的配乐普遍压得极轻（实测均值约 -50dB、峰值约 -31dB，用户需开到最大声才听得见）。**生成后必须跑 ffmpeg 响度归一化**：
  ```bash
  ffmpeg -i <in.mp4> -af "loudnorm=I=-13:TP=-1.0:LRA=6" -c:v copy -c:a aac -b:a 192k <out_loud.mp4>
  ```
  目标：均值提到约 -15dB、峰值贴近 -1.0dB（限幅不破音）。交付时优先给归一化版，原版可保留。

### 图生3D（本技能 `scripts/gen3d_direct.py`）
- **为何自带脚本**：平台 `buddy-cloud.py` 在 Windows 上有 32KB 命令行长度限制（base64 无法走 `--image-base64` / `--image-url` 也因云端访问不了 localhost 而失效）。本脚本把 base64 放 HTTP body、用纯标准库调用，跨平台零依赖，并自动下载结果。
- 认证：先用 `connect_cloud_service` 拿一次性临时 token，作为参数传入（`gen3d_direct.py <图> <token>`），**每次重新获取，绝不复用/硬编码到文件**。
- 用法：
  ```bash
  # <skill_dir>/scripts/gen3d_direct.py
  python gen3d_direct.py <单主体图路径> <token> \
    [--model 3.0] [--generate-type LowPoly|Normal] [--enable-pbr] \
    [--out-dir <下载目录>] [--glb-name <名.glb>] [--no-download]
  ```
- 输出纯 JSON 到 **stdout**（`job_id` / `preview_image_url` / `result_files[].local_path`），进度写 **stderr**。已自动下载 `.glb` 与预览图到 `--out-dir`（默认 `<图同目录>/3d_out`）。
- 自带轮询（最多 10 分钟），**不要在外层加 sleep 重试**；失败会抛 RuntimeError 并显示云端错误信息。
- 模型默认输出 `.glb`（含 `.obj` 备选），无需手动 curl。

### 前置依赖（通用环境）
- **Python 3.8+**：仅用到标准库（`urllib`/`base64`/`hmac` 等），无需 `pip install`。脚本用 `python`（Windows）或 `python3`（macOS/Linux）均可。
- **ffmpeg**：用于视频音量归一化（阶段 3 必做后处理）与可选的多段视频拼接。需已安装并在 `PATH` 中。
  - Windows：可通过 `winget install Gyan.FFmpeg` 安装；或确保 `ffmpeg.exe` 在 PATH。
  - macOS：`brew install ffmpeg`；Linux：`apt install ffmpeg` / `dnf install ffmpeg`。
- **本地 HTTP 服务器**（仅 3D 预览需要）：用 `python -m http.server` 起服务打开 `viewer.html`（`file://` 无法加载本地 `.glb`）。

## 六、局限与贴士
- 图生3D 适合「单个干净主体」；整幅拥挤的画用它易糊 → 整幅交给 ImageGen 图生图做 diorama，单主体再拆出来做真 3D。
- 风格越「孩子气」（蜡笔/马克笔/水彩）效果越好；线稿太淡或对比太低时，先用 ImageGen 图生图补一下色彩与对比。
- 动物「活过来」用轻柔动作最自然；大幅跳跃/奔跑容易穿帮，prompt 里强调「slow, tender, subtle」。
- 全部产物落地到工作目录，命名带时间戳，便于回看。

## 七、参考
- 提示词库（整幅/单主体/活过来模板）：`references/prompts.md`
- 3D 预览页生成：`scripts/make_viewer.py <glb路径> [输出html路径]`
