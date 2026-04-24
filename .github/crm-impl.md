# CRM Implementation — Kayloo SiteWeb

Documentation de l'implémentation complète du CRM pour la plateforme immobilière Kayloo.

---

## 1. Architecture générale

Le CRM suit l'architecture 4 couches du projet :

```
Model (SQLAlchemy) → Repository → Service → Route API / Admin View
```

- **Base de données** : PostgreSQL (async via SQLAlchemy + asyncpg)
- **API** : FastAPI sous `/api/v1/`
- **Admin** : starlette-admin 0.16.0 + Tabler UI 1.1.0
- **Auth** : Dual — Cookie JWT (admin web) + Bearer JWT (mobile API)

---

## 2. Modèles de données

### 2.1 Contact

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `user_id` | UUID (FK → user) | Lien optionnel vers un compte utilisateur |
| `first_name` | Text | Prénom |
| `last_name` | Text | Nom |
| `email` | Text | Email (indexé) |
| `phone_number` | Text | Téléphone |
| `country` | Text (FK → country.code) | Pays |
| `city` | Text (FK → city.code) | Ville |
| `address` | Text | Adresse |
| `contact_type` | Text | buyer, seller, tenant, landlord, investor |
| `notes` | Text | Notes libres |
| `is_active` | Boolean | Actif/Inactif |
| `created_at/updated_at` | DateTime | Audit |
| `created_by/updated_by` | Text (FK → user.email) | Audit utilisateur |

**Fichier** : `app/models/contact.py`

### 2.2 Lead

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `contact_id` | UUID (FK → contact) | Contact associé |
| `property_id` | UUID (FK → property) | Bien immobilier (optionnel) |
| `agent_id` | UUID (FK → agent) | Agent assigné |
| `agency_id` | UUID (FK → agency) | Agence |
| `source` | Text | website, mobile_app, phone, walk_in, referral, social_media |
| `status` | Text | Pipeline : new → contacted → qualified → negotiation → won/lost |
| `priority` | Text | low, medium, high, urgent |
| `probability` | Integer | 0-100% — auto-mis à jour lors des transitions |
| `expected_close` | Date | Date de clôture estimée |
| `deal_value` | Numeric(15,2) | Valeur négociée (override du prix du bien) |
| `lost_reason` | Text | Raison de la perte |
| `notes` | Text | Notes libres |
| `created_at/updated_at` | DateTime | Audit |
| `created_by/updated_by` | Text (FK → user.email) | Audit utilisateur |

**Fichier** : `app/models/lead.py`

#### Pipeline & transitions valides

```
new → contacted → qualified → negotiation → won
                                           → lost
lost → new (réouverture)
```

#### Probabilité automatique par statut

| Statut | Probabilité |
|--------|-------------|
| new | 10% |
| contacted | 25% |
| qualified | 50% |
| negotiation | 75% |
| won | 100% |
| lost | 0% |

### 2.3 Activity

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `lead_id` | UUID (FK → lead) | Lead associé |
| `contact_id` | UUID (FK → contact) | Contact associé |
| `user_id` | UUID (FK → user) | Utilisateur auteur |
| `activity_type` | Text | call, email, meeting, note, visit, status_change, assignment |
| `subject` | Text | Sujet |
| `description` | Text | Détail |
| `metadata_` | JSON | Données complémentaires (mappé sur colonne `metadata`) |
| `created_at` | DateTime | Date de l'activité |

**Fichier** : `app/models/activity.py`

> Note : `metadata_` avec underscore pour éviter le conflit avec `SQLAlchemy.MetaData`.

### 2.4 Task

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `lead_id` | UUID (FK → lead) | Lead associé (optionnel) |
| `contact_id` | UUID (FK → contact) | Contact associé (optionnel) |
| `assigned_to` | UUID (FK → user) | Utilisateur assigné |
| `title` | Text | Titre |
| `description` | Text | Description |
| `task_type` | Text | follow_up, call, email, meeting, visit, other |
| `status` | Text | pending, in_progress, completed, cancelled |
| `priority` | Text | low, medium, high, urgent |
| `due_date` | DateTime | Échéance |
| `completed_at` | DateTime | Date de complétion |
| `created_at/updated_at` | DateTime | Audit |

**Fichier** : `app/models/task.py`

### 2.5 Notification

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `user_id` | UUID (FK → user) | Destinataire |
| `title` | Text | Titre |
| `message` | Text | Message |
| `notification_type` | Text | lead_assigned, lead_won, task_due, message, system |
| `reference_id` | UUID | ID de l'objet référencé |
| `reference_type` | Text | lead, task, conversation |
| `is_read` | Boolean | Lu/Non lu |
| `created_at` | DateTime | Date de création |

