# Time Server API

Простой тестовый бэкенд на FastAPI, который возвращает текущее время сервера и умеет конвертировать время между часовыми поясами.

## Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/` | Приветственное сообщение |
| GET | `/time` | Текущее время по UTC |
| GET | `/date` | Текущая дата по UTC |
| GET | `/datetime` | Текущая дата и время по UTC |
| POST | `/convert` | Конвертация времени в указанный часовой пояс |

## Локальный запуск

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Сборка Docker-образа

```bash
docker build -t time-server .
docker run -d --name time-server -p 8000:8000 time-server
```

## CI/CD (GitHub Actions)

Файл `.github/workflows/deploy.yml` автоматически:

1. Собирает Docker-образ при каждом `push` или `pull_request` в `main`.
2. Публикует образ в **GitHub Container Registry** (`ghcr.io`).
3. При успешной сборке подключается к серверу по SSH и обновляет контейнер.

### Необходимые секреты (Settings → Secrets and variables → Actions)

| Секрет | Описание |
|--------|----------|
| `HOST` | IP-адрес или домен сервера |
| `USERNAME` | Пользователь для SSH (например, `root`) |
| `SSH_KEY` | Приватный SSH-ключ |
| `PORT` | Порт SSH (обычно `22`) |

`GITHUB_TOKEN` предоставляется GitHub автоматически, дополнительно создавать его не нужно.

## Публикация на GitHub

```bash
git init
git add .
git commit -m "Initial commit: FastAPI time server with CI/CD"
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
git push -u origin main
```

После пуша перейди во вкладку **Actions**, чтобы увидеть запущенный workflow.
