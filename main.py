from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import auth, blog, category, user, comment, like, tag
from database import engine
import models




@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(engine)
    print("Application startup")
    yield
    print("Application shutdown")

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(blog.router)
app.include_router(comment.router)
app.include_router(like.router)
app.include_router(category.router)
app.include_router(tag.router)


'''
blog/
│
├── routers/
│   ├── auth.py
│   ├── users.py
│   ├── blogs.py
│   ├── comments.py
│   ├── categories.py
│   └── likes.py
│
├── models/
│   └── user.py, blog.py, etc.
├── schemas/
│   └── user.py, blog.py, etc.
├── database.py
├── jwt_token.py
├── main.py
'''