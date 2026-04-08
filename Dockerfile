FROM python:3.11-slim
WORKDIR /app/env
COPY . .
RUN pip install fastapi uvicorn pydantic openenv-core requests openai
EXPOSE 7860
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
