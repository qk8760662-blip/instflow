from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict
import httpx

app = FastAPI(title="InstFlow - Angel One Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = "https://apiconnect.angelone.in"
KITE_BASE = "https://api.kite.trade"

class LoginData(BaseModel):
    clientcode: str
    password: str
    totp: str
    apikey: str

class QuoteData(BaseModel):
    token: str
    exchangeTokens: Dict[str, list]
    mode: str = "FULL"

class KiteTokenData(BaseModel):
    api_key: str
    api_secret: str
    request_token: str

@app.get("/", response_class=HTMLResponse)
def root(request_token: str = None, action: str = None, status: str = None):
    if request_token:
        return f"""
        <html><body style="background:#000;color:#00ff00;font-family:monospace;padding:30px;text-align:center">
        <h1 style="color:#ff6600">✅ LOGIN SUCCESSFUL!</h1>
        <h2>Your Request Token:</h2>
        <div style="background:#111;border:2px solid #ff6600;padding:20px;margin:20px;border-radius:8px;font-size:18px;word-break:break-all">
        {request_token}
        </div>
        <p style="color:#aaa">Copy the token above and share it with Claude!</p>
        </body></html>
        """
    return """
    <html><body style="background:#000;color:#00ff00;font-family:monospace;padding:30px;text-align:center">
    <h1 style="color:#ff6600">🏦 InstFlow Live Server</h1>
    <p>Status: Running ✅</p>
    </body></html>
    """

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/login")
async def login(data: LoginData):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-UserType": "USER",
        "X-SourceID": "WEB",
        "X-ClientLocalIP": "127.0.0.1",
        "X-ClientPublicIP": "127.0.0.1",
        "X-MACAddress": "00:00:00:00:00:00",
        "X-PrivateKey": data.apikey
    }
    body = {"clientcode": data.clientcode, "password": data.password, "totp": data.totp}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(f"{BASE}/rest/auth/angelbroking/user/v1/loginByPassword", headers=headers, json=body)
        return resp.json()

@app.post("/quote")
async def quote(data: QuoteData):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {data.token}",
        "X-UserType": "USER",
        "X-SourceID": "WEB",
        "X-ClientLocalIP": "127.0.0.1",
        "X-ClientPublicIP": "127.0.0.1",
        "X-MACAddress": "00:00:00:00:00:00",
    }
    body = {"mode": data.mode, "exchangeTokens": data.exchangeTokens}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(f"{BASE}/rest/secure/angelbroking/market/v1/quote/", headers=headers, json=body)
        return resp.json()

@app.post("/kite/token")
async def kite_token(data: KiteTokenData):
    import hashlib
    checksum = hashlib.sha256(f"{data.api_key}{data.request_token}{data.api_secret}".encode()).hexdigest()
    headers = {
        "X-Kite-Version": "3",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    body = f"api_key={data.api_key}&request_token={data.request_token}&checksum={checksum}"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(f"{KITE_BASE}/session/token", headers=headers, content=body)
        return resp.json()

@app.get("/kite/quote")
async def kite_quote(instruments: str, access_token: str, api_key: str):
    headers = {
        "X-Kite-Version": "3",
        "Authorization": f"token {api_key}:{access_token}"
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{KITE_BASE}/quote?i={instruments}", headers=headers)
        return resp.json()
