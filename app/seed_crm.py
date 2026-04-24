"""
CRM test data seeder.

Generates realistic test data for all CRM entities:
- 20 contacts (buyers, sellers, tenants, landlords, investors)
- 30 leads across all pipeline stages, linked to agencies/agents/properties
- 60 activities (auto + manual)
- 25 tasks (pending, overdue, completed)
- 15 notifications
- 10 conversations with messages, linked to leads
- 8 favorites + 5 saved searches

Run via: seed_database() -> seed_crm_data()
Or standalone: python seed_crm.py
"""
import asyncio
import random
import uuid
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal

import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import get_async_session_context, User
from models.agency import Agency
from models.agent import Agent
from models.property import Property
from models.contact import Contact
from models.lead import Lead
from models.activity import Activity
from models.task import Task
from models.notification import Notification
from models.favorite import Favorite
from models.saved_search import SavedSearch
from models.conversation import Conversation, ConversationParticipant
from models.message import Message
# Ensure FK-referenced tables are registered in metadata
import models.city  # noqa: F401 — Contact.city FK


def _now():
    return datetime.now(timezone.utc)


def _past(days_max=60):
    return _now() - timedelta(days=random.randint(0, days_max), hours=random.randint(0, 23))


def _future(days_max=14):
    return _now() + timedelta(days=random.randint(1, days_max))


# --- Contact data ---
CONTACTS = [
    {"first_name": "Amadou", "last_name": "Diallo", "email": "amadou.diallo@gmail.com", "phone_number": "+221 771234567", "contact_type": "buyer", "country": "SN"},
    {"first_name": "Fatou", "last_name": "Sow", "email": "fatou.sow@outlook.com", "phone_number": "+221 772345678", "contact_type": "buyer", "country": "SN"},
    {"first_name": "Moussa", "last_name": "Ndiaye", "email": "moussa.ndiaye@yahoo.fr", "phone_number": "+221 773456789", "contact_type": "tenant", "country": "SN"},
    {"first_name": "Aissatou", "last_name": "Ba", "email": "aissatou.ba@gmail.com", "phone_number": "+221 774567890", "contact_type": "buyer", "country": "SN"},
    {"first_name": "Ibrahima", "last_name": "Fall", "email": "ibrahima.fall@hotmail.com", "phone_number": "+221 775678901", "contact_type": "investor", "country": "SN"},
    {"first_name": "Mariama", "last_name": "Camara", "email": "mariama.camara@gmail.com", "phone_number": "+224 621234567", "contact_type": "buyer", "country": "GN"},
    {"first_name": "Ousmane", "last_name": "Touré", "email": "ousmane.toure@outlook.fr", "phone_number": "+225 071234567", "contact_type": "tenant", "country": "CI"},
    {"first_name": "Khady", "last_name": "Diop", "email": "khady.diop@gmail.com", "phone_number": "+221 776789012", "contact_type": "seller", "country": "SN"},
    {"first_name": "Cheikh", "last_name": "Mbaye", "email": "cheikh.mbaye@proton.me", "phone_number": "+221 777890123", "contact_type": "landlord", "country": "SN"},
    {"first_name": "Awa", "last_name": "Gueye", "email": "awa.gueye@gmail.com", "phone_number": "+221 778901234", "contact_type": "buyer", "country": "SN"},
    {"first_name": "Mamadou", "last_name": "Sarr", "email": "mamadou.sarr@yahoo.fr", "phone_number": "+221 779012345", "contact_type": "investor", "country": "SN"},
    {"first_name": "Rokhaya", "last_name": "Niang", "email": "rokhaya.niang@gmail.com", "phone_number": "+221 770123456", "contact_type": "tenant", "country": "SN"},
    {"first_name": "Abdoulaye", "last_name": "Sy", "email": "abdoulaye.sy@outlook.com", "phone_number": "+225 072345678", "contact_type": "buyer", "country": "CI"},
    {"first_name": "Dieynaba", "last_name": "Kane", "email": "dieynaba.kane@gmail.com", "phone_number": "+221 771112233", "contact_type": "buyer", "country": "SN"},
    {"first_name": "Papa", "last_name": "Thiam", "email": "papa.thiam@hotmail.fr", "phone_number": "+221 772223344", "contact_type": "landlord", "country": "SN"},
    {"first_name": "Ndeye", "last_name": "Faye", "email": "ndeye.faye@gmail.com", "phone_number": "+224 622345678", "contact_type": "buyer", "country": "GN"},
    {"first_name": "Boubacar", "last_name": "Dieng", "email": "boubacar.dieng@yahoo.fr", "phone_number": "+221 773334455", "contact_type": "investor", "country": "SN"},
    {"first_name": "Coumba", "last_name": "Diouf", "email": "coumba.diouf@gmail.com", "phone_number": "+221 774445566", "contact_type": "tenant", "country": "SN"},
    {"first_name": "Aliou", "last_name": "Cissé", "email": "aliou.cisse@proton.me", "phone_number": "+225 073456789", "contact_type": "buyer", "country": "CI"},
    {"first_name": "Mame", "last_name": "Diarra", "email": "mame.diarra@gmail.com", "phone_number": "+221 775556677", "contact_type": "seller", "country": "SN"},
]

