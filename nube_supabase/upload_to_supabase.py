import os
import sys
import json
import urllib.request
import urllib.error

# Fix terminal encoding for Windows
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("  BOXINERA IMPORTADORA - SUBIDA MASIVA A SUPABASE (1.936 ÍTEMS)")
print("=" * 60)

# Check if arguments provided or ask interactively
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

if len(sys.argv) >= 3:
    supabase_url = sys.argv[1].rstrip('/')
    supabase_key = sys.argv[2]

if not supabase_url:
    print("\nPegá los datos de tu proyecto de Supabase (Settings -> API):")
    supabase_url = input("1. Project URL (ej. https://xxxx.supabase.co): ").strip().rstrip('/')

if not supabase_key:
    supabase_key = input("2. API Key (anon public o service_role): ").strip()

if not supabase_url or not supabase_key:
    print("\n❌ Error: Debes ingresar la URL y la Key de Supabase.")
    sys.exit(1)

# Locate perfumes_db.json (check parent directory or current directory)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

db_path = os.path.join(parent_dir, "assets", "perfumes_db.json")
if not os.path.exists(db_path):
    db_path = os.path.join(current_dir, "assets", "perfumes_db.json")

if not os.path.exists(db_path):
    print(f"❌ Error: No se encontró el archivo de base de datos perfumes_db.json")
    print(f"Buscado en: {db_path}")
    sys.exit(1)

with open(db_path, "r", encoding="utf-8") as f:
    products = json.load(f)

print(f"\n📦 Cargados {len(products)} productos locales para subir.")

endpoint = f"{supabase_url}/rest/v1/products"
headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates" # Upsert mode
}

# Map keys to match supabase schema: oldPrice -> old_price, inStock -> in_stock
def format_item(p):
    return {
        "id": p.get("id"),
        "code": p.get("code"),
        "name": p.get("name"),
        "brand": p.get("brand"),
        "category": p.get("category"),
        "line": p.get("line"),
        "details": p.get("details"),
        "color": p.get("color"),
        "ml": p.get("ml"),
        "gender": p.get("gender"),
        "price": p.get("price"),
        "old_price": p.get("oldPrice"),
        "badge": p.get("badge"),
        "image": p.get("image"),
        "in_stock": p.get("inStock", True),
        "wholesale": p.get("wholesale")
    }

formatted_products = [format_item(p) for p in products]

# Upload in batches of 100
BATCH_SIZE = 100
total_batches = (len(formatted_products) + BATCH_SIZE - 1) // BATCH_SIZE

print(f"\n🚀 Iniciando subida en {total_batches} lotes a {endpoint}...\n")

success_count = 0

for i in range(0, len(formatted_products), BATCH_SIZE):
    batch = formatted_products[i:i + BATCH_SIZE]
    batch_num = (i // BATCH_SIZE) + 1
    
    data_bytes = json.dumps(batch).encode('utf-8')
    req = urllib.request.Request(endpoint, data=data_bytes, headers=headers, method='POST')

    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status in (200, 201):
                success_count += len(batch)
                percent = int((success_count / len(formatted_products)) * 100)
                print(f"  ✓ Lote {batch_num}/{total_batches}: {len(batch)} productos subidos ({percent}%)")
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8', errors='ignore')
        print(f"  ❌ Error en Lote {batch_num} (HTTP {e.code}): {err_msg}")
        print("\nVerificá que hayas ejecutado el archivo 'supabase_schema.sql' en el SQL Editor de Supabase.")
        sys.exit(1)
    except Exception as e:
        print(f"  ❌ Error de conexión: {e}")
        sys.exit(1)

print("\n" + "=" * 60)
print(f"🎉 ¡SUBIDA EXITOSA! {success_count} productos cargados en Supabase.")
print("=" * 60)
