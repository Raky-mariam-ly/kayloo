# KAYLOO WEB

## Setup

### 1. Cloner le projet et se deplacer dans le dossier

```bash
git clone https://github.com/groupe-sepro/kayloo_web.git
cd kayloo_web
```

### 2. Lancer le build docker

S'assurer d'avoir **Docker Desktop** et **Docker compose** installé au préalable.

```bash
docker compose build
```

### 3. Demarrer le projet

```bash
docker compose up -d
```

### 4. Demarrer les migrations existantes

```bash
docker exec web alembic upgrade head
```

### 5. Arreter et redemarrer docker

```bash
docker compose stop && docker compose start
```

### 4. Vérifier les logs que tout est OK

```bash
docker logs  web -f
```

## Developpement

Nouvelle entité pour l'interface **Admin**

- Creér une nouvelle enité dans le dossier `models/xxx.py`
- Importer la nouvelle entité dans `migrations/env.py`
- Lander la migration avec

```bash
docker exec web alembic revision --autogenerate -m "Create new xxxx table"
docker exec web alembic migrate head
```

- Creer la vue **Admin** selon les recommendations **starlette-admin**
  - Creer une vue dans `admin/xxx.py`
  - Importer la vue dans `main.py`
  - Tester les methodes CRUD