SOURCES = ["website", "mobile_app", "phone", "walk_in", "referral", "social_media"]
STATUSES = ["new", "contacted", "qualified", "negotiation", "won", "lost"]
PRIORITIES = ["low", "medium", "high", "urgent"]
ACTIVITY_TYPES = ["call", "email", "sms", "whatsapp", "visit", "meeting", "note", "status_change"]
TASK_TYPES = ["call", "email", "visit", "follow_up", "document", "other"]

# Status distribution (weighted)
STATUS_WEIGHTS = [5, 6, 5, 5, 4, 5]  # ~30 total


async def _get_users(session: AsyncSession):
    result = await session.execute(select(User).limit(5))
    return result.scalars().all()


async def _get_agencies(session: AsyncSession) -> list[Agency]:
    result = await session.execute(select(Agency).filter_by(is_active=True))
    return result.scalars().all()


async def _get_agents(session: AsyncSession) -> list[Agent]:
    result = await session.execute(select(Agent))
    return result.scalars().all()


async def _get_properties(session: AsyncSession) -> list[Property]:
    result = await session.execute(select(Property).limit(40))
    return result.scalars().all()


async def seed_contacts(session: AsyncSession) -> list[Contact]:
    """Create 20 contacts."""
    contacts = []
    for data in CONTACTS:
        contact = Contact(**data)
        session.add(contact)
        contacts.append(contact)
    await session.flush()
    print(f"  ✓ {len(contacts)} contacts created")
    return contacts


DEFAULT_PROBABILITY = {
    "new": 10, "contacted": 25, "qualified": 50,
    "negotiation": 75, "won": 100, "lost": 0,
}


