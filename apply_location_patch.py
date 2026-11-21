from pathlib import Path
import re, shutil, datetime, sys

root = Path.cwd()
stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
backup = root / f"location_backup_fixed_{stamp}"

files = [
    "backend/app/models/models.py",
    "backend/app/schemas/schemas.py",
    "backend/app/api/visits.py",
    "frontend/src/services/api.ts",
    "frontend/src/pages/VoiceAssistantPage.tsx",
]
for name in files:
    p = root / name
    if not p.exists():
        raise SystemExit(f"Missing file: {name}")
    dest = backup / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dest)

print("Backup:", backup)

def read(name):
    return (root / name).read_text(encoding="utf-8-sig")

def write(name, content):
    (root / name).write_text(content, encoding="utf-8")

def add_after_once(text, pattern, addition, label):
    matches = list(re.finditer(pattern, text, re.M))
    if len(matches) != 1:
        raise RuntimeError(f"{label}: expected 1 match, found {len(matches)}")
    m = matches[0]
    return text[:m.end()] + addition + text[m.end():]

# DATABASE MODEL
name = "backend/app/models/models.py"
s = read(name)
if "location_lat = Column" not in s:
    s = add_after_once(
        s,
        r"^    weight_kg = Column\(Float, nullable=True\)$",
        "\n    house_number = Column(String(100), nullable=True)"
        "\n    location_lat = Column(Float, nullable=True)"
        "\n    location_lng = Column(Float, nullable=True)"
        "\n    location_address = Column(String(500), nullable=True)",
        "HealthcareVisit model"
    )
write(name, s)

# PYDANTIC CREATE + RESPONSE SCHEMAS
name = "backend/app/schemas/schemas.py"
s = read(name)
for cls in ("HealthcareVisitCreate", "HealthcareVisitResponse"):
    start = s.find(f"class {cls}(")
    if start < 0:
        raise RuntimeError(f"Missing schema class {cls}")
    next_class = s.find("\nclass ", start + 1)
    end = len(s) if next_class < 0 else next_class
    block = s[start:end]
    if "location_lat:" not in block:
        block = add_after_once(
            block,
            r"^    weight_kg: Optional\[float\] = None$",
            "\n    house_number: Optional[str] = None"
            "\n    location_lat: Optional[float] = None"
            "\n    location_lng: Optional[float] = None"
            "\n    location_address: Optional[str] = None",
            cls
        )
        s = s[:start] + block + s[end:]
write(name, s)

# VISITS API
name = "backend/app/api/visits.py"
s = read(name)
for anchor, fields, label in [
    ("            weight_kg=v.weight_kg,",
     "\n            house_number=v.house_number,\n            location_lat=v.location_lat,\n            location_lng=v.location_lng,\n            location_address=v.location_address,", "GET response"),
    ("        weight_kg=payload.weight_kg,",
     "\n        house_number=payload.house_number,\n        location_lat=payload.location_lat,\n        location_lng=payload.location_lng,\n        location_address=payload.location_address,", "database insert"),
    ("        weight_kg=visit.weight_kg,",
     "\n        house_number=visit.house_number,\n        location_lat=visit.location_lat,\n        location_lng=visit.location_lng,\n        location_address=visit.location_address,", "POST response"),
]:
    if fields.strip().splitlines()[0].strip() not in s:
        s = add_after_once(s, r"^" + re.escape(anchor) + r"$", fields, label)
write(name, s)

# FRONTEND API PAYLOAD TYPE
name = "frontend/src/services/api.ts"
s = read(name)
if "location_lat?: number | null" not in s:
    s = add_after_once(
        s, r"^    weight_kg\?: number \| null;$",
        "\n    house_number?: string;"
        "\n    location_lat?: number | null;"
        "\n    location_lng?: number | null;"
        "\n    location_address?: string;",
        "frontend save API type"
    )
write(name, s)

# FRONTEND PAGE
name = "frontend/src/pages/VoiceAssistantPage.tsx"
s = read(name)

