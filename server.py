from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os

app = FastAPI()

GUMROAD_ACCESS_TOKEN = os.getenv("GUMROAD_ACCESS_TOKEN")

class LicenseCheck(BaseModel):
    license_key: str

@app.post("/verify")
async def verify_license(data: LicenseCheck):
    if not GUMROAD_ACCESS_TOKEN:
        raise HTTPException(status_code=500, detail="Server not configured")

    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                "https://api.gumroad.com/v2/licenses/verify",
                params={
                    "access_token": GUMROAD_ACCESS_TOKEN,
                    "license_key": data.license_key
                }
            )
            r.raise_for_status()
            result = r.json()
            if result.get("success"):
                if result.get("subscription_cancelled_at") is None and not result.get("refunded"):
                    return {"valid": True, "active": True}
                else:
                    return {"valid": False, "reason": "Subscription cancelled or refunded"}
            else:
                return {"valid": False, "reason": result.get("message", "Invalid license")}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