async def seed_leads(
    session: AsyncSession,
    contacts: list[Contact],
    agencies: list[Agency],
    agents: list[Agent],
    properties: list[Property],
) -> list[Lead]:
    """Create 30 leads linked to agencies, agents, and properties."""
    leads = []
    status_pool = []
    for status, weight in zip(STATUSES, STATUS_WEIGHTS):
        status_pool.extend([status] * weight)
    random.shuffle(status_pool)

    if not agencies:
        print("  ⚠ No agencies found — cannot create leads")
        return leads

    # Build a map: agency_id → agents in that agency
    agents_by_agency = {}
    for ag in agents:
        agents_by_agency.setdefault(ag.agency_id, []).append(ag)

    # Build a map: agency_id → properties in that agency
    props_by_agency = {}
    for p in properties:
        props_by_agency.setdefault(p.agency_id, []).append(p)

    for i in range(30):
        contact = random.choice(contacts)
        status = status_pool[i % len(status_pool)]
        agency = random.choice(agencies)

        # Pick agent from same agency (if any)
        agency_agents = agents_by_agency.get(agency.id, [])
        agent = random.choice(agency_agents) if agency_agents else None

        # Pick property from same agency (~80% of leads have a property)
        agency_props = props_by_agency.get(agency.id, [])
        prop = random.choice(agency_props) if agency_props and random.random() < 0.8 else None

        # Compute deal value from property price when available
        deal_value = None
        if prop and prop.price:
            deal_value = prop.price * Decimal(str(random.uniform(0.85, 1.15))).quantize(Decimal("0.01"))
        elif status in ("qualified", "negotiation", "won"):
            deal_value = Decimal(str(random.choice([25_000_000, 50_000_000, 75_000_000, 150_000_000])))

        # Expected close date based on status
        expected_close = None
        if status in ("contacted", "qualified"):
            expected_close = (date.today() + timedelta(days=random.randint(14, 60)))
        elif status == "negotiation":
            expected_close = (date.today() + timedelta(days=random.randint(3, 21)))
        elif status == "won":
            expected_close = (date.today() - timedelta(days=random.randint(1, 30)))

        lead = Lead(
            contact_id=contact.id,
            agency_id=agency.id,
            agent_id=agent.id if agent else None,
            property_id=prop.id if prop else None,
            source=random.choice(SOURCES),
            status=status,
            priority=random.choice(PRIORITIES),
            probability=DEFAULT_PROBABILITY.get(status, 10),
            expected_close=expected_close,
            deal_value=deal_value,
            notes=random.choice([
                "Recherche appartement 3 pièces à Dakar",
                "Intéressé par villa avec piscine",
                "Budget: 150M CFA, zone Almadies",
                "Demande de location meublée pour 1 an",
                "Investisseur cherche immeuble de rapport",
                "Recherche terrain constructible à Saly",
                "Demande urgente — déménagement dans 2 semaines",
                "Recommandé par un client existant",
                None,
            ]),
            lost_reason="Budget insuffisant" if status == "lost" else None,
            created_at=_past(45),
        )
        session.add(lead)
        leads.append(lead)
    await session.flush()
    print(f"  ✓ {len(leads)} leads created (linked to {len(set(l.agency_id for l in leads))} agencies)")
    return leads


async def seed_activities(session: AsyncSession, leads: list[Lead], contacts: list[Contact]) -> list[Activity]:
    """Create ~60 activities tied to leads."""
    activities = []

    for lead in leads:
        num_activities = random.randint(1, 4)
        for j in range(num_activities):
            atype = random.choice(ACTIVITY_TYPES)
            titles = {
                "call": "Appel téléphonique avec le prospect",
                "email": "Email de suivi envoyé",
                "sms": "SMS de rappel rendez-vous",
                "whatsapp": "Échange WhatsApp — photos du bien",
                "visit": "Visite du bien programmée",
                "meeting": "Réunion au bureau de l'agence",
                "note": "Note interne sur le dossier",
                "status_change": f"Statut changé vers {lead.status}",
            }
            activity = Activity(
                lead_id=lead.id,
                contact_id=lead.contact_id,
                activity_type=atype,
                title=titles.get(atype, "Activité"),
                description=random.choice([
                    "Le prospect est très intéressé, à relancer cette semaine.",
                    "Visite effectuée, le client souhaite réfléchir.",
                    "Documents envoyés par email.",
                    "Négociation en cours sur le prix.",
                    "Le prospect demande des informations complémentaires.",
                    None,
                ]),
                created_at=_past(30),
            )
            session.add(activity)
            activities.append(activity)
    await session.flush()
    print(f"  ✓ {len(activities)} activities created")
    return activities


async def seed_tasks(session: AsyncSession, leads: list[Lead], users: list[User]) -> list[Task]:
    """Create 25 tasks — mix of pending, overdue, and completed."""
    tasks = []
    if not users:
        print("  ⚠ No users found, skipping tasks")
        return tasks

    for i in range(25):
        lead = random.choice(leads)
        user = random.choice(users)
        is_overdue = i < 5
        is_completed = 5 <= i < 12

        if is_overdue:
            due = _now() - timedelta(days=random.randint(1, 7))
            status = "pending"
        elif is_completed:
            due = _past(20)
            status = "completed"
        else:
            due = _future(14)
            status = random.choice(["pending", "in_progress"])

        task = Task(
            lead_id=lead.id,
            contact_id=lead.contact_id,
            assigned_to=user.id,
            assigned_by=random.choice(users).id,
            title=random.choice([
                "Relancer le prospect par téléphone",
                "Envoyer les documents du bien",
                "Planifier une visite",
                "Suivre la négociation en cours",
                "Préparer le contrat de bail",
                "Vérifier les références du locataire",
                "Rappeler le propriétaire",
                "Mettre à jour le dossier client",
            ]),
            task_type=random.choice(TASK_TYPES),
            status=status,
            priority=random.choice(PRIORITIES),
            due_date=due,
            completed_at=_past(5) if is_completed else None,
        )
        session.add(task)
        tasks.append(task)
    await session.flush()
    print(f"  ✓ {len(tasks)} tasks created ({sum(1 for t in tasks if t.status == 'pending')} pending, 5 overdue)")
    return tasks


