"""
L3 Commercial HCP 360 & Next Best Action — Synthetic Data Generator
Generates: brands.csv, territories.csv, hcps.csv, rx_monthly.csv, calls.csv,
           call_notes.csv, messaging_docs.csv
Schema modeled on typical pharma commercial feeds (HCP master, IQVIA-style
prescription data, CRM call activity, field notes).

Planted patterns:
  1. Territory T07 (Pune West): Glucavia NRx drops ~35% from May 2026 after a
     formulary change; call notes there are dominated by prior-auth / access objections.
  2. Competitor Sematra gains share in T03 (Hyderabad Central) with rising
     competitor mentions in notes.
  3. ~40 Decile 8-10 HCPs have received no call in the last 90 days (missed targets).
"""
import csv
import os
import random
from datetime import date, timedelta

SEED = 42
random.seed(SEED)
OUT = os.path.join(os.path.dirname(__file__), '..', 'tracks', 'l3_commercial_hcp360', 'data')
os.makedirs(OUT, exist_ok=True)


def write_csv(name, rows):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


# --- brands: our brand + competitors in the T2D market ---
BRANDS = [
    ('BR-01', 'Glucavia', 'semaglutide-like GLP-1 RA', 'GLP-1 RA', 'Type 2 diabetes', 'Y'),
    ('BR-02', 'Sematra', 'GLP-1 RA', 'GLP-1 RA', 'Type 2 diabetes', 'N'),
    ('BR-03', 'Empaflo', 'SGLT2 inhibitor', 'SGLT2i', 'Type 2 diabetes', 'N'),
    ('BR-04', 'Sitaglen', 'DPP-4 inhibitor', 'DPP-4i', 'Type 2 diabetes', 'N'),
]
brands = [dict(BRAND_ID=b[0], BRAND_NAME=b[1], MOLECULE_CLASS=b[2], DRUG_CLASS=b[3],
               INDICATION=b[4], IS_OUR_BRAND=b[5]) for b in BRANDS]
write_csv('brands.csv', brands)

# --- territories ---
TERR = [
    ('T01', 'Bengaluru North', 'South', 'Ananya Rao'), ('T02', 'Bengaluru South', 'South', 'Karthik Iyer'),
    ('T03', 'Hyderabad Central', 'South', 'Sravani Reddy'), ('T04', 'Hyderabad West', 'South', 'Rahul Varma'),
    ('T05', 'Chennai', 'South', 'Divya Krishnan'), ('T06', 'Mumbai Central', 'West', 'Rohan Mehta'),
    ('T07', 'Pune West', 'West', 'Sneha Kulkarni'), ('T08', 'Ahmedabad', 'West', 'Harsh Patel'),
    ('T09', 'Delhi NCR', 'North', 'Aman Khanna'), ('T10', 'Jaipur', 'North', 'Pooja Sharma'),
    ('T11', 'Kolkata', 'East', 'Arijit Sen'), ('T12', 'Bhubaneswar', 'East', 'Lipsa Mohanty'),
]
territories = [dict(TERRITORY_ID=t[0], TERRITORY_NAME=t[1], REGION=t[2], REP_NAME=t[3],
                    REP_ID=f"REP-{i+1:03d}") for i, t in enumerate(TERR)]
write_csv('territories.csv', territories)

# --- HCPs ---
FIRST = ['Arjun', 'Priya', 'Vikram', 'Meera', 'Sanjay', 'Kavya', 'Ravi', 'Lakshmi', 'Suresh', 'Neha',
         'Anil', 'Deepa', 'Manoj', 'Swati', 'Rajesh', 'Asha', 'Nikhil', 'Shreya', 'Vivek', 'Anjali']
LAST = ['Sharma', 'Reddy', 'Iyer', 'Patel', 'Nair', 'Gupta', 'Rao', 'Menon', 'Joshi', 'Das',
        'Kumar', 'Singh', 'Pillai', 'Chatterjee', 'Desai', 'Bhat', 'Kapoor', 'Mishra']
