from urllib.parse import urlencode

SEARCH_URL = "https://www.upwork.com/nx/search/jobs/"

# Fixed enum values from Upwork's UI
CONTRACTOR_TIER = {
    "entry":        "1",
    "intermediate": "2", 
    "expert":       "3",
}

AMOUNT_BUCKETS = {
    "lt100":    "0-99",
    "100-500":  "100-499",
    "500-1k":   "500-999",
    "1k-5k":    "1000-4999",
    "5k+":      "5000-9999",
}

DURATION = {
    "lt_month": "week",       # Less than 1 month
    "1_3mo":    "month",      # 1–3 months
    "3_6mo":    "semester",   # 3–6 months
    "gt_6mo":   "ongoing",    # 6+ months
}

WORKLOAD = {
    "lt30":  "as_needed",   # < 30 hrs/week
    "gt30":  "full_time",   # > 30 hrs/week
}

CLIENT_HIRES = {
    "none": "0",
    "1-9":  "1-9",
    "10+":  "10-",
}

def build_search_url(params: dict) -> str:
    """Build url with parameters."""
    p = {}

    # Query & pagination
    if q := params.get("query"):
        p["q"] = q
    if sort := params.get("sort"):
        p["sort"] = sort                          # "recency" | "relevance"
    if page := params.get("page"):
        p["page"] = page
    if per_page := params.get("per_page"):
        p["per_page"] = per_page

    # Job type  →  t params
    # hourly=True  fixed=False  → t=0  (hourly only — rarely used, usually omit)
    # hourly=False fixed=True   → t=1
    # both or neither           → omit t entirely
    hourly = params.get("hourly", False)
    fixed  = params.get("fixed",  False)
    if fixed and not hourly:
        p["t"] = "1"
    elif hourly and not fixed:
        p["t"] = "0"
    # else: omit → returns all types

    # Contractor tier  →  contractor_tier=1,2,3 
    if tiers := params.get("tier"):
        p["contractor_tier"] = ",".join(
            CONTRACTOR_TIER[t] for t in tiers if t in CONTRACTOR_TIER
        )

    # Hourly rate  →  hourly_rate=min-max 
    h_min = params.get("hourly_min", "")
    h_max = params.get("hourly_max", "")
    if h_min or h_max:
        p["hourly_rate"] = f"{h_min}-{h_max}"

    # Fixed price  →  amount=bucket1,bucket2 OR amount=min-max 
    if buckets := params.get("fixed_buckets"):
        p["amount"] = ",".join(
            AMOUNT_BUCKETS[b] for b in buckets if b in AMOUNT_BUCKETS
        )
    elif params.get("fixed_min") or params.get("fixed_max"):
        f_min = params.get("fixed_min", "")
        f_max = params.get("fixed_max", "")
        p["amount"] = f"{f_min}-{f_max}"

    # Client hires  →  client_hires=0,1-9,10-
    if hires := params.get("client_hires"):
        p["client_hires"] = ",".join(
            CLIENT_HIRES[h] for h in hires if h in CLIENT_HIRES
        )

    # Project duration  →  duration_v3=week,month,... 
    if durations := params.get("duration"):
        p["duration_v3"] = ",".join(
            DURATION[d] for d in durations if d in DURATION
        )

    # Workload  →  workload=as_needed,full_time 
    if workloads := params.get("workload"):
        p["workload"] = ",".join(
            WORKLOAD[w] for w in workloads if w in WORKLOAD
        )

    # Location / timezone 
    if loc := params.get("location"):
        p["location"] = loc
    if tz := params.get("timezone"):
        p["timezone"] = tz

    # Contract-to-hire 
    if params.get("contract_to_hire"):
        p["contract_to_hire"] = "true"

    return SEARCH_URL + "?" + urlencode(p, safe=",")