from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from pathlib import Path

app = FastAPI(title="Modern Calculator")

# Get the directory where this file is located
base_dir = Path(__file__).parent


class CalculationRequest(BaseModel):
    expression: str


class CalculationResult(BaseModel):
    expression: str
    result: float


@app.post("/api/calc")
def calculate(request: CalculationRequest):
    """
    Calculate a mathematical expression and return the result as JSON.
    Supports basic arithmetic operations: +, -, *, /, %, **
    """
    try:
        # Convert Unicode operators to ASCII
        expression = request.expression
        expression = expression.replace("×", "*")  # Unicode multiplication
        expression = expression.replace("−", "-")  # Unicode minus
        expression = expression.replace(" ", "")   # Remove spaces

        # Sanitize and validate the expression
        allowed_chars = set("0123456789+-*/.%()")
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Invalid characters in expression")

        # Prevent empty expression
        if not expression:
            raise ValueError("Empty expression")

        # Evaluate the expression
        result = eval(expression)

        # Ensure result is a number
        if isinstance(result, bool):
            raise ValueError("Invalid expression")

        return CalculationResult(expression=request.expression, result=float(result))

    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Division by zero")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid expression: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")


# Mount static files directory AFTER defining routes
static_dir = base_dir / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
