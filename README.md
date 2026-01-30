# NBPRate

**NBPRate** to zaawansowana aplikacja typu *Full-Stack* służąca do pobierania, synchronizacji i wizualizacji kursów walut z API Narodowego Banku Polskiego (NBP). System charakteryzuje się architekturą mikroserwisową, pełną konteneryzacją oraz zoptymalizowanym mechanizmem zarządzania danymi ("Smart Gap Detection").

Aplikacja umożliwia użytkownikom analizę danych historycznych w układzie hierarchicznym (Rok → Kwartał → Miesiąc → Dzień) z wykorzystaniem interfejsu reaktywnego.

---

## Kluczowe Funkcjonalności

* **Smart Gap Detection:** Autorski algorytm backendowy, który inteligentnie wykrywa luki w danych lokalnych. System pobiera z API NBP tylko brakujące zakresy dat, minimalizując ruch sieciowy i ryzyko rate-limitów.
* **Wydajny Cache (Persistent Storage):** Pobrane kursy są trwale zapisywane w bazie PostgreSQL, zapewniając błyskawiczny dostęp przy kolejnych zapytaniach (Warm Cache).
* **Reaktywny Frontend:** Zbudowany w **Angular 19** (Standalone Components), wykorzystujący Reactive Forms oraz RxJS do zarządzania stanem i strumieniami danych.
* **Architektura "Production-Ready":**
    * Backend: Asynchroniczny **FastAPI** z **SQLModel**.
    * Frontend: Serwowany przez lekki serwer **Nginx** (Alpine Linux).
    * Baza Danych: Zoptymalizowany **PostgreSQL 16**.
* **Bezpieczeństwo i Integralność:** Pełna walidacja typów danych (Pydantic/TypeScript), constrainty bazodanowe (`UNIQUE`) oraz izolacja sekretów w plikach `.env`.

---

## Stack Technologiczny

### Backend
* **Język:** Python 3.13+
* **Framework:** FastAPI
* **ORM/Database:** SQLModel (SQLAlchemy Core + Pydantic v2)
* **Driver:** AsyncPG (Asynchroniczny driver PostgreSQL)
* **Migracje:** Alembic
* **Testy:** Pytest (Testy integracyjne i jednostkowe)

### Frontend
* **Framework:** Angular 19
* **Serwer HTTP:** Nginx (w kontenerze produkcyjnym)
* **Stylizacja:** CSS3 / HTML5
* **Architektura:** Container/Presentational Components Pattern

### DevOps & Infrastruktura
* **Konteneryzacja:** Docker & Docker Compose
* **Baza Danych:** PostgreSQL 16
* **Healthchecks:** Automatyczna weryfikacja gotowości usług (`pg_isready`)

---

## Architektura Systemu

Aplikacja składa się z trzech izolowanych usług orkiestrowanych przez Docker Compose:

1.  **`nbp_db` (PostgreSQL 16):**
    * Przechowuje relacyjne dane o walutach i kursach.
    * Wykorzystuje wolumen `postgres_data` do zapewnienia trwałości danych po restarcie kontenerów.
2.  **`nbp_backend` (FastAPI):**
    * Wystawia REST API (OpenAPI/Swagger).
    * Zarządza logiką biznesową i synchronizacją z NBP.
    * Komunikuje się z bazą danych wewnątrz sieci Docker.
3.  **`nbp_frontend` (Angular + Nginx):**
    * Zbudowany w procesie *Multi-stage build*.
    * Nginx serwuje statyczne pliki aplikacji i obsługuje routing.

---

## Uruchomienie Projektu

### Wymagania wstępne
* Docker Desktop (lub Docker Engine + Docker Compose)
* Git

### Instrukcja krok po kroku

1.  **Sklonuj repozytorium:**
    ```bash
    git clone <repository_url>
    cd NBPRate
    ```

2.  **Konfiguracja środowiska:**
    Utwórz plik `.env` w głównym katalogu projektu. Użyj poniższego szablonu (zmień hasło na własne):
    ```env
    POSTGRES_DB=nbp_db
    POSTGRES_USER=nbp_user
    POSTGRES_PASSWORD=twoje_bezpieczne_haslo
    ```

3.  **Uruchomienie aplikacji:**
    Zbuduj i uruchom kontenery w trybie deweloperskim (z podglądem logów):
    ```bash
    docker-compose up --build
    ```
    *Aby uruchomić w tle, dodaj flagę `-d`.*

4.  **Zatrzymanie aplikacji:**
    ```bash
    docker-compose down
    ```

---

## Punkty Dostępu (Access Points)

Po uruchomieniu aplikacja jest dostępna pod następującymi adresami:

| Usługa | Adres URL | Opis |
| :--- | :--- | :--- |
| **Frontend** | `http://localhost:4200` | Główny interfejs użytkownika |
| **API Docs (Swagger)** | `http://localhost:8000/docs` | Interaktywna dokumentacja API |
| **API Docs (ReDoc)** | `http://localhost:8000/redoc` | Alternatywna dokumentacja API |
| **Baza Danych** | `localhost:5432` | Bezpośredni dostęp do PostgreSQL (wymaga klienta SQL) |

---

## Development & Testowanie

### Backend
Uruchomienie testów regresyjnych (Pytest) wewnątrz kontenera:
```bash
docker exec -it nbp_backend pytest -v
```

### Baza danych
Bezpośredni dostęp do powłoki SQL wewnątrz kontenera
```
docker exec -it nbp_db psql -U nbp_user -d nbp_db
```
## Struktura projektu
```
NBPRate/
├── backend/            # Kod źródłowy API (Python/FastAPI)
│   ├── app/            # Logika aplikacji (Modele, Serwisy, Routery)
│   ├── tests/          # Testy jednostkowe i integracyjne
│   └── alembic/        # Migracje bazy danych
├── frontend/           # Kod źródłowy UI (Angular)
│   ├── src/            # Komponenty, Serwisy, Modele
│   └── Dockerfile      # Konfiguracja multi-stage build (Node -> Nginx)
├── docker-compose.yml  # Orkiestracja usług
└── README.md           # Dokumentacja
```