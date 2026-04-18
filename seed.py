import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal, init_db, User, Content, Event
from backend.auth.utils import hash_password
from datetime import datetime, timedelta, timezone
import random

init_db()
db = SessionLocal()

# Clear existing data
db.query(Event).delete()
db.query(Content).delete()
db.query(User).delete()
db.commit()

now = datetime.now(timezone.utc)

# --- 50 Users ---
usernames = [
    "alice", "bob", "charlie", "diana", "evan", "fiona", "george", "hannah",
    "ivan", "julia", "kevin", "laura", "mike", "nina", "oscar", "priya",
    "quinn", "rachel", "sam", "tina", "umar", "vera", "will", "xena", "yash",
    "zara", "aaron", "bella", "carl", "demi", "eli", "faith", "gary", "holly",
    "ian", "jade", "kyle", "lisa", "mark", "nora", "owen", "paula", "raj",
    "sara", "tom", "uma", "victor", "wendy", "xander", "yasmin"
]

users = []
for i, name in enumerate(usernames, 1):
    user = User(
        username=name,
        email=f"{name}@example.com",
        password_hash=hash_password("password123"),
        created_at=now - timedelta(days=random.randint(1, 90))
    )
    db.add(user)
    users.append(user)
db.commit()

# --- 100 Content Posts ---
topics = [
    "How to learn Python fast", "Top 10 travel destinations", "Healthy meal prep ideas",
    "Best productivity apps", "Introduction to machine learning", "Photography tips for beginners",
    "Home workout routines", "Financial planning for students", "Web development roadmap",
    "Understanding cloud computing", "Social media marketing tips", "Book recommendations 2024",
    "Gaming setup guide", "Mental health awareness", "Career advice for freshers",
    "Data science projects", "Mobile app development", "Cooking Italian food",
    "Running a marathon", "Learning a new language", "Investing in stocks",
    "Building a personal brand", "Remote work tips", "Cybersecurity basics",
    "AI tools for productivity", "Sustainable living tips", "Music production guide",
    "Freelancing tips", "Starting a blog", "Digital art tutorials",
    "Python for data analysis", "Cloud architecture patterns", "DevOps best practices",
    "UI/UX design principles", "Database optimization", "API design guide",
    "Docker and containers", "Kubernetes basics", "React vs Vue comparison",
    "FastAPI tutorial", "PostgreSQL tips", "Snowflake data warehouse",
    "ETL pipeline design", "Data visualization", "Business intelligence tools",
    "Agile methodology", "System design interview", "Coding interview prep",
    "Open source contribution", "Tech startup ideas"
]

contents = []
for i, topic in enumerate(topics, 1):
    content = Content(
        user_id=random.choice(users).id,
        title=topic,
        body=f"This is a detailed post about: {topic}. " * 5,
        created_at=now - timedelta(days=random.randint(1, 90))
    )
    db.add(content)
    contents.append(content)
db.commit()

# --- 1500 Events spread over 90 days ---
event_types = ["login", "view", "like", "comment", "create"]
event_weights = [0.25, 0.35, 0.20, 0.12, 0.08]

for _ in range(1500):
    event_type = random.choices(event_types, weights=event_weights)[0]
    needs_content = event_type in {"view", "like", "comment"}
    event = Event(
        user_id=random.choice(users).id,
        content_id=random.choice(contents).id if needs_content else None,
        event_type=event_type,
        timestamp=now - timedelta(
            days=random.randint(0, 90),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
    )
    db.add(event)

db.commit()
db.close()

print("✅ Enhanced seed data inserted:")
print(f"   👥 50 users")
print(f"   📝 100 posts")
print(f"   ⚡ 1500 events over 90 days")
print(f"\nLogin with any user e.g:")
print(f"   Email: alice@example.com")
print(f"   Password: password123")