SPECIALTY = [('Endocrinology', 0.18), ('Internal Medicine', 0.32), ('Family Medicine', 0.28),
             ('Cardiology', 0.12), ('Nephrology', 0.10)]
SETTING = ['Private clinic', 'Hospital-affiliated', 'Corporate hospital', 'Group practice']

hcps = []
for i in range(1, 2001):
    terr = random.choice(TERR)
    spec = random.choices([s[0] for s in SPECIALTY], [s[1] for s in SPECIALTY])[0]
    base_decile = random.choices(range(1, 11), [14, 13, 12, 11, 10, 10, 9, 8, 7, 6])[0]
    if spec == 'Endocrinology':
        base_decile = min(10, base_decile + 3)
    tier = 'A' if base_decile >= 8 else ('B' if base_decile >= 5 else 'C')
    hcps.append(dict(HCP_ID=f"HCP-{i:05d}", HCP_NAME=f"Dr. {random.choice(FIRST)} {random.choice(LAST)}",
                     SPECIALTY=spec, TERRITORY_ID=terr[0], CITY=terr[1].split()[0],
                     PRACTICE_SETTING=random.choice(SETTING), DECILE=base_decile, TARGET_TIER=tier,
                     YEARS_IN_PRACTICE=random.randint(3, 35)))
write_csv('hcps.csv', hcps)

# --- monthly Rx: Oct 2025 - Sep 2026 ---
MONTHS = [date(2025, 10, 1)]
while len(MONTHS) < 12:
    d = MONTHS[-1]
    MONTHS.append(date(d.year + (d.month == 12), d.month % 12 + 1, 1))

rx = []
for h in hcps:
    volume = h['DECILE'] * random.uniform(2.0, 3.5)  # monthly T2D market TRx
    share = {'BR-01': random.uniform(0.18, 0.32), 'BR-02': random.uniform(0.10, 0.22),
             'BR-03': random.uniform(0.18, 0.30), 'BR-04': random.uniform(0.12, 0.25)}
    for mi, m in enumerate(MONTHS):
        s = dict(share)
        growth = 1 + 0.012 * mi  # our brand grows slowly overall
        s['BR-01'] *= growth
        if h['TERRITORY_ID'] == 'T07' and m >= date(2026, 5, 1):
            s['BR-01'] *= 0.62  # formulary change -> access problem
            s['BR-03'] *= 1.15
        if h['TERRITORY_ID'] == 'T03' and mi >= 5:
            s['BR-02'] *= 1 + 0.09 * (mi - 4)  # competitor surge
            s['BR-01'] *= 1 - 0.035 * (mi - 4)
        tot = sum(s.values())
        market = max(1, round(volume * random.uniform(0.85, 1.15)))
        for b, v in s.items():
            trx = round(market * v / tot)
            nrx = round(trx * random.uniform(0.25, 0.40))
            rx.append(dict(HCP_ID=h['HCP_ID'], BRAND_ID=b, MONTH=m.isoformat(),
                           TRX=trx, NRX=nrx, MARKET_TRX=market))
write_csv('rx_monthly.csv', rx)

# --- calls (CRM activity) ---
CHANNEL = [('In-person', 0.62), ('Remote video', 0.18), ('Phone', 0.12), ('Email', 0.08)]
calls = []
cid = 0
neglected = set(h['HCP_ID'] for h in random.sample([h for h in hcps if h['DECILE'] >= 8], 40))
for h in hcps:
    n = {'A': random.randint(8, 14), 'B': random.randint(3, 8), 'C': random.randint(0, 3)}[h['TARGET_TIER']]
    for _ in range(n):
        d = date(2025, 10, 1) + timedelta(days=random.randint(0, 364))
        if h['HCP_ID'] in neglected and d > date(2026, 6, 30):
            continue  # no recent calls for neglected high-value HCPs
        cid += 1
        terr = next(t for t in territories if t['TERRITORY_ID'] == h['TERRITORY_ID'])
        calls.append(dict(CALL_ID=f"CALL-{cid:06d}", HCP_ID=h['HCP_ID'], REP_ID=terr['REP_ID'],
                          TERRITORY_ID=h['TERRITORY_ID'], CALL_DATE=d.isoformat(),
                          CHANNEL=random.choices([c[0] for c in CHANNEL], [c[1] for c in CHANNEL])[0],
                          BRAND_DETAILED='Glucavia', SAMPLES_DROPPED=random.choice([0, 0, 2, 4, 6]),
                          DURATION_MIN=random.choice([5, 8, 10, 12, 15, 20])))
