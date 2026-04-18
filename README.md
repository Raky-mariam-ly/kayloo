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

### Tags `tags`

```sql
table tag
{
  id uuid [pk]
  name text [not null, unique]
  slug text [not null, unique]
  created_at datetime
  created_by text [ref :> user.email]
  updated_at datetime
  updated_by text [ref :> user.email]
}
```

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

### Immeuble `building`

```sql
table building
{
  id uuid [pk]
  agency_id uuid [ref:> agency.id]
  city_id uuid [ref:> agency.id]
  name text [not null]
  address text
  lat decimal
  lng decimal
  slug text
  image_url text
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
  id uuid [pk]
  building_id uuid [ref:> building.id]
  agency_id uuid [ref:> agency_id]
  label text
  code text
  status_before_reserved text
  managed_by text
  base_price_type text
  description text
  usage text
  type text
  status text
  rent_type text
  rental_period text
  image_url text
  level text
  position text
  apartment_number text
  country text [ref:> country.code]
  city text
  zone text
  street text
  address text
  bath_room_count int
  bed_room_count int
  kitchen_count int
  living_room_count int
  build_year text
  lng decimal
  lat decimal
  acquisition_date date
  acquisition_price decimal
  acquisition_fee decimal
  surface decimal
  free_since date
  currency text
  vat_rate decimal
  tom_rate decimal
  ir_rate decimal
  mgmt_rate decimal
  commission_rate decimal
  deposit_rate decimal
  sale_price decimal
  price decimal
  base_price decimal
  extra_price decimal
  rent_price decimal
  syndic_amount decimal
  is_hidden boolean default false
  is_exposed boolean default false
  is_saleable boolean default true
  is_managed boolean default false
  archived boolean default false
  is_featured boolean
  created_at datetime
  created_by text [ref :> user.email]
  updated_at datetime
  updated_by text [ref :> user.email]
}
```

### Photos de biens `property_image`

```sql
table propertry_image
{
  id uuid [pk]
  property_id uuid [ref:> property.id]
  url text
  created_at datetime
  created_by text [ref :> user.email]
  updated_at datetime
  updated_by text [ref :> user.email]
}
```
