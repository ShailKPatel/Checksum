from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from pydantic import BaseModel
from typing import Optional

# Import local modules
from checksum import calculate_checksum, calculate_receiver_checksum

app = FastAPI(title="Checksum Verifier")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# --- Global State (Simulated Wire) ---
class Packet(BaseModel):
    data: str
    sent_checksum_val: int
    sent_checksum_hex: str
    is_active: bool = False

current_packet: Optional[Packet] = None

@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/sender")

@app.get("/sender", response_class=HTMLResponse)
async def sender_page(request: Request):
    return templates.TemplateResponse("sender.html", {
        "request": request,
        "step": "input"
    })

@app.post("/calculate", response_class=HTMLResponse)
async def calculate_step(request: Request, data: str = Form(...)):
    """
    Step 1-4: Checksum Generation
    Takes input, calculates checksum steps in structured format.
    """
    # New return format: (checksum, list_of_step_objects)
    # Each step object: {"title": "Step X", "lines": ["line 1", "line 2"]}
    checksum_val, structured_steps = calculate_checksum(data) 
    checksum_hex = f"{checksum_val:04X}"
    
    return templates.TemplateResponse("sender.html", {
        "request": request,
        "step": "preview",
        "data": data,
        "checksum_val": checksum_val,
        "checksum_hex": checksum_hex,
        "steps_log": structured_steps
    })

@app.post("/send", response_class=HTMLResponse)
async def send_to_wire(
    request: Request, 
    final_data: str = Form(""), 
    final_checksum_hex: str = Form("")
):
    """
    Step 5: Send
    Takes the (potentially edited) data and checksum from the Preview panel.
    """
    global current_packet
    
    try:
        sent_checksum_val = int(final_checksum_hex, 16)
    except ValueError:
        sent_checksum_val = 0
        
    current_packet = Packet(
        data=final_data,
        sent_checksum_val=sent_checksum_val,
        sent_checksum_hex=final_checksum_hex,
        is_active=True
    )
    
    return templates.TemplateResponse("sender.html", {
        "request": request,
        "step": "sent",
        "packet": current_packet
    })

@app.get("/receiver", response_class=HTMLResponse)
async def receiver_page(request: Request):
    global current_packet
    
    context = {
        "request": request,
        "packet": None,
        "verification_log": [],
        "is_valid": False,
        "final_sum_hex": ""
    }
    
    if current_packet and current_packet.is_active:
        is_valid, final_sum, log = calculate_receiver_checksum(
            current_packet.data, 
            current_packet.sent_checksum_val
        )
        
        context["packet"] = current_packet
        context["verification_log"] = log
        context["is_valid"] = is_valid
        context["final_sum_hex"] = f"{final_sum:04X}"
        
    return templates.TemplateResponse("receiver.html", context)

@app.post("/reset")
async def reset():
    global current_packet
    current_packet = None
    return RedirectResponse(url="/sender")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
