# Authentication System: `POST /auth/login`

Kini nga dokumento nag-explain sa authentication system nga gi-implementar para sa LeafCloud Server V2.

## 1. Overview sa Implementasyon
Gi-implementar nato ang usa ka robust ug secure nga authentication system gamit ang **FastAPI**, **JWT (JSON Web Tokens)**, ug **Bcrypt** para sa password hashing.

### Key Components:
*   **Security**: Gigamit ang `passlib` (bcrypt) para sa hashing ug `python-jose` para sa JWT operations.
*   **Database**: Gigamit ang SQLAlchemy para sa `User` model.
*   **Validation**: Gigamit ang Pydantic (lakip ang `email-validator`) para sa type safety ug validation.
*   **Environment**: Ang mga sensitive data (secrets, admin credentials) gi-manage pinaagi sa `.env` file.

---

## 2. Giunsa kini pag-work? (The Process)

Kung ang usa ka user mo-access sa `/auth/login` endpoint:

1.  **Request Validation**: I-check sa Pydantic kung ang JSON body naay valid nga `email` format ug `password` string.
2.  **User Lookup**: Pangitaon sa database (`users` table) ang user nga naay matching email.
3.  **Password Verification**: 
    *   Kung naay nakit-an nga user, i-compare ang plain-text password gikan sa request ngadto sa `hashed_password` nga naa sa database gamit ang `bcrypt`.
    *   Kung dili match o wala ang user, mo-return og `401 Unauthorized`.
4.  **JWT Generation**: 
    *   Kung successful ang verification, ang server mo-create og JWT access token.
    *   Ang token naay `sub` (subject/email), `user_id`, ug `exp` (expiration time).
5.  **Response**: I-return ang JSON response nga naay status, ang actual token, ug ang basic user info.

---

## 3. Automatic Admin Seeding
Para sa initial setup, naay **startup event** sa `app/main.py`. 

*   Inig sugod sa server, i-check niini kung naa na ba'y admin user sa database.
*   Kung wala pa, automatic kini nga mo-create og admin account base sa `.env` settings:
    *   **Email**: `admin@leafcloud.com`
    *   **Name**: `Super Admin`
    *   **Password**: `admin123`

---

## 4. Unsaon Pag-gamit (How to Use)

### A. Pag-start sa Server
Siguroha nga gamiton ang saktong environment:
```bash
~/.env_leafcloud/bin/uvicorn app.main:app --reload
```

### B. Pag-test sa Login (via cURL)
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "admin@leafcloud.com",
       "password": "admin123"
     }'
```

### C. Sample Response
```json
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiI...",
  "message": "Login successful",
  "user": {
    "id": 1,
    "name": "Super Admin",
    "email": "admin@leafcloud.com"
  }
}
```

---

## 5. Technical Details for Developers

*   **Endpoint**: `POST /auth/login`
*   **Files Involved**:
    *   `app/main.py`: Route handler ug seeding logic.
    *   `app/auth.py`: JWT creation ug password verification logic.
    *   `app/models.py`: Database schema para sa `User`.
    *   `app/schemas.py`: Request (`LoginRequest`) ug Response (`LoginResponse`) schemas.
    *   `app/database.py`: DB engine ug session setup.
*   **Requirements**: Tan-awa ang `requirements.txt` para sa listahan sa dependencies.