if "const [houseNumber, setHouseNumber]" not in s:
    s = add_after_once(
        s, r"^  const \[manualText, setManualText\] = useState\(''\);$",
        "\n  const [houseNumber, setHouseNumber] = useState('');",
        "house number state"
    )

if "const [gpsLocation, setGpsLocation]" not in s:
    s = add_after_once(
        s, r"^  const \[manualText, setManualText\] = useState\(''\);$",
        "\n  const [gpsLocation, setGpsLocation] = useState<{ latitude: number; longitude: number } | null>(null);"
        "\n  const [gpsStatus, setGpsStatus] = useState('Location not captured');",
        "GPS state"
    )

if "const captureLiveLocation" not in s:
    handler = """
  const captureLiveLocation = () => {
    if (!navigator.geolocation) {
      setGpsStatus('GPS is not supported by this browser');
      return;
    }
    setGpsStatus('Requesting location permission...');
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;
        setGpsLocation({ latitude, longitude });
        setGpsStatus('Location captured successfully');
      },
      (error) => setGpsStatus(error.message || 'Location permission denied'),
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );
  };

"""
    anchor = "  // 5. Explicit Record Confirmation"
    if s.count(anchor) != 1:
        raise RuntimeError("Could not locate confirmation handler")
    s = s.replace(anchor, handler + anchor, 1)

if "location_lat: gpsLocation" not in s:
    s = add_after_once(
        s, r"^        weight_kg: record\.weight_kg,$",
        "\n        house_number: houseNumber.trim(),"
        "\n        location_lat: gpsLocation?.latitude ?? null,"
        "\n        location_lng: gpsLocation?.longitude ?? null,"
        "\n        location_address: gpsLocation"
        "\n          ? `${gpsLocation.latitude.toFixed(6)}, ${gpsLocation.longitude.toFixed(6)}`"
        "\n          : '',",
        "visit save payload"
    )

if "Capture Live GPS Location" not in s:
    ui = """
              <div className="p-3 rounded-xl bg-white/5 border border-teal-500/20 space-y-3">
                <label className="block text-slate-300 text-xs font-semibold">House Number (enter manually)</label>
                <input
                  type="text"
                  value={houseNumber}
                  onChange={(e) => setHouseNumber(e.target.value)}
                  placeholder="Enter house / door number"
                  className="w-full rounded-lg bg-slate-900 border border-white/10 px-3 py-2 text-white text-sm"
                />
                <button
                  type="button"
                  onClick={captureLiveLocation}
                  className="w-full rounded-lg bg-teal-500/20 border border-teal-400/40 px-3 py-2 text-teal-200 text-xs font-bold"
                >
                  Capture Live GPS Location
                </button>
                <p className="text-xs text-slate-400">{gpsStatus}</p>
                {gpsLocation && (
                  <p className="text-xs text-emerald-300 font-mono">
                    Latitude: {gpsLocation.latitude.toFixed(6)} | Longitude: {gpsLocation.longitude.toFixed(6)}
                  </p>
                )}
              </div>

"""
    anchor = "            {/* Readback & Confirmation Gate Box */}"
    if s.count(anchor) != 1:
        raise RuntimeError("Could not locate report confirmation UI")
    s = s.replace(anchor, ui + anchor, 1)

write(name, s)
print("Frontend and backend source changes written.")

# DATABASE MIGRATION
migration = r'''
from sqlalchemy import inspect, text
from app.database.session import engine

columns = {
    "house_number": "VARCHAR(100)",
    "location_lat": "FLOAT",
    "location_lng": "FLOAT",
    "location_address": "VARCHAR(500)",
}
inspector = inspect(engine)
if "healthcare_visits" not in inspector.get_table_names():
    raise RuntimeError("healthcare_visits table not found")
existing = {c["name"] for c in inspector.get_columns("healthcare_visits")}
with engine.begin() as conn:
    for name, sql_type in columns.items():
        if name not in existing:
            conn.execute(text(f"ALTER TABLE healthcare_visits ADD COLUMN {name} {sql_type}"))
            print("Added:", name)
        else:
            print("Already exists:", name)
'''
(root / "backend/add_location_columns.py").write_text(migration, encoding="utf-8")
print("Patch files created.")