calls.sort(key=lambda c: c['CALL_DATE'])
write_csv('calls.csv', calls)

# --- call notes (free text) ---
NOTES = {
    'access': [
        "Dr. {n} said most of her patients on {payer} now need prior authorization for Glucavia since the formulary update. She is defaulting to Empaflo to avoid paperwork.",
        "Discussed Glucavia for an obese T2D patient. HCP likes the data but PA rejections from {payer} are frustrating; asked if we have a hub or PA support line.",
        "HCP reports {payer} moved Glucavia to non-preferred tier. Three patients switched last month after PA was denied. Requested copay card details.",
        "Access is the main barrier here. Dr. {n} says the step-therapy requirement (metformin + SGLT2 first) makes Glucavia hard to start.",
    ],
    'efficacy': [
        "Dr. {n} asked for HbA1c reduction data versus Sematra. Shared the head-to-head summary; he wants real-world data from Indian patients.",
        "HCP questioned durability of weight loss beyond 52 weeks. Left the extension study reprint.",
    ],
    'safety': [
        "Dr. {n} mentioned two elderly patients stopped Glucavia due to nausea and vomiting in the first month. Discussed slow titration schedule.",
        "GI tolerability concern raised again. HCP prefers to start low and titrate every 4 weeks. Asked for patient education leaflets.",
        "HCP asked about pancreatitis risk; referred to medical information for a formal response.",
    ],
    'cost': [
        "Patient affordability is the issue for self-pay patients. Dr. {n} asked whether a lower-cost pen or patient assistance program is coming.",
        "Cost discussion: HCP says monthly out-of-pocket is too high compared with generic DPP-4s.",
    ],
    'competitor': [
        "Sematra rep has been visiting weekly with lunch programs. Dr. {n} is trialing Sematra in new starts because of the once-weekly pen device.",
        "HCP says Sematra offered a free starter kit program; she has moved several new patients to it. Need to counter with our titration support.",
        "Competitive pressure from Sematra is strong here. Dr. {n} sees them as equivalent and chooses based on samples and device.",
    ],
    'positive': [
        "Very positive call. Dr. {n} has started 6 new patients on Glucavia this month and is seeing good HbA1c and weight results.",
        "HCP happy with Glucavia outcomes in obese T2D patients. Interested in speaking at the regional CME event.",
        "Good discussion on CV benefit data. Dr. {n} will consider Glucavia earlier for patients with established CVD.",
    ],
}
PAYERS = ['StarHealth', 'CareFirst India', 'MediAssure', 'National Health Cover']


def pick_category(terr, d):
    if terr == 'T07' and d >= date(2026, 5, 1):
        return random.choices(list(NOTES), [55, 8, 10, 12, 5, 10])[0]
    if terr == 'T03' and d >= date(2026, 3, 1):
        return random.choices(list(NOTES), [8, 10, 10, 10, 45, 17])[0]
    return random.choices(list(NOTES), [12, 15, 15, 13, 12, 33])[0]


