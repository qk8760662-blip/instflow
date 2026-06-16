InstFlow Live Server</h1>
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