async def seed_notifications(session: AsyncSession, users: list[User], leads: list[Lead]) -> None:
    """Create 15 notifications for users."""
    if not users:
        return

    notif_templates = [
        ("new_lead", "Nouveau lead", "Un nouveau lead a été créé depuis le site web."),
        ("lead_assigned", "Lead assigné", "Un nouveau lead vous a été assigné."),
        ("task_due", "Tâche à faire", "Vous avez une tâche qui arrive à échéance."),
        ("task_overdue", "Tâche en retard", "Une tâche est en retard et nécessite votre attention."),
        ("new_message", "Nouveau message", "Vous avez reçu un nouveau message d'un prospect."),
        ("review_posted", "Avis publié", "Un nouvel avis a été publié sur un de vos biens."),
        ("system", "Mise à jour système", "Le système CRM a été mis à jour avec de nouvelles fonctionnalités."),
    ]

    count = 0
    for i in range(15):
        user = random.choice(users)
        template = random.choice(notif_templates)
        lead = random.choice(leads) if template[0] in ("new_lead", "lead_assigned") else None
        notif = Notification(
            user_id=user.id,
            title=template[1],
            body=template[2],
            notification_type=template[0],
            reference_type="lead" if lead else None,
            reference_id=lead.id if lead else None,
            is_read=random.choice([True, False, False]),  # 2/3 unread
            created_at=_past(10),
        )
        session.add(notif)
        count += 1
    await session.flush()
    print(f"  ✓ {count} notifications created")


async def seed_conversations(session: AsyncSession, users: list[User], leads: list[Lead]) -> None:
    """Create 10 conversations with messages, linked to leads."""
    if len(users) < 2:
        print("  ⚠ Not enough users for conversations, skipping")
        return

    subjects = [
        "Appartement F3 Almadies — Visite",
        "Villa Saly — Négociation prix",
        "Bureau Plateau — Disponibilité",
        "Terrain Diamniadio — Documents",
        "Duplex Mermoz — Informations",
        "Studio Liberté 6 — Location",
        "Immeuble Point E — Investissement",
        "Appartement Ngor — Réservation",
        "Villa Fann — Rendez-vous",
        "Magasin Medina — Bail commercial",
    ]

    messages_pool = [
        "Bonjour, je suis intéressé par ce bien. Est-il toujours disponible ?",
        "Oui, le bien est disponible. Quand souhaitez-vous organiser une visite ?",
        "Je suis disponible ce week-end, samedi matin si possible.",
        "Parfait, je vous propose samedi à 10h. Je vous envoie l'adresse exacte.",
        "Merci beaucoup ! J'ai quelques questions sur les charges.",
        "Les charges mensuelles sont de 50 000 CFA, tout compris.",
        "D'accord, et concernant la caution ?",
        "La caution est de 2 mois de loyer. Je vous prépare le dossier.",
        "Pouvez-vous m'envoyer plus de photos de l'intérieur ?",
        "Bien sûr, je vous envoie un album complet par email.",
        "Le prix est-il négociable ?",
        "Il y a une petite marge de négociation, nous pouvons en discuter lors de la visite.",
        "J'ai visité le bien, il me plaît beaucoup. Quelles sont les prochaines étapes ?",
        "Excellent ! Il faut constituer un dossier avec pièce d'identité et justificatif de revenus.",
        "Je vous envoie les documents dans la journée.",
    ]

    conv_count = 0
    msg_count = 0
    for i in range(10):
        u1 = users[i % len(users)]
        u2 = users[(i + 1) % len(users)]
        if u1.id == u2.id and len(users) > 2:
            u2 = users[(i + 2) % len(users)]

        conv = Conversation(
            subject=subjects[i],
            lead_id=leads[i % len(leads)].id if leads else None,
            property_id=leads[i % len(leads)].property_id if leads else None,
            is_archived=i >= 8,
            created_at=_past(20),
        )
        session.add(conv)
        await session.flush()

        session.add(ConversationParticipant(conversation_id=conv.id, user_id=u1.id))
        session.add(ConversationParticipant(conversation_id=conv.id, user_id=u2.id))

        num_msgs = random.randint(3, 8)
        base_time = conv.created_at or _past(20)
        for j in range(num_msgs):
            sender = u1 if j % 2 == 0 else u2
            msg = Message(
                conversation_id=conv.id,
                sender_id=sender.id,
                content=random.choice(messages_pool),
                message_type="text",
                created_at=base_time + timedelta(hours=j * random.randint(1, 12)),
            )
            session.add(msg)
            msg_count += 1
        conv_count += 1

    await session.flush()
    print(f"  ✓ {conv_count} conversations, {msg_count} messages created")


