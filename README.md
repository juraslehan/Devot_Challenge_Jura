# Home Budget API (FastAPI)

## Quick Start
```bash
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload

docs live at: http://127.0.0.1:8000/docs

Auth flow
1) POST /auth/register -> create account
2) POST /auth/login -> get JWT (access_token)
3) Click Authorize in Swagger and paste Bearer <token>
4) GET /auth/me -> verify

Endpoints
Auth: /auth/register, /auth/login, /auth/me
Categories: POST /categories, GET /categories, PUT /categories/{id}, DELETE /categories/{id}
Expenses: POST /expenses, GET /expenses, GET /expenses/{id}, PUT /expenses/{id}, DELETE /expenses/{id}
    Filters on GET /expenses: categoryId, amount_min, amount_max, date_from, date_to, q
Reports: GET /reports/balance, GET /reports/summary?period=month|quarter|year&year=YYYY[&month|quarter]