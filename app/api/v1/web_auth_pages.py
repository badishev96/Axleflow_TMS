from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from app.db.session import get_db
from app.models.user import User

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return HTMLResponse("""
    <html>
    <head>
      <title>AxleFlow Login</title>
      <style>
        body { font-family: Arial, sans-serif; background:#fafafa; margin:0; }
        .wrap { max-width:420px; margin:80px auto; background:#fff; border:1px solid #e6e6e6; border-radius:14px; padding:18px; }
        label { display:block; margin-top:12px; color:#444; font-size:12px; }
        input { width:100%; padding:10px; border:1px solid #ddd; border-radius:10px; margin-top:6px; }
        button { margin-top:14px; width:100%; padding:10px; border:0; border-radius:12px; background:#111; color:#fff; cursor:pointer; }
        .muted { color:#666; font-size:12px; margin-top:10px; }
      </style>
    </head>
    <body>
      <div class="wrap">
        <h2 style="margin:0;">AxleFlow TMS</h2>
        <div class="muted">Login</div>

        <form method="post" action="/login">
          <label>Email</label>
          <input name="email" type="email" required />

          <label>Password</label>
          <input name="password" type="password" required />

          <button type="submit">Log in</button>
        </form>

        <div class="muted">
          If you don’t know your credentials yet, create a user in Swagger once. After that, use this page.
        </div>
      </div>
    </body>
    </html>
    """)

@router.post("/login")
async def login_action(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    email = str(form.get("email", "")).strip().lower()
    password = str(form.get("password", ""))

    user = db.query(User).filter(User.email == email).first()
    if not user or not bcrypt.verify(password, user.hashed_password):
        return HTMLResponse("""
        <html><body style="font-family:Arial;margin:40px;">
          <h3>Login failed</h3>
          <p>Invalid credentials.</p>
          <p><a href="/login">Try again</a></p>
        </body></html>
        """, status_code=401)

    request.session["user_id"] = user.id
    request.session["company_id"] = user.company_id
    request.session["role"] = user.role

    return RedirectResponse(url="/app", status_code=303)

@router.post("/logout")
def logout_action(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
