# Burg'ulash va Operatsiyalar Tizimi (UNG Drilling API)

Ushbu loyiha berilgan ma'lumotlar bazasi sxemasi (DBML) asosida **Django**, **Django REST Framework (DRF)** va **PostgreSQL** ma'lumotlar bazasi bilan *Best Practice* qoidalariga rioya qilingan holda yaratilgan.

---

## 🚀 Modullar va Imkoniyatlar

### 1. Ma'lumotnomalar (Directory App)
- **Korxonalar (`Enterprise`)**
- **Burg'ulash qurilmalari turlari (`DrillingRigType`)**
- **Hududlar / Viloyatlar (`Region`)**
- **Maydonlar / Konlar (`Area`)**
- **Ustalar / Prorablar (`Foreman`)**
- **Transport vositalari turlari (`TransportType`)**
- **Lavozimlar (`Position`)**
- **Xodimlar (`Employee`)**

### 2. VBM va Quduq Qurilishi Operatsiyalari (Operations App)
- **VBM Operatsiyalari (`DerrickErectionOperation`)**: Burg'ulash uskunasini bir maydondan ikkinchisiga ko'chirish, masofa, reja kunlar, bajarilish foizi va kechikish sabablari.
- **Operatsiya bosqichlari (`OperationStage`)**: Demontaj, Tashish, Montaj bosqichlari (reja va amaldagi kunlar, sanalar).
- **Kunlik ish tavsifi (`DailyWorkDescription`)**: Har kunlik operatsiya bo'yicha bajarilgan ishlar hisoboti.
- **Kunlik transport vositalari (`DailyTransportItem`)**: Kunlik hisobotga biriktirilgan transport turlari va ularning soni.

---

## 📁 Loyiha Strukturasi

```text
ung-drilling-backend/
├── apps/
│   ├── common/                 # TimeStampedModel (abstrakt model)
│   ├── directory/              # Ma'lumotnomalar (Enterprise, Rig, Area, Employee...)
│   └── operations/             # VBM Operatsiyalari, Bosqichlar, Kunlik hisobotlar
├── core/
│   ├── pagination.py           # Standart paginatsiya
│   ├── settings.py             # PostgreSQL, DRF, CORS, Swagger sozlamalari
│   ├── urls.py                 # Asosiy URL marshrutlari
│   └── wsgi.py / asgi.py
├── docker-compose.yml          # PostgreSQL konteyneri
├── .env.example / .env         # Muhit o'zgaruvchilari
├── manage.py
└── requirements.txt
```

---

## 🌐 API Endpointlar Ro'yxati (`/api/v1/`)

### VBM Operatsiyalari:
| URL | Metod | Tavsif |
|---|---|---|
| `/api/v1/derrick-erection-operations/` | GET, POST | VBM operatsiyalari ro'yxati va yangi yaratish |
| `/api/v1/derrick-erection-operations/{id}/` | GET, PUT, PATCH, DELETE | Operatsiyani boshqarish |
| `/api/v1/derrick-erection-operations/{id}/daily-reports/` | GET | Operatsiyaga tegishli kunlik hisobotlar |
| `/api/v1/operation-stages/` | GET, POST, PUT, DELETE | Demontaj, Tashish, Montaj bosqichlari |
| `/api/v1/daily-works/` | GET, POST, PUT, DELETE | Kunlik ish hisobotlari |
| `/api/v1/daily-transports/` | GET, POST, PUT, DELETE | Kunlik hisobotga transport biriktirish |

### Ma'lumotnomalar:
| URL | Metod | Tavsif |
|---|---|---|
| `/api/v1/enterprises/` | GET, POST | Korxonalar |
| `/api/v1/drilling-rig-types/` | GET, POST | Burg'ulash uskunasi turlari |
| `/api/v1/regions/` | GET, POST | Hududlar (viloyatlar) |
| `/api/v1/areas/` | GET, POST | Maydonlar (`?region_id=1` bilan filtrlash) |
| `/api/v1/foremen/` | GET, POST | Ustalar |
| `/api/v1/transport-types/` | GET, POST | Transport turlari |
| `/api/v1/positions/` | GET, POST | Lavozimlar |
| `/api/v1/employees/` | GET, POST | Xodimlar (`?position_id=2` bilan filtrlash) |
| `/api/v1/operation-stages/` | GET | `OperationStageType` enum ro'yxati |

---

## 📚 Hujjatlar:
- **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **ReDoc UI**: [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
- **Admin Panel**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
