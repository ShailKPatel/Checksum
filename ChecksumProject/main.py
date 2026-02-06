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

@app.post("/sender", response_class=HTMLResponse)
async def sender_actions(
    request: Request,
    data: Optional[str] = Form(None),
    final_data: Optional[str] = Form(None),
    final_checksum_hex: Optional[str] = Form(None),
    action: str = Form(...) # 'calculate' or 'send'
):
    """
    Unified Handler for Sender Actions to keep URL at /sender
    """
    global current_packet

    # 1. GENERATE CHECKSUM
    if action == 'calculate':
        payload = data if data else ""
        checksum_val, structured_steps = calculate_checksum(payload) 
        checksum_hex = f"{checksum_val:04X}"
        
        return templates.TemplateResponse("sender.html", {
            "request": request,
            "step": "preview",
            "data": payload,
            "checksum_val": checksum_val,
            "checksum_hex": checksum_hex,
            "steps_log": structured_steps
        })

    # 2. SEND TO WIRE
    elif action == 'send':
        payload = final_data if final_data else ""
        chk_hex = final_checksum_hex if final_checksum_hex else ""
        
        try:
            sent_checksum_val = int(chk_hex, 16)
        except ValueError:
            sent_checksum_val = 0
            
        current_packet = Packet(
            data=payload,
            sent_checksum_val=sent_checksum_val,
            sent_checksum_hex=chk_hex,
            is_active=True
        )
        
        return templates.TemplateResponse("sender.html", {
            "request": request,
            "step": "sent",
            "packet": current_packet,
            "data": "" 
        })
    
    return RedirectResponse(url="/sender", status_code=303)


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


@app.post("/receiver", response_class=HTMLResponse)
async def receiver_actions(request: Request, action: str = Form(...)):
    """
    Unified Handler for Receiver Actions to keep URL at /receiver
    """
    global current_packet
    
    if action == 'clear':
        current_packet = None
        return templates.TemplateResponse("receiver.html", {
            "request": request,
            "packet": None,
            "verification_log": [],
            "is_valid": False,
            "final_sum_hex": ""
        })
        
    return RedirectResponse(url="/receiver", status_code=303)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
