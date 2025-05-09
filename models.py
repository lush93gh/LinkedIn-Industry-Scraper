"""Pydantic contract reflecting LinkedIn fields."""

from __future__ import annotations
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
import json


class ProfileData(BaseModel):
    id: str  # derived from custom public URL or public identifier
    headline: Optional[str] = None
    pronouns: Optional[str] = None
    url: str = Field(..., alias="Custom public profile URL")
    industry: Optional[str] = None
    about: Optional[str] = Field(None, alias="About (Summary)")
    experience: List[Dict[str, Any]] = Field(
        default_factory=list, alias="Experience (past positions)"
    )
    career_break: Optional[Dict[str, Any]] = Field(None, alias="Career break")
    services: List[Any] = Field(default_factory=list, alias="Services")
    featured: List[Any] = Field(default_factory=list, alias="Featured")
    skills: List[str] = Field(default_factory=list, alias="Skills")
    endorsements: List[Any] = Field(default_factory=list, alias="Endorsements")
    licenses_certifications: List[Any] = Field(
        default_factory=list, alias="Licenses & Certifications"
    )
    projects: List[Any] = Field(default_factory=list, alias="Projects")
    courses: List[Any] = Field(default_factory=list, alias="Courses")
    recommendations: List[Any] = Field(default_factory=list, alias="Recommendations")
    volunteer_experience: List[Any] = Field(
        default_factory=list, alias="Volunteer Experience"
    )
    publications: List[Any] = Field(default_factory=list, alias="Publications")
    patents: List[Any] = Field(default_factory=list, alias="Patents")
    honors_awards: List[Any] = Field(default_factory=list, alias="Honors & Awards")
    test_scores: List[Any] = Field(default_factory=list, alias="Test Scores")
    languages: List[Any] = Field(default_factory=list, alias="Languages")
    organizations: List[Any] = Field(default_factory=list, alias="Organizations")
    causes: List[Any] = Field(default_factory=list, alias="Causes")
    interests: List[Any] = Field(default_factory=list, alias="Interests")
    connections: Optional[int] = Field(None, alias="Connections / Follower count")
    open_to: Optional[Dict[str, Any]] = Field(
        None, alias="Open to (Work / Hiring / Providing Services)"
    )

    class Config:
        allow_population_by_field_name = True
        orm_mode = True

    def csv_headers() -> list[str]:  # type: ignore[override]
        return [
            "Headline",
            "Pronouns",
            "Custom public profile URL",
            "Industry",
            "About (Summary)",
            "Experience (past positions)",
            "Career break",
            "Services",
            "Featured",
            "Skills",
            "Endorsements",
            "Licenses & Certifications",
            "Projects",
            "Courses",
            "Recommendations",
            "Volunteer Experience",
            "Publications",
            "Patents",
            "Honors & Awards",
            "Test Scores",
            "Languages",
            "Organizations",
            "Causes",
            "Interests",
            "Connections / Follower count",
            "Open to (Work / Hiring / Providing Services)",
        ]

    def to_csv_row(self) -> dict[str, Any]:
        def _j(val):
            return (
                json.dumps(val, ensure_ascii=False)
                if isinstance(val, (list, dict))
                else val
            )

        return {
            "Headline": self.headline,
            "Pronouns": self.pronouns,
            "Custom public profile URL": self.url,
            "Industry": self.industry,
            "About (Summary)": self.about,
            "Experience (past positions)": _j(self.experience),
            "Career break": _j(self.career_break),
            "Services": _j(self.services),
            "Featured": _j(self.featured),
            "Skills": _j(self.skills),
            "Endorsements": _j(self.endorsements),
            "Licenses & Certifications": _j(self.licenses_certifications),
            "Projects": _j(self.projects),
            "Courses": _j(self.courses),
            "Recommendations": _j(self.recommendations),
            "Volunteer Experience": _j(self.volunteer_experience),
            "Publications": _j(self.publications),
            "Patents": _j(self.patents),
            "Honors & Awards": _j(self.honors_awards),
            "Test Scores": _j(self.test_scores),
            "Languages": _j(self.languages),
            "Organizations": _j(self.organizations),
            "Causes": _j(self.causes),
            "Interests": _j(self.interests),
            "Connections / Follower count": self.connections,
            "Open to (Work / Hiring / Providing Services)": _j(self.open_to),
        }
