from ipaddress import ip_address
from contextlib import asynccontextmanager
from pathlib import Path

import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.routes import contacts, auth, users
from src.database.db import get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Підключення до Redis
    """
    The lifespan function is a FastAPI lifecycle hook that runs before the app starts and after it stops.
    
    :param app: FastAPI: Pass the fastapi instance to the function
    :return: A function
    :doc-author: Trelent
    """
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD
    )
    await FastAPILimiter.init(r)
    app.state.redis = r
    
    # Yield управління життєвим циклом
    yield

    # Закриття підключення до Redis
    await r.close()
    app.state.redis = None

# Ініціалізація FastAPI з контекстним менеджером lifespan
app = FastAPI(lifespan=lifespan)

# Додаємо middleware для CORS (як приклад)
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent
directory = BASE_DIR.joinpath("src").joinpath("static")

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")

templates = Jinja2Templates(directory=BASE_DIR/"src"/"templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """
    The index function is responsible for returning the index page of our website.
        It does this by using a TemplateResponse object, which takes in two arguments:
            1) The name of the template to be rendered (in this case, 'index.html')
            2) A context dictionary containing any variables that need to be passed into the template
    
    :param request: Request: Get the request object
    :return: A templateresponse object
    :doc-author: Trelent
    """
    return templates.TemplateResponse('index.html', context={"request": request, "our": "Here was me! Mew was here!"})

@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    The healthchecker function is a simple function that checks if the database connection is working.
    It does this by making a request to the database and checking if it returns any results.
    If there are no results, then we know something went wrong with our connection.
    
    :param db: AsyncSession: Inject the database session into the function
    :return: A dictionary with the message &quot;welcome to fastapi!&quot;
    :doc-author: Trelent
    """
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")