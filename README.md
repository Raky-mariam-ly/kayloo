# KAYLOO WEB

## Setup

### 1. Cloner le projet et se deplacer dans le dossier

```bash
git clone https://github.com/groupe-sepro/kayloo_siteweb.git
cd kayloo_siteweb
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

### 6. Vérifier les logs que tout est OK

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
docker exec web alembic upgrade head
```

- Creer la vue **Admin** selon les recommendations **starlette-admin**
  - Creer une vue dans `admin/xxx.py`
  - Importer la vue dans `admin/admin.py`
  - Tester les methodes CRUD

## Entité administrative

### Pays `country`

```sql
table country
{
  id uuid [pk]
  code text [not null, unique]
  name text
  created_at datetime
  created_by text [ref :> user.email]
  updated_at datetime
  updated_by text [ref :> user.email]
}
```

### Ville `city`

```sql
table city
{
  id uuid [pk]
  country text [ref:> country.code]
  code text [not null, unique]
  name text
  created_at datetime
  created_by text [ref :> user.email]
  updated_at datetime
  updated_by text [ref :> user.email]
}
```

### Zone `area`

```sql
table area
{
  id uuid [pk]
  city text [ref:> city.code]
  name text [not null]
  created_at datetime
  created_by text [ref :> user.email]
  updated_at datetime
  updated_by text [ref :> user.email]
}
```

### Agences `agency`

```sql
table agency
{
  id uuid [pk]
  country text [ref:> country.code]
  name text
  email text
  phone_number text
  logo_url text
  siteweb_url text
  whatsapp_url text
  x_url text
  facebook_url text
  tiktok_url text
  youtube_url text
  instragrm_url text
  created_at datetime
  created_by text [ref :> user.email]
  updated_at datetime
  updated_by text [ref :> user.email]
}
```

### Agents `agent`

```sql
table agent
{
  id uuid [pk]
  user_id uuid [ref:> user.id]
  agency_id uuid [ref:> agency.id]
  slug text
  created_at datetime
  created_by text [ref :> user.email]
  updated_at datetime
  updated_by text [ref :> user.email]
}
```

### Partenaires `partner`

```sql
table partner
{
  id uuid [pk]
  country text [ref:> country.code]
  name text [not null, unique]
  email text [not null, unique]
  phone_number text [not null, unique]
  logo_url text
  siteweb_url text
  created_at datetime
  created_by text [ref :> user.email]
  updated_at datetime
  updated_by text [ref :> user.email]
}
```

### Biens `propertry`

```sql
table propertry
{

}
```