**Fichier** : `app/models/notification.py`

### 2.6 Favorite

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `user_id` | UUID (FK → user) | Utilisateur |
| `property_id` | UUID (FK → property) | Bien favori |
| `created_at` | DateTime | Date d'ajout |

**Fichier** : `app/models/favorite.py`

### 2.7 SavedSearch

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `user_id` | UUID (FK → user) | Utilisateur |
| `name` | Text | Nom de la recherche |
| `filters` | JSON | Critères de recherche |
| `notify` | Boolean | Recevoir des alertes |
| `created_at/updated_at` | DateTime | Audit |

**Fichier** : `app/models/saved_search.py`

### 2.8 Conversation & Message

**Conversation** :

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `subject` | Text | Sujet |
| `property_id` | UUID (FK → property) | Bien associé (optionnel) |
| `lead_id` | UUID (FK → lead) | Lead associé (optionnel) |
| `is_archived` | Boolean | Archivée |
| `created_at/updated_at` | DateTime | Audit |

**ConversationParticipant** : table de liaison `(conversation_id, user_id)` + `joined_at`

**Message** :

| Champ | Type | Description |
|-------|------|-------------|
| `id` | UUID | PK |
| `conversation_id` | UUID (FK → conversation) | Conversation |
| `sender_id` | UUID (FK → user) | Expéditeur |
| `content` | Text | Contenu |
| `is_read` | Boolean | Lu |
| `created_at` | DateTime | Date |

**Fichiers** : `app/models/conversation.py`, `app/models/message.py`

---

## 3. API REST — Endpoints

Tous les endpoints CRM sont sous `/api/v1/` et protégés par `current_active_user` (cookie ou bearer JWT).

### 3.1 Contacts (`/api/v1/contacts`)

| Méthode | Path | Description |
|---------|------|-------------|
| GET | `/` | Liste paginée |
| GET | `/{id}` | Détail |
| POST | `/` | Créer |
| PUT | `/{id}` | Modifier |
| DELETE | `/{id}` | Supprimer |

### 3.2 Leads (`/api/v1/leads`)

| Méthode | Path | Description |
|---------|------|-------------|
| GET | `/` | Liste (filtrable par status, agent, agency) |
| GET | `/{id}` | Détail |
| POST | `/` | Créer |
| PUT | `/{id}` | Modifier |
| DELETE | `/{id}` | Supprimer |
| PATCH | `/{id}/status` | Changer le statut (valide les transitions) |
| PATCH | `/{id}/assign` | Assigner un agent |
| GET | `/pipeline` | Stats pipeline par statut |
| GET | `/pipeline?agency_id=...` | Stats pipeline filtrées |

**Endpoint public** (sans auth) :

| Méthode | Path | Description |
|---------|------|-------------|
| POST | `/properties/{id}/inquire` | Créer un lead depuis le site public |

#### Automatisations sur changement de statut

Lors d'un `PATCH /{id}/status` :
1. **Activity** créée automatiquement (type `status_change`)
2. **Task** de suivi créée :
   - `contacted` → tâche à J+3
   - `negotiation` → tâche à J+7
3. **Notification** envoyée si statut = `won`

Lors d'un `PATCH /{id}/assign` :
1. **Activity** créée (type `assignment`)
2. **Notification** envoyée à l'agent assigné

### 3.3 Activities (`/api/v1/activities`)

| Méthode | Path | Description |
|---------|------|-------------|
| GET | `/` | Liste (filtrable par lead_id, contact_id) |
| GET | `/{id}` | Détail |
| POST | `/` | Créer manuellement |

### 3.4 Tasks (`/api/v1/tasks`)

| Méthode | Path | Description |
|---------|------|-------------|
| GET | `/` | Liste (filtrable par status, assigned_to) |
| GET | `/{id}` | Détail |
| POST | `/` | Créer |
| PUT | `/{id}` | Modifier |
| PATCH | `/{id}/complete` | Marquer comme complétée |

### 3.5 Notifications (`/api/v1/notifications`)

