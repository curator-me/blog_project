# 📝 Blog Project

A full-featured blogging platform built with **FastAPI**. This project allows users to create, manage, and interact with blogs — including features like comments, likes, favorites, tags, categories, and user history.

## 🚀 Features

- **User Authentication** (JWT-based)
- **CRUD Operations** for Blogs, Comments, Categories, Tags
- **Like and Comment** on blogs
- **Tag & Categorize** blogs
- **Favorite** blogs
- **User-specific blog history**
- **Search-friendly blog structure**
- Secure password hashing with **bcrypt**
- Full backend API ready for integration with any frontend

---

## 🧰 Tech Stack

- **Python** 3.10+
- **FastAPI** – backend framework
- **SQLite** – default database
- **SQLAlchemy** – ORM
- **bcrypt** – password hashing
- **PyJWT / python-jose** – JWT authentication
- **Pydantic v2** – schema validation

---

## 📦 Installation

1. **Clone the repository**

```bash
git clone https://github.com/curator-me/blog_project.git
cd blog_project
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```
pip install -r requirements.txt
```
4. **Run the server**
```
fastapi dev main.py
```
The API will be live at:
👉 http://127.0.0.1:8000
Interactive docs:
👉 http://127.0.0.1:8000/docs

🤝 Contributing
Contributions are welcome! Feel free to fork the repo and submit a pull request.

🙌 Acknowledgments
Thanks to the FastAPI and SQLAlchemy communities for amazing tools!
