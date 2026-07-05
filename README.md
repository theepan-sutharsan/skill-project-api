# Community Skill-Swap — Backend API

A Flask REST API for a skill-swap platform. Members post skills they can
teach (**offer**) and skills they want to learn (**wanted**); they send
swap requests to each other, the receiver accepts/declines, and an
accepted request can be scheduled into a session.

---

## Tech stack

- Python 3.12+
- Flask 3.x (application factory pattern)
- Flask-SQLAlchemy + SQLAlchemy 2.x
- MySQL via PyMySQL
- Flask-JWT-Extended (Bearer token auth)
- flask-cors

---

## Folder structure

```
api/
├── .env.example
├── requirements.txt
├── run.py
└── app/
    ├── __init__.py          # create_app(), error handlers, blueprint registration
    ├── config.py             # Config class (.env)
    ├── extensions.py         # shared db + jwt instances
    ├── utils.py              # utc_now() helper
    ├── middleware.py         # login_required decorator
    ├── models/
    │   ├── user_model.py
    │   ├── skill_model.py
    │   ├── user_skill_model.py
    │   ├── swap_request_model.py
    │   └── session_model.py
    ├── controllers/
    │   ├── auth_controller.py
    │   ├── user_controller.py
    │   ├── skill_controller.py
    │   ├── user_skill_controller.py
    │   ├── swap_request_controller.py
    │   ├── session_controller.py
    │   └── dashboard_controller.py
    └── routes/
        ├── __init__.py        # register_blueprints(app)
        ├── auth_routes.py
        ├── user_routes.py
        ├── skill_routes.py
        ├── user_skill_routes.py
        ├── swap_request_routes.py
        ├── session_routes.py
        └── dashboard_routes.py
```

---

## Database model

```
users            — registered members (public profile)
skills           — master catalog of skills (name + category)
user_skills      — many-to-many link: a user offers OR wants a skill,
                   at a level (beginner / Intermediate / advanced)
swap_requests    — sender requests a swap with receiver, referencing
                   the two user_skills rows being traded
sessions         — one-to-one with an *accepted* swap_request; holds
                   the agreed date, time, and meeting link
```

**Many-to-many link:** `users` ↔ `skills` is connected through
`user_skills`, which also carries `type` (offer/wanted) and `level`.

**Signature flow:** `swap_requests.offter_skill_id` and
`wanted_skill_id` both point to `user_skills.user_skills_id` (not
directly to `skills`), so each request always carries the exact level
of the skill being exchanged.

---

## Setup

### 1. Create the database

```sql
CREATE DATABASE skill_swap_db;
```

### 2. API setup

```bash
cd api
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows

pip install -r requirements.txt

cp .env.example .env
# edit .env with your DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, JWT_SECRET_KEY

python run.py
```

The API runs at `http://127.0.0.1:5000`. Tables are created automatically
on first run via `db.create_all()`.

---

## API reference

### Auth — `/api/auth`
| Method | Endpoint    | Description                          |
|--------|-------------|---------------------------------------|
| POST   | `/register` | Create account → returns access_token |
| POST   | `/login`    | Login → returns access_token          |

All routes below require header: `Authorization: Bearer <access_token>`

### Users — `/api/users`
| Method | Endpoint        | Description                          |
|--------|------------------|---------------------------------------|
| GET    | `/`              | Browse/search members (`?search=&location=`) |
| GET    | `/me`            | Current logged-in user's profile      |
| GET    | `/<user_id>`     | Get one user's public profile         |
| PUT    | `/<user_id>`     | Update profile                        |
| DELETE | `/<user_id>`     | Delete account                        |

### Skills — `/api/skills`
| Method | Endpoint        | Description                          |
|--------|------------------|---------------------------------------|
| POST   | `/`              | Add a new skill to the master catalog |
| GET    | `/`              | Browse/search skills (`?search=&category=`) |
| GET    | `/<skill_id>`    | Get one skill                         |
| PUT    | `/<skill_id>`    | Update skill                          |
| DELETE | `/<skill_id>`    | Delete skill                          |

### User Skills — `/api/user-skills`  (offer / wanted postings)
| Method | Endpoint              | Description                                          |
|--------|------------------------|-------------------------------------------------------|
| POST   | `/`                    | Post a skill offered or wanted (`type`, `level`)       |
| GET    | `/`                    | Browse/search (`?user_id=&type=&category=&search=`)   |
| GET    | `/<user_skills_id>`    | Get one posting                                       |
| PUT    | `/<user_skills_id>`    | Update posting                                        |
| DELETE | `/<user_skills_id>`    | Remove posting                                        |

### Swap Requests — `/api/swap-requests`
| Method | Endpoint                    | Description                                   |
|--------|------------------------------|-------------------------------------------------|
| POST   | `/`                          | Send a swap request                            |
| GET    | `/`                          | List (`?sender_id=&reciver_id=&status=`)        |
| GET    | `/<request_id>`              | Get one request                                 |
| PUT    | `/<request_id>/status`       | Receiver accepts/declines: `{"status": "accepted"}` |
| DELETE | `/<request_id>`              | Delete request                                  |

### Sessions — `/api/sessions`
| Method | Endpoint           | Description                                            |
|--------|---------------------|-----------------------------------------------------------|
| POST   | `/`                 | Schedule a session for an **accepted** request             |
| GET    | `/`                 | List (`?user_id=&status=`)                                |
| GET    | `/<session_id>`     | Get one session                                            |
| PUT    | `/<session_id>`     | Update date/time/link/status                               |
| DELETE | `/<session_id>`     | Cancel/delete session                                      |

### Dashboard — `/api/dashboard`
| Method | Endpoint        | Description                                                        |
|--------|------------------|----------------------------------------------------------------------|
| GET    | `/<user_id>`     | My offers, my wanted, requests sent, requests received, sessions   |

---

## Demo flow for viva (request → accept → schedule)

1. **Register two users** (`POST /api/auth/register`) — User A and User B.
2. **Post skills**: A posts an `offer` skill (e.g. Guitar); B posts an
   `offer` skill (e.g. Python) — via `POST /api/user-skills`.
3. **A sends a swap request to B**: `POST /api/swap-requests` with
   `sender_id=A`, `reciver_id=B`, `offter_skill_id=<A's Guitar user_skill>`,
   `wanted_skill_id=<B's Python user_skill>`.
4. **B accepts**: `PUT /api/swap-requests/<id>/status` with
   `{"status": "accepted"}` (logged in as B).
5. **Schedule the session**: `POST /api/sessions` with the `request_id`,
   `session_date`, `session_time`.
6. **Check dashboards**: `GET /api/dashboard/<A's id>` and
   `GET /api/dashboard/<B's id>` to show requests sent/received and the
   confirmed session on both sides.
7. To show the many-to-many link in the DB: query `user_skills` and
   point out how the same `skills` row can be attached to many users,
   and the same `users` row can have many `skills` (as both offer and
   wanted).

---

## Notes

- Passwords are hashed with Werkzeug's `generate_password_hash` —
  never stored in plain text.
- All protected routes require a valid JWT in the `Authorization` header.
- Validation errors return `{"errors": [...]}` with HTTP 400.
- Single business-rule errors return `{"error": "..."}` with the
  appropriate status code (401/403/404/500).
