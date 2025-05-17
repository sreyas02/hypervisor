# MLOps Platform - Hypervisor Service

A backend service for managing user authentication, organization membership, cluster resource allocation, and deployment scheduling in an MLOps platform.

## Features

- User Authentication and Organization Management
- Cluster Resource Management
- Deployment Scheduling with Priority-based Preemption
- Resource Utilization Optimization
- Queue Management for Deployments

## Tech Stack

- Python 3.9+
- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy
- Pydantic
- Alembic (for database migrations)

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
alembic upgrade head
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests using pytest:
```bash
pytest
```

## Project Structure

```
.
├── alembic/              # Database migrations
├── app/
│   ├── api/             # API routes
│   ├── core/            # Core functionality
│   ├── db/              # Database models and session
│   ├── schemas/         # Pydantic models
│   └── services/        # Business logic
├── tests/               # Test files
├── .env                 # Environment variables
├── .env.example         # Example environment variables
├── alembic.ini          # Alembic configuration
├── requirements.txt     # Project dependencies
└── README.md           # Project documentation
```

## Database Schema

The database schema includes the following main entities:
- Users
- Organizations
- Clusters
- Deployments
- Resource Allocations

See the UML diagram in `docs/database_schema.png` for detailed relationships.

## License

MIT 