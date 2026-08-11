#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图生3D 直调脚本（纯标准库，无第三方依赖）。
解决两个通用化问题：
  1. Windows 命令行 32KB 长度限制 —— base64 直接放 HTTP body，不走 CLI 参数。
  2. 跨平台可移植 —— 仅用 urllib/stdlib，结果自动下载到本地。
用法:
    python gen3d_direct.py <image_path> <token> [options]

    <token>        通过 connect_cloud_service 获取的临时 token（每次重取，勿硬编码）
    --model 3.0               混元 3D 模型版本（默认 3.0）
    --generate-type LowPoly   生成类型：LowPoly（童趣低面数）| Normal
    --enable-pbr              开启 PBR 材质（默认开）
    --out-dir <dir>           结果下载目录（默认：图片同目录下的 3d_out/）
    --no-download             只输出 JSON（含下载 URL），不下载文件
    --glb-name <name>         本地 glb 文件名（默认：<图片名>_model.glb）

输出（stdout，纯 JSON，便于解析）：
    {"job_id":..., "status":"success",
     "preview_image_url":..., "result_files":[{"type","url","local_path"}...]}
进度/信息一律写 stderr，不污染 stdout。
"""
import base64
import json
import os
import sys
import time
import hashlib
import hmac
import urllib.parse
import urllib.request
from datetime import datetime

# ---------------------------------------------------------------------------
# Constants (与内置技能 3D模型与视频特效 的 buddy-cloud.py 对齐)
# ---------------------------------------------------------------------------
SIGNING_KEY = "codebuddy"
REGION = "ap-guangzhou"

PROVIDER_3D = {
    "provider": "hy-3d",
    "service": "ai3d",
    "version": "2025-05-13",
    "submit_action": "SubmitHunyuanTo3DProJob",
    "query_action": "QueryHunyuanTo3DProJob",
}

TCPROXY_PATH = "/agenttool/v1/tcproxy"
FALLBACK_ENDPOINT = "https://copilot.tencent.com" + TCPROXY_PATH


def resolve_endpoint():
    """优先用运行环境注入的 endpoint，否则回退公共地址。"""
    acc_config = os.environ.get("ACC_PRODUCT_CONFIG_V3", "")
    if acc_config:
        try:
            cfg = json.loads(acc_config)
            ep = cfg.get("endpoint")
            if ep:
                return ep
        except Exception:
            pass
    return FALLBACK_ENDPOINT


def sign_request(secret_id, secret_key, service, action, version,
                 region, host, payload):
    """TCProxy-HMAC-SHA256 签名。"""
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    payload_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    canonical_headers = (
        f"content-type:application/json\n"
        f"host:{host}\n"
        f"x-tc-action:{action.lower()}\n"
        f"x-tc-timestamp:{int(time.time())}\n"
    )
    signed_headers = "content-type;host;x-tc-action;x-tc-timestamp"
    canonical_req = "\n".join([
        "POST", TCPROXY_PATH, "",
        canonical_headers, signed_headers, payload_hash,
    ])

    credential_scope = f"{now[:8]}/{region}/{service}/tc3_request"
    hashed_canonical = hashlib.sha256(canonical_req.encode("utf-8")).hexdigest()
    string_to_sign = "\n".join([
        "TC3-HMAC-SHA256", now, credential_scope, hashed_canonical,
    ])

    def hmac_sha256(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    date_key = hmac_sha256(f"TC3{secret_key}".encode(), now[:8])
    service_key = hmac_sha256(date_key, service)
    signing_key = hmac_sha256(service_key, "tc3_request")
    signature = hmac.new(signing_key, string_to_sign.encode("utf-8"),
                         hashlib.sha256).hexdigest()

    timestamp = str(int(time.time()))
    return {
        "Content-Type": "application/json",
        "X-TC-Action": action,
        "X-Tc-Version": version,
        "X-Tc-Timestamp": timestamp,
        "X-Tc-Region": region,
        "Authorization": (
            f"TC3-HMAC-SHA256 "
            f"Credential={secret_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        ),
    }


def call_api(endpoint, provider, service, version, action, body, token):
    """调用云端 AI 服务（经 tcproxy）。仅用 urllib，无第三方依赖。"""
    secret_id = f"{provider}.{token}"
    parsed = urllib.parse.urlparse(endpoint)
    host = parsed.hostname

    payload = json.dumps(body, ensure_ascii=False)
    headers = sign_request(
        secret_id=secret_id, secret_key=SIGNING_KEY,
        service=service, action=action, version=version,
        region=REGION, host=host, payload=payload,
    )

    req = urllib.request.Request(
        endpoint, data=payload.encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')}")

    if "Response" in result:
        inner = result["Response"]
        if "Error" in inner:
            raise RuntimeError(inner["Error"].get("Message", "Request failed"))
        return inner
    if "error" in result:
        raise RuntimeError(result.get("message", result["error"]))
    return result


def poll_job(endpoint, provider, service, version, query_action,
             job_id, token, poll_interval=5, max_time=600):
    """轮询直到任务完成（最多 10 分钟）。"""
    start = time.time()
    while True:
        elapsed = time.time() - start
        if elapsed > max_time:
            raise TimeoutError(f"Job {job_id} 在 {max_time}s 内未完成")
        result = call_api(endpoint, provider, service, version,
                          query_action, {"JobId": job_id}, token)
        status = result.get("Status", "")
        code = int(result.get("JobStatusCode", 0))
        if status == "DONE" or code == 5:
            return result
        if status == "FAIL" or code == 4:
            raise RuntimeError(result.get("ErrorMessage",
                                 result.get("JobErrorMsg", "生成失败")))
        print(f"[INFO] Job {job_id}: status={status or code}, "
              f"已等待 {int(elapsed)}s，{poll_interval}s 后重试...", file=sys.stderr)
        time.sleep(poll_interval)


def download(url, path):
    """下载模型/预览文件到本地（COS 预签名 URL，直接 GET 即可）。"""
    req = urllib.request.Request(url, headers={"User-Agent": "child-art-skill"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = resp.read()
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <image_path> <token> [options]",
              file=sys.stderr)
        sys.exit(1)

    image_path = sys.argv[1]
    token = sys.argv[2]

    model, gen_type, enable_pbr = "3.0", "LowPoly", True
    out_dir, no_download, glb_name = None, False, None
    args = sys.argv[3:]
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--model":
            model = args[i + 1]; i += 2
        elif a == "--generate-type":
            gen_type = args[i + 1]; i += 2
        elif a == "--enable-pbr":
            enable_pbr = True; i += 1
        elif a == "--out-dir":
            out_dir = args[i + 1]; i += 2
        elif a == "--no-download":
            no_download = True; i += 1
        elif a == "--glb-name":
            glb_name = args[i + 1]; i += 2
        else:
            i += 1

    if not os.path.isfile(image_path):
        print(f"[ERROR] 找不到图片: {image_path}", file=sys.stderr)
        sys.exit(1)

    with open(image_path, "rb") as f:
        img_data = f.read()
    b64 = base64.b64encode(img_data).decode("ascii")
    print(f"[INFO] 图片 {len(img_data)} 字节, base64 {len(b64)} 字符",
          file=sys.stderr)

    body = {"Model": model, "ImageBase64": b64, "GenerateType": gen_type}
    if enable_pbr:
        body["EnablePBR"] = True

    endpoint = resolve_endpoint()
    cfg = PROVIDER_3D
    print("[INFO] 提交 3D 生成任务...", file=sys.stderr)
    submit = call_api(endpoint, cfg["provider"], cfg["service"], cfg["version"],
                      cfg["submit_action"], body, token)
    job_id = submit.get("JobId")
    if not job_id:
        print(json.dumps(submit, indent=2, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
    print(f"[INFO] 任务已提交: {job_id}", file=sys.stderr)

    result = poll_job(endpoint, cfg["provider"], cfg["service"], cfg["version"],
                      cfg["query_action"], job_id, token)

    output = {"job_id": job_id, "status": "success", "result_files": []}
    if "PreviewImageUrl" in result:
        output["preview_image_url"] = result["PreviewImageUrl"]

    # 收集可下载文件
    file_specs = []
    for field, ftype, ext in (("ModelUrl", "glb", ".glb"),
                              ("ResultModelUrl", "glb", ".glb"),
                              ("ResultUrl", "obj", ".obj")):
        if field in result and result[field]:
            file_specs.append((result[field], ftype, ext))
    if "PreviewImageUrl" in result:
        file_specs.append((result["PreviewImageUrl"], "preview", ".png"))

    if no_download:
        for url, ftype, ext in file_specs:
            output["result_files"].append({"type": ftype, "url": url})
    else:
        if out_dir is None:
            out_dir = os.path.join(os.path.dirname(os.path.abspath(image_path)),
                                   "3d_out")
        os.makedirs(out_dir, exist_ok=True)
        stem = os.path.splitext(os.path.basename(image_path))[0]
        for idx, (url, ftype, ext) in enumerate(file_specs):
            if ftype == "glb" and glb_name:
                fname = glb_name
            elif ftype == "glb":
                fname = f"{stem}_model{ext}"
            elif ftype == "obj":
                fname = f"{stem}_model{ext}"
            elif ftype == "preview":
                fname = f"{stem}_preview{ext}"
            else:
                fname = f"{stem}_{idx}{ext}"
            local = os.path.join(out_dir, fname)
            try:
                size = download(url, local)
                print(f"[INFO] 已下载 {ftype}: {local} ({size} 字节)",
                      file=sys.stderr)
                output["result_files"].append(
                    {"type": ftype, "url": url, "local_path": local})
            except Exception as e:
                print(f"[WARN] 下载 {ftype} 失败: {e}", file=sys.stderr)
                output["result_files"].append({"type": ftype, "url": url})

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
