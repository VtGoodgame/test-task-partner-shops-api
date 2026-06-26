import uvicorn
from db import database
from src.const import DB_PATH
from fastapi import FastAPI, Depends, HTTPException, status
from datetime import datetime

DB = database.Database(str(DB_PATH))

app = FastAPI(
    title="Shop API",
    description="API для отображения данных о магазинах партнерах",
    version="1.0.0"
)

@app.get(
    "/api/v1/shops/with-delivery-by-hour",
    status_code=status.HTTP_200_OK,
    summary="Получить магазины с доставкой по указанному часу"
)
async def get_stores_by_hour(hour: int):
    """
    Получение магазинов с ближайшей доставкой к указанному часу
    """
    # Создаем время с указанным часом
    current_time = datetime.now().replace(hour=hour, minute=0, second=0)
    shops = await DB.get_stores_with_nearest_delivery_by_hour(current_time)
    
    if not shops:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активные магазины не найдены"
        )
    
    return shops

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="localhost",
        port=8000,       
        reload=False,
        log_level="info"
    )