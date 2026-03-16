FROM python:3.10-slim AS builder

WORKDIR /risk-calculator

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"

RUN python -m venv /venv

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.10-slim

WORKDIR /risk-calculator

ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"
ENV PYTHONPATH="${PYTHONPATH}:/risk-calculator"

ENV APP_NAME="risk-calculator"
ARG git_commit_sha="local"
ENV GIT_COMMIT=$git_commit_sha
LABEL GIT_COMMIT=$git_commit_sha

COPY --from=builder /venv /venv

COPY fair_monte_carlo ./fair_monte_carlo
COPY webapp ./webapp
COPY src ./src

EXPOSE 5000

ENTRYPOINT ["gunicorn"]
CMD ["--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "--preload", "webapp.app:app"]
