from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

class LoginData(BaseModel):
    clientcode: str
    password: str
    totp: str
    apikey: str

class QuoteData(BaseModel):
    token: str
    exchangeTokens: Dict[str, list]
    mode: str = "FULL"

@app.get("/")
def root():
    return {"status": "InstFlow Live Server Running ✅"}

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
    body = {
        "clientcode": data.clientcode,
        "password": data.password,
        "totp": data.totp
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            f"{BASE}/rest/auth/angelbroking/user/v1/loginByPassword",
            headers=headers, json=body)
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
        resp = await client.post(
            f"{BASE}/rest/secure/angelbroking/market/v1/quote/",
            headers=headers, json=body)
        return resp.json()
