# Incidents API — mini (FastAPI + SQLite)

Минимальная реализация строго по ТЗ (≈30 минут).

## Модель
- `id: int`
- `description: str`
- `status: NEW | IN_PROGRESS | RESOLVED | CLOSED`
- `source: operator | monitoring | partner`
- `created_at: datetime (UTC)`

## Эндпоинты
- `POST /incidents` — создать инцидент (status=NEW по умолчанию)
- `GET  /incidents?status=NEW&limit=50&offset=0` — получить список (фильтр по статусу)
- `PATCH /incidents/{id}/status` — обновить статус по id (если не найден — 404)

## Запуск
```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
# Swagger: http://127.0.0.1:8000/docs
```

## Примеры
```bash
# создать
curl -s -X POST http://127.0.0.1:8000/incidents \\
  -H "Content-Type: application/json" \\
  -d '{"description":"Самокат #42 оффлайн","source":"monitoring"}'

# список (только NEW)
curl -s "http://127.0.0.1:8000/incidents?status=NEW&limit=20&offset=0"

# обновить статус
curl -s -X PATCH http://127.0.0.1:8000/incidents/1/status \\
  -H "Content-Type: application/json" \\
  -d '{"status":"IN_PROGRESS"}'

# не найден
curl -i -s -X PATCH http://127.0.0.1:8000/incidents/999999/status \\
  -H "Content-Type: application/json" \\  -d '{"status":"RESOLVED"}'
```
