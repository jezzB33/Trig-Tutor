from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to a specific domain for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EvalRequest(BaseModel):
    x: float

class EvalResponse(BaseModel):
    sinval: float
    cosval: float
    tanval: float
    secval: float
    csecval: float
    alpha_rad: float
    alpha_deg: float

@app.post("/evaluate", response_model=EvalResponse)
def evaluate_trig(req: EvalRequest):
    x = req.x
    if not 0 < x < 1:
        raise HTTPException(status_code=400, detail="x must be in (0,1)")

    denom = math.sqrt(x**2 + (1 - x)**2)
    sinval = x / denom
    cosval = (1 - x) / denom
    tanval = x / (1 - x)
    secval = denom / (1 - x)
    csecval = denom / x
    alpha_rad = math.atan(tanval)
    alpha_deg = math.degrees(alpha_rad)

    return {
        "sinval": sinval,
        "cosval": cosval,
        "tanval": tanval,
        "secval": secval,
        "csecval": csecval,
        "alpha_rad": alpha_rad,
        "alpha_deg": alpha_deg
    }
