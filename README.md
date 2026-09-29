# Burg'ulash va Operatsiyalar Tizimi (Drilling API)

Ushbu loyiha berilgan ma'lumotlar bazasi sxemasi (DBML) asosida **Django**, **Django REST Framework (DRF)** va **PostgreSQL** ma'lumotlar bazasi bilan *Best Practice* qoidalariga rioya qilingan holda yaratilgan.

---

## 🚀 Texnologiyalar va Imkoniyatlar

- **Python & Django**: Zamonaviy arxitektura, `TimeStampedModel` abstrakt bazasi (`created_at`, `updated_at`).
- **PostgreSQL**: `psycopg2-binary` orqali to'liq integratsiya, `.env` orqali ulanish konfiguratsiyasi, persistent connection pooling (`CONN_MAX_AGE`).
- **Docker Compose**: PostgreSQL bazasini 1 ta buyruq bilan ko'tarish imkoniyati (`docker compose up -d`).
- **Django REST Framework**: Barcha jadvallar uchun to'liq CRUD `ModelViewSet` lar.
- **N+1 Query Optimization**: `select_related('region')` va `select_related('position')` orqali ma'lumotlar bazasiga keraksiz so'rovlarni oldini olish.
- **Nested & Dynamic Serializers**:
  - `Area`: O'qishda (`GET`) `region` ma'lumotlarini to'liq nested obyekt sifatida, yozishda (`POST/PUT`) esa `region` ID qabul qiladi.
  - `Employee`: O'qishda `position` obyektini, yozishda ID qabul qiladi.
- **Filtering, Search & Ordering**:
  - `django-filter` orqali har bir model bo'yicha aniq filtrlar (`region_id`, `position_id`, va h.k.).
  - `filters.SearchFilter` orqali nom va telefonlar bo'yicha qidiruv.
  - `filters.OrderingFilter` orqali saralash.
- **Pagination**: Standart `StandardResultsSetPagination` (`page_size=20`, `max_page_size=100`).
- **OpenAPI 3.0 / Swagger**: `drf-spectacular` integratsiyasi (`/api/docs/` va `/api/redoc/`).
- **Django Admin**: Barcha modellar uchun qidiruv va filtrlar bilan sozlangan admin panel.

---

## 📁 Loyiha Strukturasi

```text
ung-drilling-backend/
├── apps/
│   ├── common/
│   │   └── models.py           # TimeStampedModel (abstrakt model)
│   └── directory/
│       ├── admin.py            # Django Admin sozlamalari
│       ├── apps.py
│       ├── filters.py          # Django-filter sinflari
│       ├── migrations/         # Ma'lumotlar bazasi migratsiyalari
│       ├── models.py           # Enterprise, Region, Area, Foreman, Position, Employee, ...
│       ├── serializers.py      # DRF ModelSerializers
│       ├── urls.py             # Router va API endpointlar
│       └── views.py            # ModelViewSets va APIView lar
├── core/
│   ├── pagination.py           # Custom pagination
│   ├── settings.py             # Asosiy sozlamalar (PostgreSQL, DRF, CORS, Swagger)
│   ├── urls.py                 # Asosiy URL marshrutlari (Swagger + API)
│   └── wsgi.py
├── docker-compose.yml          # PostgreSQL konteyneri
├── .env.example                # Muhit o'zgaruvchilari namunasi
├── .env                        # Konfiguratsiya fayli (git-ignore qilingan)
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🛠 O'rnatish va Ishga Tushirish

### 1. Virtual muhitni faollashtirish
```bash
cd /home/bekmuxtorov/projects/ung-drilling-backend
source venv/bin/activate
```

*(Agar noldan o'rnatilayotgan bo'lsa: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`)*

### 2. PostgreSQL bazasini sozlash

#### Variant A: Docker Compose orqali (Tavsiya etiladi)
```bash
docker compose up -d
```

#### Variant B: O'rnatilgan lokal PostgreSQL orqali
PostgreSQL-da yangi baza yarating:
```sql
CREATE DATABASE ung_drilling_db;
```

So'ng `.env` faylida ulanish parametrlarini tekshiring yoki o'zgartiring:
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ung_drilling_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 3. Migratsiyalarni amalga oshirish
```bash
python manage.py migrate
```

### 4. Superuser (admin) yaratish
```bash
python manage.py createsuperuser
```

### 5. Serverni ishga tushirish
```bash
python manage.py runserver
```

---

## 🌐 API Endpointlar Ro'yxati

Asosiy URL prefiksi: `/api/v1/`

| URL Prefiksi | Metodlar | Tavsif |
|---|---|---|
| `/api/v1/enterprises/` | GET, POST | Korxonalar ro'yxati va yaratish |
| `/api/v1/enterprises/{id}/` | GET, PUT, PATCH, DELETE | Korxonani boshqarish |
| `/api/v1/drilling-rig-types/` | GET, POST, ... | Burg'ulash uskunasi turlari |
| `/api/v1/regions/` | GET, POST, ... | Hududlar (viloyatlar) |
| `/api/v1/areas/` | GET, POST, ... | Maydonlar (`?region_id=1` bilan filtrlash mumkin) |
| `/api/v1/foremen/` | GET, POST, ... | Ustalar (Prorablar) |
| `/api/v1/transport-types/` | GET, POST, ... | Transport turlari |
| `/api/v1/positions/` | GET, POST, ... | Lavozimlar |
| `/api/v1/employees/` | GET, POST, ... | Xodimlar (`?position_id=2` bilan filtrlash mumkin) |
| `/api/v1/operation-stages/` | GET | `OperationStageType` enum ro'yxati (demontaj, tashish, montaj) |

### 📚 Hujjatlar (Swagger UI / ReDoc):
- **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **ReDoc UI**: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- **OpenAPI Schema (JSON/YAML)**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)
