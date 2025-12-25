from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
import re
import os
import json
import httpx  # Measurement Protocolのリクエスト送信のために追加
import asyncio  # 非同期タスクのために追加
from fastapi.staticfiles import StaticFiles  # StaticFilesをインポート
import logging
import time
import hashlib

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 設定ファイルのパス
REDIRECT_CONFIG_FILE = os.getenv("REDIRECT_CONFIG_FILE", "redirect_config.json")

# Google Analytics の設定
GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID")
GA_API_SECRET = os.getenv("GA_API_SECRET")

if not GA_MEASUREMENT_ID or not GA_API_SECRET:
    logger.warning("GA_MEASUREMENT_ID or GA_API_SECRET is not set. Google Analytics events will not be sent.")
    logger.warning(f"GA_MEASUREMENT_ID: {'Set' if GA_MEASUREMENT_ID else 'Not Set'}")
    logger.warning(f"GA_API_SECRET: {'Set' if GA_API_SECRET else 'Not Set'}")


# 静的ファイルを提供するためのディレクトリをマウント
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    return RedirectResponse(url="/static/favicon.ico")

# Measurement Protocol イベント送信ヘルパー関数
async def send_ga_event(client_id: str, session_id: int, event_name: str, event_params: dict, ip_override: str | None = None):
    if not GA_MEASUREMENT_ID or not GA_API_SECRET:
        return

    url = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={GA_API_SECRET}"

    event_params.update({
        "session_id": session_id,
        "engagement_time_msec": 1, # ユーザーがリダイレクトページにエンゲージしたとみなす
    })

    payload = {
        "client_id": client_id,
        "events": [{
            "name": event_name,
            "params": event_params
        }]
    }

    if ip_override:
        payload["ip_override"] = ip_override  # ←トップレベルが正しい :contentReference[oaicite:3]{index=3}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=5)
            response.raise_for_status()
            logger.info(f"Google Analytics event '{event_name}' sent successfully for client_id: {client_id}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Error sending GA event (HTTP status {e.response.status_code}): {e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Error sending GA event (network/request error): {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred while sending GA event: {e}")

def get_device_type(user_agent: str) -> str:
    if re.search(r"Android", user_agent, re.IGNORECASE):
        return "android"
    elif re.search(r"iPhone|iPad|iPod", user_agent, re.IGNORECASE):
        return "ios"
    return "pc"

def get_client_ip(request: Request) -> str:
    """リクエストからクライアントのIPアドレスを取得する。X-Forwarded-Forを考慮する。"""
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        # X-Forwarded-Forヘッダーは "client, proxy1, proxy2" の形式なので、最初のIPアドレスを取得
        return x_forwarded_for.split(',')[0].strip()
    return request.client.host

@app.get("/{redirect_group:path}")
@app.post("/{redirect_group:path}")
async def dynamic_redirect(redirect_group: str, request: Request):
    try:
        with open(os.path.join(os.path.dirname(__file__), REDIRECT_CONFIG_FILE), "r", encoding="utf-8") as f:
            current_redirect_config = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"Redirect configuration file '{REDIRECT_CONFIG_FILE}' not found.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Could not decode JSON from '{REDIRECT_CONFIG_FILE}'")

    redirect_group = redirect_group or "root"
    requested_group = redirect_group
    event_params = {}
    event_name = "redirect_event"

    if redirect_group not in current_redirect_config:
        logger.warning(f"Unknown redirect_group='{redirect_group}'. Fallback to 'root'.")
        event_params["requested_group"] = requested_group
        event_name = "redirect_event_not_found"

        redirect_group = "root"

    if redirect_group not in current_redirect_config:
        raise HTTPException(status_code=500, detail="Fallback redirect group 'root' not found.")

    user_agent = request.headers.get("User-Agent", "")
    device_type = get_device_type(user_agent)

    destination_url = current_redirect_config[redirect_group].get(device_type) or current_redirect_config[redirect_group].get("pc")

    if not destination_url:
        raise HTTPException(status_code=500, detail=f"No redirect URL configured for group '{redirect_group}'")

    # --- Google Analytics イベント送信 ---
    if GA_MEASUREMENT_ID and GA_API_SECRET:
        client_ip = get_client_ip(request)

        # IPとUserAgentから安定したIDを生成
        # これにより、同じユーザーからのリクエストをある程度特定できる
        user_hash = hashlib.sha256((client_ip + user_agent).encode()).hexdigest()
        client_id = f"server-side.{user_hash}"

        # セッションIDを生成（ここではリクエストごとにユニークなセッションとしているが、
        # より高度なセッション管理も可能）
        session_id = int(time.time())

        event_params["redirect_group"] = redirect_group
        event_params["device_type"] = device_type
        event_params["user_agent"] = user_agent
        event_params["destination_url"] = destination_url
        event_params["page_location"] = str(request.url)
        event_params["page_path"] = request.url.path
        event_params["ip_override"] = client_ip # IPアドレスをGAに送信

        asyncio.create_task(send_ga_event(client_id, session_id, event_name, event_params, ip_override=client_ip))

    return RedirectResponse(url=destination_url)
