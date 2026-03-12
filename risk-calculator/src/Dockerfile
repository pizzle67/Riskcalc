FROM docker.artifactory.rbx.com/rbx-docker-base-images/python-3.10-dev:latest AS builder

WORKDIR /risk-calculator

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"

RUN python -m venv /venv

COPY services/risk-calculator/src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM docker.artifactory.rbx.com/rbx-docker-base-images/python-3.10:latest

WORKDIR /risk-calculator

ENV PYTHONUNBUFFERED=1
ENV PATH="/venv/bin:$PATH"
ENV PYTHONPATH="${PYTHONPATH}:/risk-calculator"

ENV APP_NAME="risk-calculator"
ARG git_commit_sha="local"
ENV GIT_COMMIT=$git_commit_sha
LABEL GIT_COMMIT=$git_commit_sha

COPY ./services/risk-calculator .
COPY --from=builder /venv /venv

EXPOSE 5000

ENTRYPOINT [ "gunicorn" ]
CMD [ "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "--preload", "webapp.app:app" ]
