import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
RESUME_PATH = ROOT_DIR / "resume.txt"
RESULTS_DIR = ROOT_DIR / "results"
DB_PATH = ROOT_DIR / "job_search.db"

RESUME_TEXT = RESUME_PATH.read_text()

TC_MIN = 700_000
TC_MAX = 2_000_000

# West Coast metros + remote
LOCATION_KEYWORDS = [
    "remote", "seattle", "bellevue", "redmond", "kirkland", "tacoma",
    "san francisco", "sf", "bay area", "silicon valley", "san jose",
    "palo alto", "menlo park", "mountain view", "sunnyvale", "santa clara",
    "los angeles", "la", "santa monica", "venice", "culver city",
    "san diego", "portland", "oregon", "washington", "california",
    "distributed", "work from home", "wfh",
]

# Job title patterns that match Matt's level (VP, SVP, CTO, Head-of, Distinguished)
TITLE_PATTERNS = [
    r"\bvp\b",
    r"vice president",
    r"\bsvp\b",
    r"senior vice president",
    r"head of (software|engineering|ai|platform|infrastructure|technology|product engineering)",
    r"\bcto\b",
    r"chief (technology|ai|engineering|technical)",
    r"distinguished (engineer|software|technologist)",
    r"\bfellow\b",
    r"(senior |staff )?director of (software |platform |ai |engineering |cloud )",
    r"senior director",
    r"director of engineering",
    r"director of software",
    r"director of ai",
    r"director of platform",
    r"director of infrastructure",
    r"director of cloud",
    r"director of technology",
    r"engineering director",
    r"gm of engineering",
    r"general manager.*engineering",
    r"principal (engineer|architect)",
]

# Greenhouse ATS slugs for companies that pay $700K+ at VP/Director level
GREENHOUSE_COMPANIES = [
    # AI-first
    "anthropic",
    "openai",
    "cohere",
    "adept",
    "inflection",
    "characterai",
    "runway",
    "harvey",
    "imbue",
    "together",
    "mistral",
    "perplexity",
    "groq",
    "cerebras",
    "sambanova",
    "cresta",
    "cognitiveresearch",
    "aisera",
    "moveworks",
    "glean",
    "writer",
    "jasper",
    "covariant",
    "nuro",
    "wayve",
    "aurora1",
    # Cloud / Infra / Data
    "databricks",
    "snowflake",
    "confluent",
    "hashicorp",
    "dbtlabs",
    "cloudflare",
    "fastly",
    "netlify",
    "vercel",
    "mongodb",
    "elastic",
    "couchbase",
    "singlestore",
    "timescale",
    "cockroachlabs",
    # Fintech
    "stripe",
    "brex",
    "rippling",
    "deel",
    "ramp",
    "mercury",
    "plaid",
    "chime",
    "robinhood",
    "coinbase",
    "anchorage",
    "figma",
    "notion",
    "linear",
    "loom",
    "retool",
    # Enterprise SaaS
    "servicenow",
    "salesforce",
    "workday",
    "zendesk",
    "okta",
    "pagerduty",
    "amplitude",
    "mixpanel",
    "segment",
    "miro",
    "asana",
    # Marketplace / Consumer
    "airbnb",
    "doordash",
    "instacart",
    "lyft",
    "waymo",
    "cruise",
]

# Lever ATS slugs
LEVER_COMPANIES = [
    "netflix",
    "twitter",
    "square",
    "dropbox",
    "box",
    "twilio",
    "attentive",
    "benchling",
    "lattice",
    "coda",
    "scale-ai",
    "replit",
    "weights-and-biases",
    "huggingface",
    "modal-labs",
    "modal",
    "anyscale",
    "ray",
    "vanta",
    "drata",
    "modern-treasury",
    "finix",
    "payitoff",
    "persona",
    "sardine",
]

# Direct web search queries (used by websearch source)
# Each query targets a different segment of the job market
SEARCH_QUERIES = [
    'site:linkedin.com/jobs "VP of Engineering" OR "VP Engineering" "remote OR Seattle OR "San Francisco"',
    '"VP of AI" OR "VP of ML" OR "head of AI" engineering executive Seattle OR "San Francisco" OR remote',
    '"senior director" OR "VP" engineering "agentic AI" OR "LLM" OR "generative AI" executive',
    '"distinguished engineer" OR "principal engineer" AI cloud Seattle OR remote 2024 OR 2025',
    'site:jobs.lever.co "VP Engineering" OR "Head of Engineering" remote OR Seattle',
    'site:boards.greenhouse.io "VP Engineering" OR "Senior Director Engineering" remote OR Seattle',
]

ANTHROPIC_MODEL = "claude-sonnet-4-6"