hcp_by_id = {h['HCP_ID']: h for h in hcps}
notes = []
note_calls = [c for c in calls if c['CHANNEL'] in ('In-person', 'Remote video') and random.random() < 0.18]
for i, c in enumerate(note_calls, 1):
    d = date.fromisoformat(c['CALL_DATE'])
    cat = pick_category(c['TERRITORY_ID'], d)
    surname = hcp_by_id[c['HCP_ID']]['HCP_NAME'].split()[-1]
    text = random.choice(NOTES[cat]).format(n=surname, payer=random.choice(PAYERS))
    if random.random() < 0.3:
        text += " Follow-up scheduled in two weeks."
    notes.append(dict(NOTE_ID=f"NOTE-{i:05d}", CALL_ID=c['CALL_ID'], HCP_ID=c['HCP_ID'],
                      TERRITORY_ID=c['TERRITORY_ID'], NOTE_DATE=c['CALL_DATE'], NOTE_TEXT=text))
write_csv('call_notes.csv', notes)

# --- approved messaging & objection-handling docs (for Cortex Search) ---
DOCS = [
    ('DOC-01', 'Glucavia Core Messaging Guide',
     "Glucavia is a once-weekly GLP-1 receptor agonist for adults with type 2 diabetes. Key messages: (1) Glucavia lowers HbA1c by up to 1.8 percentage points from baseline. (2) Patients lost an average of 6.2 kg at 52 weeks. (3) Glucavia demonstrated a reduction in major adverse cardiovascular events in patients with established CVD. Position Glucavia after metformin for patients who need both glycemic control and weight reduction."),
    ('DOC-02', 'Objection Handling: Access and Prior Authorization',
     "When an HCP raises prior authorization or formulary barriers: acknowledge the burden, confirm the payer, and offer the Glucavia Access Hub (PA form pre-fill, appeal templates, 48-hour turnaround). For step-therapy requirements, document metformin failure and HbA1c above 7.5% in the PA submission. Escalate payers with denial rates above 30% to Market Access."),
    ('DOC-03', 'Objection Handling: GI Tolerability',
     "Nausea and vomiting are the most common adverse reactions and are usually mild to moderate and transient. Recommend starting at 0.25 mg and titrating every 4 weeks. Advise patients to eat smaller meals and stop eating when full. Elderly patients may benefit from a slower titration schedule. Do not make comparative safety claims versus competitors."),
    ('DOC-04', 'Objection Handling: Cost and Affordability',
     "For self-pay patients, offer the Glucavia Patient Support Program: first month free and up to 40% off the monthly price for eligible patients. Discuss total cost of care, including the potential to reduce the need for additional agents. Never discuss pricing negotiated with specific payers."),
    ('DOC-05', 'Competitive Positioning vs Sematra',
     "Glucavia and Sematra are both once-weekly GLP-1 RAs. Glucavia differentiators: proven cardiovascular outcome benefit and a single-dose pen with a simpler titration. Do not disparage competitor products. Focus on patient support services and the CV outcomes label."),
    ('DOC-06', 'Field Engagement Guidelines',
     "Tier A HCPs (deciles 8-10) should be engaged at least monthly, Tier B at least quarterly. Any Tier A HCP without a call in 60 days should be prioritized in the next call plan. Record key discussion points and objections in the call note within 24 hours."),
    ('DOC-07', 'Medical Information Referral Policy',
     "Off-label questions, pancreatitis, thyroid C-cell tumor risk and pregnancy questions must be referred to Medical Information. Representatives must not answer these directly. Log the referral in CRM."),
    ('DOC-08', 'Formulary Update Bulletin May 2026',
     "Effective 1 May 2026, StarHealth moved Glucavia from preferred to non-preferred tier in the West region, requiring prior authorization and documented failure of metformin plus an SGLT2 inhibitor. Field teams in Pune and Mumbai should proactively offer Access Hub support."),
]
write_csv('messaging_docs.csv', [dict(DOC_ID=d[0], TITLE=d[1], CONTENT=d[2]) for d in DOCS])

print(f"brands={len(brands)} territories={len(territories)} hcps={len(hcps)} rx_monthly={len(rx)} "
      f"calls={len(calls)} call_notes={len(notes)} messaging_docs={len(DOCS)}")
