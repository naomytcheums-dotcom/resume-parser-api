from pydantic import BaseModel, Field


class ExperienceEntry(BaseModel):
    title: str = ""
    company: str = ""
    duration: str = ""
    description: str = ""


class EducationEntry(BaseModel):
    degree: str = ""
    institution: str = ""
    year: str = ""


class ParseResumeResponse(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = Field("", description="A short professional summary extracted or inferred from the resume.")
    skills: list[str] = []
    experience: list[ExperienceEntry] = []
    education: list[EducationEntry] = []
