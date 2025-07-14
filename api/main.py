from fastapi import FastAPI
from .routes import users
from .routes import auth
from .routes import password_reset
from .routes import blog_content

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(blog_content.router)
app.include_router(password_reset.router)