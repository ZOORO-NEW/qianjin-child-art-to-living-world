#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为图生3D 产出的 .glb 生成一个可交互的 viewer.html（旋转/缩放/自动旋转）。
用法:
    python make_viewer.py <glb_path> [output_html_path]
说明:
    - <model-viewer> 通过 CDN 引入，src 用相对路径引用同目录 .glb。
    - 必须用本地 HTTP 服务器打开（file:// 下 fetch 本地 glb 会被浏览器拦截）。
"""
import sys
import os


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>3D Model Viewer</title>
  <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
  <style>
    html, body {{ margin: 0; height: 100%; }}
    body {{ overflow: hidden; background: #f0f0f0; }}
    model-viewer {{ width: 100vw; height: 100vh; --poster-color: transparent; }}
  </style>
</head>
<body>
  <model-viewer src="{glb_name}"
    camera-controls auto-rotate shadow-intensity="1"
    exposure="1.1" environment-image="neutral"
    alt="3D model">
  </model-viewer>
</body>
</html>
"""


def main():
    if len(sys.argv) < 2:
        print("用法: python make_viewer.py <glb_path> [output_html_path]")
        sys.exit(1)

    glb_path = sys.argv[1]
    if not os.path.isfile(glb_path):
        print("错误: 找不到 glb 文件: %s" % glb_path)
        sys.exit(1)

    glb_name = os.path.basename(glb_path)
    if len(sys.argv) >= 3:
        out_path = sys.argv[2]
    else:
        out_path = os.path.join(os.path.dirname(os.path.abspath(glb_path)),
                                os.path.splitext(glb_name)[0] + "_viewer.html")

    html = HTML_TEMPLATE.format(glb_name=glb_name)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("已生成 viewer: %s" % out_path)
    print("请在该目录下启动本地服务器后访问，例如:")
    print("  cd %s && python -m http.server 18899" % os.path.dirname(os.path.abspath(glb_path)))
    print("  浏览器打开: http://localhost:18899/%s" % os.path.basename(out_path))


if __name__ == "__main__":
    main()
