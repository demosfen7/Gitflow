# Gitflow

Учебный проект: минимальный FastAPI-сервис с автодеплоем через GitHub Actions на собственный сервер (Hetzner). Часть песочницы учебных проектов на `vibecoding.aithinglab.com`.

## Что делает приложение

Отдаёт текущее время в UTC в нескольких видах.

**[Открыть интерактивную документацию (Swagger UI)](https://vibecoding.aithinglab.com/gitflow/docs)** — там же можно вызвать любой эндпоинт прямо из браузера.

| Метод | Путь | Ответ |
|---|---|---|
| `GET` | `/` | `{"service": "gitflow", "status": "ok"}` |
| `GET` | `/time` | `{"utc_time": "...", "timestamp": ...}` |
| `GET` | `/date` | `{"date": "...", "year": ..., "month": ..., "day": ...}` |
| `GET` | `/datetime` | `{"datetime": "...", "date": "...", "time": "...", "timestamp": ...}` |
| `GET` | `/timezone/{tz}` | `{"timezone": "...", "datetime": "...", "utc_offset": "..."}` — текущее время в зоне `tz` (IANA-имя), например `/timezone/Europe/Berlin` |
| `GET` | `/convert?time=15:00&tz=Asia/Yekaterinburg` | `{"input_utc_time": "15:00", "timezone": "Asia/Yekaterinburg", "converted_time": "20:00", ...}` — переводит заданное время из UTC в указанный часовой пояс |
| `GET` | `/health` | `{"status": "ok"}` — используется в healthcheck контейнера |

Локально:

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Через Docker:

```bash
docker build -t gitflow .
docker run -p 8000:8000 gitflow
```

## Как устроен деплой

```
push в master
   │
   ▼
GitHub Actions
   ├─ собирает Docker-образ
   ├─ кладёт его на GHCR (ghcr.io/demosfen7/gitflow)
   └─ по SSH заходит на сервер и поднимает контейнер через docker compose
   │
   ▼
https://vibecoding.aithinglab.com/gitflow/time
```

Файлы, отвечающие за деплой:

- **[.github/workflows/deploy.yml](.github/workflows/deploy.yml)** — сборка образа и деплой при пуше в `master`.
- **[deploy/docker-compose.yml](deploy/docker-compose.yml)** — рецепт запуска контейнера на сервере.
- **[deploy/vibecoding.aithinglab.com.caddy](deploy/vibecoding.aithinglab.com.caddy)** — конфиг общего Caddy для пути `/gitflow/*` (файл общий для всех учебных проектов на этом поддомене, CI его не трогает — правки вносятся вручную на сервере).

Сервер обслуживает несколько независимых проектов. Учебные проекты (этот в том числе) деплоятся под отдельным непривилегированным Linux-пользователем со своим изолированным Docker-демоном — без доступа к боевым проектам на той же машине.

## Настройка секретов GitHub Actions

Deploy-workflow подключается к серверу по SSH, поэтому репозиторию нужны четыре секрета: **Settings → Secrets and variables → Actions → New repository secret**.

| Секрет | Значение |
|---|---|
| `SSH_HOST` | IP-адрес сервера |
| `SSH_USER` | Linux-пользователь для деплоя (не боевой аккаунт с sudo!) |
| `SSH_PORT` | Обычно `22` |
| `SSH_KEY` | Приватный SSH-ключ этого пользователя, целиком, включая строки `-----BEGIN...-----` / `-----END...-----` |

Через `gh` CLI (проще, чем руками через веб-интерфейс):

```bash
gh secret set SSH_HOST -R <owner>/<repo> -b "IP-адрес"
gh secret set SSH_USER -R <owner>/<repo> -b "имя-пользователя"
gh secret set SSH_PORT -R <owner>/<repo> -b "22"
gh secret set SSH_KEY  -R <owner>/<repo> < ~/.ssh/приватный_ключ
```

Проверить, какие секреты уже заданы (значения не показываются, только имена и даты):

```bash
gh secret list -R <owner>/<repo>
```

`GITHUB_TOKEN`, использующийся для входа в GHCR, отдельно настраивать не нужно — GitHub создаёт его автоматически для каждого запуска workflow.

### Важно про SSH-ключ

Заведите **отдельный** ключ и пользователя специально под CI, а не тот, которым вы сами ходите на сервер. Если репозиторий или секрет когда-нибудь утекут, ущерб ограничится тем, что видит этот пользователь — а не всем сервером.