| Méthode | Path | Description |
|---------|------|-------------|
| GET | `/` | Liste (de l'utilisateur courant) |
| PATCH | `/{id}/read` | Marquer comme lue |
| POST | `/read-all` | Tout marquer comme lu |

### 3.6 Favorites (`/api/v1/favorites`)

| Méthode | Path | Description |
|---------|------|-------------|
| GET | `/` | Liste des favoris de l'utilisateur |
| POST | `/` | Ajouter un favori |
| DELETE | `/{id}` | Retirer un favori |

### 3.7 Saved Searches (`/api/v1/saved-searches`)

| Méthode | Path | Description |
|---------|------|-------------|
| GET | `/` | Liste |
| POST | `/` | Créer |
| PUT | `/{id}` | Modifier |
| DELETE | `/{id}` | Supprimer |

### 3.8 Conversations (`/api/v1/conversations`)

| Méthode | Path | Description |
|---------|------|-------------|
| GET | `/` | Liste des conversations de l'utilisateur |
| GET | `/{id}` | Détail avec messages |
| POST | `/` | Créer une conversation |
| POST | `/{id}/messages` | Envoyer un message |
| PATCH | `/{id}/archive` | Archiver |

### 3.9 Dashboard (`/api/v1/dashboard`)

| Méthode | Path | Description |
|---------|------|-------------|
| GET | `/stats` | KPIs globaux (leads, contacts, taux conversion, tâches) |

---

## 4. Admin Panel — Vues CRM

### 4.1 Organisation sidebar

```
📊 Tableau de bord CRM    (CustomView → /admin/crm-dashboard)
📋 Kanban Leads            (CustomView → /admin/crm-kanban)
📂 CRM (DropDown)
   ├── 📇 Contacts         (ModelView → Contact)
   ├── 🔄 Leads            (ModelView → Lead)
   ├── 📜 Activités        (ModelView → Activity)
   ├── ✅ Tâches           (ModelView → Task)
   ├── 💬 Conversations    (ModelView → Conversation)
   └── 🔔 Notifications   (ModelView → Notification)
```

### 4.2 Dashboard CRM (`/admin/crm-dashboard`)

Vue custom Tabler UI avec :
- **KPI Cards** : Total leads, contacts, taux de conversion, tâches en retard, notifications non lues, conversations actives
- **Pipeline funnel** : Barres colorées par statut avec tooltips
- **Sources** : Barres de progression par source d'acquisition
- **Résumé tâches** : Par statut (pending, in_progress, completed)
- **Leads récents** : Tableau des 5 derniers leads
- **Timeline activités** : 10 dernières activités

**Fichiers** : `app/admin/crm_dashboard.py`, `app/templates/admin/crm/dashboard.html`

### 4.3 Kanban Leads (`/admin/crm-kanban`)

Vue Kanban drag-and-drop pour le pipeline commercial :

- **6 colonnes** : Nouveau, Contacté, Qualifié, Négociation, Gagné, Perdu
- **Drag & drop** : HTML5 natif, zéro dépendance externe
- **Transitions validées** côté client (miroir de `services/lead.py`)
- **Mise à jour optimiste** : carte déplacée immédiatement, rollback si erreur API
- **Cartes enrichies** : nom contact, bien, source, priorité (dot coloré), probabilité (badge %), valeur négociée, date clôture prévue, notes
- **Colonnes non autorisées** s'estompent pendant le drag
- **Toast notifications** succès/erreur
- **Hauteur responsive** : `calc(100vh - 200px)`

L'endpoint PATCH est directement intégré dans la CustomView (`/admin/crm-kanban` accepte GET + PATCH) pour réutiliser l'authentification admin (SessionMiddleware), évitant le problème de 401 avec l'API REST qui utilise un mécanisme d'auth différent (fastapi-users cookie/bearer).

**Fichiers** : `app/admin/lead_kanban.py`, `app/templates/admin/crm/lead_kanban.html`

### 4.4 Lead List View

Vue liste custom avec :
- Badges colorés par statut
- Dots de priorité colorés
- Bouton "Vue Kanban" dans le header

**Fichier** : `app/templates/admin/crm/lead_list.html`

---

## 5. Authentification

### Double système

| Backend | Transport | Usage | Durée |
|---------|-----------|-------|-------|
| `jwt-cookie` | Cookie (`fastapiusersauth`) | Admin web | 1h |
| `jwt-bearer` | Bearer token | API mobile | 15min |

### Refresh tokens

- Modèle `RefreshToken` en base (30 jours)
- Endpoints : `POST /api/v1/auth/login`, `/refresh`, `/logout`
- `require_role(*roles)` — dependency pour contrôle d'accès par rôle

### Admin panel

L'admin utilise **starlette SessionMiddleware** (pas les cookies fastapi-users) :
- Token stocké dans `request.session["session"]`
- Auth provider custom : `FastapiUsersAuthProvider`
- `cookie_secure` dynamique : `False` en dev, `True` en prod

**Important** : Les appels AJAX depuis l'admin doivent passer par des endpoints admin (CustomView) et non par l'API REST, car les mécanismes d'auth sont séparés.

---

## 6. Données de test (Seeders)

### 6.1 CRM (`app/seed_crm.py`)

| Entité | Quantité |
|--------|----------|
| Contacts | 20 |
| Leads | 30 (répartis sur tous les statuts) |
| Activities | ~60 |
| Tasks | 25 |
| Notifications | 15 |
| Conversations | 10 |
| Messages | ~50 |
| Favorites | 8 |
| Saved Searches | 5 |

### 6.2 Properties (`app/seed_properties.py`)

| Entité | Quantité |
|--------|----------|
| Agences | 5 (SN, CI, GN) |
| Agents | 5 |
| Biens | 40 (F2-F5, villas, duplex, bureaux, magasins, terrains, parking) |
| Images | ~160 (3-5 par bien via picsum.photos) |

Distribution géographique : Dakar (Almadies, Ngor, Mermoz, Plateau, Yoff…), Saly, Saint-Louis, Abidjan (Cocody, Marcory), Conakry (Kaloum, Kipé).

### Chaîne d'exécution

```python
seed_database()
├── populate_users()
├── polulate_property_types()
├── polulate_property_rent_types()
├── populate_countries()
├── seed_properties_data()      # agences, agents, biens, images
└── seed_crm_data()             # contacts, leads, activités, tâches...
```

Tous les seeders sont **idempotents** (vérifient l'existence avant insertion).

---

## 7. Décisions techniques

### Pourquoi pas d'Opportunities séparées (style Salesforce) ?

Le Lead couvre déjà le cycle Lead + Opportunity :
- Statuts `new`/`contacted` = Lead non qualifié
- Statuts `qualified`/`negotiation`/`won`/`lost` = Opportunity
- Le "produit" est toujours un bien immobilier (pas de line items)
- Le "montant" est le prix du bien ou `deal_value` si négocié
- Les champs `probability`, `expected_close`, `deal_value` donnent 80% de la valeur d'une Opportunity sans complexité supplémentaire

### Convention de nommage

- Tables : snake_case singulier (`lead`, `contact`, `activity`)
- UUID PKs : `Column(UUID(as_uuid=True), default=uuid.uuid4)`
- Audit : `created_at`, `updated_at`, `created_by`, `updated_by`
- Events SQLAlchemy `before_insert`/`before_update` pour l'audit automatique

### Gotchas

- `Activity.metadata_` (avec underscore) mappé sur `Column("metadata", JSON)` pour éviter le conflit SQLAlchemy
- `ConversationService.__init__` prend 2 repos (conversation + message) — exception au pattern `BaseService(repo)`
- `seed_properties` doit s'exécuter AVANT `seed_crm` car les favoris CRM référencent des biens

---

## 8. Fichiers du CRM

### Modèles
```
app/models/contact.py
app/models/lead.py
app/models/activity.py
app/models/task.py
app/models/notification.py
app/models/favorite.py
app/models/saved_search.py
app/models/conversation.py
app/models/message.py
```

### Repositories
```
app/repositories/contact.py
app/repositories/lead.py
app/repositories/activity.py
app/repositories/task.py
app/repositories/notification.py
app/repositories/favorite.py
app/repositories/saved_search.py
app/repositories/conversation.py
```

### Services
```
app/services/contact.py
app/services/lead.py
app/services/activity.py
app/services/task.py
app/services/notification.py
app/services/favorite.py
app/services/saved_search.py
app/services/conversation.py
```

### Schemas (Pydantic)
```
app/schemas/contact.py
app/schemas/lead.py
app/schemas/activity.py
app/schemas/task.py
app/schemas/notification.py
app/schemas/favorite.py
app/schemas/saved_search.py
app/schemas/conversation.py
```

### API Routes
```
app/api/v1/contact.py
app/api/v1/lead.py
app/api/v1/activity.py
app/api/v1/task.py
app/api/v1/notification.py
app/api/v1/favorite.py
app/api/v1/saved_search.py
app/api/v1/conversation.py
app/api/v1/dashboard.py
```

### Admin Views
```
app/admin/contact.py
app/admin/lead.py
app/admin/lead_kanban.py
app/admin/activity.py
app/admin/task.py
app/admin/notification.py
app/admin/conversation.py
app/admin/crm_dashboard.py
```

### Templates
```
app/templates/admin/crm/dashboard.html
app/templates/admin/crm/lead_list.html
app/templates/admin/crm/lead_kanban.html
```

### Seeders
```
app/seed_crm.py
app/seed_properties.py
```
