.PHONY: install seed dev backend frontend cli test build clean

VENV := venv/bin

install:
	python3 -m venv venv
	$(VENV)/pip install -r requirements.txt
	cd web && npm install

seed:
	$(VENV)/python -m scripts.seed

dev:
	@echo "Starting backend (:8000) and frontend (:5173). Ctrl+C to stop both."
	@trap 'kill 0' EXIT; \
	$(VENV)/uvicorn app.main:app --reload --port 8000 & \
	(cd web && npm run dev) & \
	wait

backend:
	$(VENV)/uvicorn app.main:app --reload --port 8000

frontend:
	cd web && npm run dev

cli:
	$(VENV)/python main.py

test:
	$(VENV)/python -m pytest tests/ -v
	cd web && npx tsc -b

build:
	cd web && npm run build

clean:
	rm -f jobs.db jobs.db-shm jobs.db-wal
