import json
from faker import Faker
from bson import ObjectId
import random
from datetime import datetime, timedelta
import bcrypt
from collections import defaultdict

# Configuration
USER_COUNT = 5000  # Total users (VIP + Normal + Trial)
OUTPUT_FILE = "casino_users.json"
DEFAULT_PASSWORD = "Temp123!"  # Will be hashed

# Role distribution - Adjusted to exclude admin
ROLE_DISTRIBUTION = {
    'vip': 0.20,    # 20% VIP
    'trial': 0.30,  # 30% Trial
    'normal': 0.50  # 50% Normal
}

def generate_users(count):
    """Generate casino users with Chilean data (no admin accounts)"""
    fake = Faker('es_CL')
    users = []
    password_hash = bcrypt.hashpw(DEFAULT_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    for _ in range(count):
        # Weighted random role selection
        role = random.choices(
            list(ROLE_DISTRIBUTION.keys()),
            weights=list(ROLE_DISTRIBUTION.values()),
            k=1
        )[0]
        
        # Balance logic
        if role == 'trial':
            balance = 100000  # Fixed for trial accounts
        elif role == 'vip':
            balance = random.randint(100000, 1000000)  # VIPs get 100k-1M
        else:
            balance = random.randint(0, 50000)  # Normal users get 0-50k
            
        # Chilean phone number (mobile only)
        phone = f"+569{fake.msisdn()[3:10]}"  # +569 + 8 digits
        
        # Account dates
        created_at = fake.date_time_between(start_date='-1y', end_date='now')
        last_login = fake.date_time_between(start_date=created_at, end_date='now') if random.random() > 0.4 else None
        
        users.append({
            "_id": {"$oid": str(ObjectId())},
            "email": f"{fake.unique.user_name()}@{random.choice(['gmail.cl','hotmail.com','outlook.cl'])}",
            "password": password_hash,
            "phone": phone,
            "role": role,
            "balance": balance,
            "created_at": {"$date": created_at.isoformat() + "Z"},
            "last_login": {"$date": last_login.isoformat() + "Z"} if last_login else None,
            "active": random.random() < 0.85  # 85% active rate
        })
    
    return users

def save_to_file(data, filename):
    """Save to JSON with MongoDB extended format"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Generated {len(data)} users in {filename}")

if __name__ == "__main__":
    print(f"⚙️ Generating {USER_COUNT} casino users (VIP/Normal/Trial)...")
    users = generate_users(USER_COUNT)
    
    # Print summary
    role_counts = defaultdict(int)
    for user in users:
        role_counts[user['role']] += 1
    
    print("\n📊 Distribution:")
    for role, count in role_counts.items():
        print(f"- {role.upper()}: {count} users ({count/USER_COUNT:.1%})")
    
    print(f"\n💵 Balance ranges:")
    print(f"- VIP: 100,000 - 1,000,000 CLP")
    print(f"- Trial: Fixed 100,000 CLP")
    print(f"- Normal: 0 - 50,000 CLP")
    
    save_to_file(users, OUTPUT_FILE)
    
    print("\n🔍 Sample user:")
    print(json.dumps(users[0], indent=2))