async def seed_favorites_and_searches(session: AsyncSession, users: list[User]) -> None:
    """Create favorites and saved searches if properties exist."""
    from models.property import Property
    result = await session.execute(select(Property.id).limit(20))
    property_ids = [row[0] for row in result.all()]

    if not property_ids or not users:
        print("  ⚠ No properties or users found, skipping favorites/saved searches")
        return

    # Favorites
    fav_count = 0
    seen = set()
    for _ in range(min(8, len(property_ids))):
        user = random.choice(users)
        prop_id = random.choice(property_ids)
        key = (user.id, prop_id)
        if key in seen:
            continue
        seen.add(key)
        session.add(Favorite(user_id=user.id, property_id=prop_id))
        fav_count += 1

    # Saved searches
    search_filters = [
        {"type": "F3", "city": "Dakar", "price_max": 200000},
        {"type": "VILLA", "country": "SN", "price_min": 100000000},
        {"rent_type": "RENT_FURNISHED", "rooms_min": 2},
        {"type": "LAND", "city": "Saly", "surface_min": 500},
        {"type": "OFFICE", "city": "Dakar", "price_max": 500000},
    ]
    for i, filters in enumerate(search_filters):
        user = users[i % len(users)]
        session.add(SavedSearch(
            user_id=user.id,
            name=f"Recherche {i + 1}",
            filters=filters,
            notify_enabled=i < 3,
        ))

    await session.flush()
    print(f"  ✓ {fav_count} favorites, {len(search_filters)} saved searches created")


async def seed_crm_data() -> None:
    """Main CRM seeder — call from seed_database() or run standalone."""
    print("\n🏗️  Seeding CRM test data...")
    try:
        async with get_async_session_context() as session:
            # Check if CRM data already exists
            existing = await session.execute(select(Contact.id).limit(1))
            if existing.scalar_one_or_none():
                print("  ℹ CRM data already exists, skipping")
                return

            users = await _get_users(session)
            if not users:
                print("  ⚠ No users found — run base seed first")
                return

            agencies = await _get_agencies(session)
            agents = await _get_agents(session)
            properties = await _get_properties(session)

            if not agencies:
                print("  ⚠ No agencies found — run seed_properties first")
                return

            contacts = await seed_contacts(session)
            leads = await seed_leads(session, contacts, agencies, agents, properties)
            await seed_activities(session, leads, contacts)
            await seed_tasks(session, leads, users)
            await seed_notifications(session, users, leads)
            await seed_conversations(session, users, leads)
            await seed_favorites_and_searches(session, users)

            await session.commit()
            print("✅ CRM test data seeded successfully!\n")

    except sqlalchemy.exc.IntegrityError as e:
        print(f"  ⚠ CRM data already exists or integrity error: {e}")
    except Exception as e:
        print(f"  ❌ Error seeding CRM data: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(seed_crm_data())
