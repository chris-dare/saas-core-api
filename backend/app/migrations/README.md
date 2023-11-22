Generic single-database configuration with an async dbapi.

Key assumptions:

- Docker-compose service is called `backend`

### How to create a migration

```bash
docker-compose exec backend alembic revision --autogenerate -m "migration_name"
```

### How to apply the migration

```bash
docker-compose exec backend alembic upgrade head
```
