from dataclasses import dataclass, field
from typing import Optional


@dataclass
class JobListing:
    id: str
    title: str
    company: str
    location: str
    url: str
    source: str
    description: str = ""
    salary_info: str = ""
    posted_date: str = ""
    # Filled in by analyzer
    fit_score: Optional[int] = None
    fit_rationale: str = ""
    tc_likelihood: str = ""
    is_remote: bool = False

    def location_lower(self) -> str:
        return (self.location or "").lower()

    def title_lower(self) -> str:
        return (self.title or "").lower()
