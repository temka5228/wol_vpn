from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from wakeonlan import send_magic_packet
import uvicorn

app = FastAPI(title="WoL Cloud Gateway")

# Модель данных для устройства
class Device(BaseModel):
    id: int
    name: str
    mac: str
    vpn_ip: str  # Внутренний IP роутера в VPN-сети (например, 10.8.0.2)

# Временная база данных (в будущем можно заменить на JSON или SQLite)
devices_db = [
    {"id": 1, "name": "ПК Ивана", "mac": "AA:BB:CC:DD:EE:FF", "vpn_ip": "10.8.0.2"},
    {"id": 2, "name": "Сервер Алексея", "mac": "11:22:33:44:55:66", "vpn_ip": "10.8.0.3"}
]

@app.get("/devices")
async def get_devices():
    """Возвращает список доступных устройств"""
    return devices_db

@app.post("/wake/{device_id}")
async def wake_device(device_id: int):
    """Находит устройство и отправляет WoL пакет через VPN-туннель"""
    device = next((d for d in devices_db if d["id"] == device_id), None)
    
    if not device:
        raise HTTPException(status_code=404, detail="Устройство не найдено")
    
    try:
        # Отправляем Magic Packet на VPN IP роутера (порт 9 UDP)
        # Роутер должен быть настроен на проброс этого порта на локальный Broadcast
        send_magic_packet(device["mac"], ip_address=device["vpn_ip"], port=9)
        return {"status": "success", "message": f"Пакет отправлен на {device['name']}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6767)
