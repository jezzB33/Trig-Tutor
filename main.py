from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import math
from typing import List, Union
from uuid import uuid4
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# Models
# ========================

class EvalRequest(BaseModel):
    x: float

class EvalResponse(BaseModel):
    sinval: float
    cosval: float
    tanval: float
    secval: float
    csecval: float
    alpha_expr: str  # <- expression only, no degrees

class ProblemRequest(BaseModel):
    topic: str
    difficulty: str
    mode: str

class ProblemStep(BaseModel):
    step_id: str
    prompt: str
    expected_type: str
    expression: str
    correct_answer: Union[str, float]

class ProblemResponse(BaseModel):
    problem_id: str
    x: float
    steps: List[ProblemStep]

class ProblemEvalRequest(BaseModel):
    step_id: str
    user_response: Union[str, float]
    correct_answer: Union[str, float]

class ProblemEvalResponse(BaseModel):
    is_correct: bool
    feedback: str

# ========================
# Endpoints
# ========================

@app.post("/evaluate", response_model=EvalResponse)
def evaluate_trig(req: EvalRequest):
    x = req.x
    if not 0 < x < 1:
        raise HTTPException(status_code=400, detail="x must be in (0,1)")

    denom = math.sqrt(1 - 2 * x + 2 * x**2)
    sinval = x / denom
    cosval = (1 - x) / denom
    tanval = x / (1 - x)
    secval = denom / (1 - x)
    csecval = denom / x
    alpha_expr = f"arctan({x} / (1 - {x}))"  # symbolic

    return {
        "sinval": sinval,
        "cosval": cosval,
        "tanval": tanval,
        "secval": secval,
        "csecval": csecval,
        "alpha_expr": alpha_expr
    }

@app.post("/generate-problem", response_model=ProblemResponse)
def generate_problem(req: ProblemRequest):
    x = round(random.uniform(0.2, 0.8), 4)
    problem_id = str(uuid4())

    step_data = [
        {
            "prompt": f"Compute sin(θ) using x = {x}",
            "expression": "x / sqrt(1 - 2x + 2x^2)",
            "answer": round(x / math.sqrt(1 - 2 * x + 2 * x**2), 4),
            "expected_type": "value"
        },
        {
            "prompt": f"Now compute cos(θ) using x = {x}",
            "expression": "(1 - x) / sqrt(1 - 2x + 2x^2)",
            "answer": round((1 - x) / math.sqrt(1 - 2 * x + 2 * x**2), 4),
            "expected_type": "value"
        },
        {
            "prompt": f"Give the algebraic expression for α = arctan(x / (1 - x))",
            "expression": f"arctan({x} / (1 - {x}))",
            "answer": f"arctan({x} / (1 - {x}))",  # symbolic only
            "expected_type": "expression"
        }
    ]

    steps = []
    for i, step in enumerate(step_data):
        step_id = f"step{i+1}"
        if req.mode == "missing-steps" and random.choice([True, False]):
            correct_answer = "??"
        else:
            correct_answer = step["answer"]

        steps.append(ProblemStep(
            step_id=step_id,
            prompt=step["prompt"],
            expected_type=step["expected_type"],
            expression=step["expression"],
            correct_answer=correct_answer
        ))

    return ProblemResponse(problem_id=problem_id, x=x, steps=steps)

@app.post("/evaluate-problem", response_model=ProblemEvalResponse)
def evaluate_problem_step(req: ProblemEvalRequest):
    is_correct = str(req.user_response).strip() == str(req.correct_answer).strip()
    feedback = "Correct!" if is_correct else "Try again — check your simplification or algebra."
    return ProblemEvalResponse(is_correct=is_correct, feedback=feedback)

@app.get("/concept-map")
def get_concept_map():
    return {
        "topics": [
            {
                "id": "sine-from-x",
                "name": "Compute sine using radical unit angle",
                "prerequisites": []
            },
            {
                "id": "derive-ratios",
                "name": "Derive rational cosine and tangent",
                "prerequisites": ["sine-from-x"]
            },
            {
                "id": "inverse-expressions",
                "name": "Construct symbolic inverse expressions",
                "prerequisites": ["derive-ratios"]
            }
        ]
    }
