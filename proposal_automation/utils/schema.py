from pydantic import BaseModel, Field
from typing import List, Optional


class Page(BaseModel):
    """Schema for a wiki page to create or update."""
    filename: str = Field(..., description="Filename for the page, e.g. 'skill-python.md'")
    title: str = Field(..., description="Title of the page, e.g. 'Python Programming'")
    type: str = Field(..., description="Type of the page, e.g. 'skill', 'experience', 'project', 'education', 'certification', 'tool', 'others'")
    action: str = Field(..., description="Action to take: 'create', 'update', or 'skip'")
    content: Optional[str] = Field(None, description="Markdown content for the page (required if action is create/update)")


class IndexEntry(BaseModel):
    """Schema for an entry to add or update in the wiki index."""
    filename: str = Field(..., description="Filename of the page to link in the index, e.g. 'skill-python.md'")
    title: str = Field(..., description="Title to display in the index, e.g. 'Python Programming'")
    type: str = Field(..., description="Type of the entry, e.g. 'skill', 'experience', 'project', 'education', 'certification', 'tool', 'others'")
    summary: str = Field(..., description="One-line summary of that page to include in the index, e.g. '5+ years experience, used in data pipelines and ML projects'")
    

class IngestedDocument(BaseModel):
    """Schema for an ingested document."""
    entities_found: List[str] = Field(..., description="List of career-relevant entities found in the document.")
    pages: List[Page] = Field(..., description="List of pages to create or update, with filename, title, type, action, and content.")
    index_entries: List[IndexEntry] = Field(..., description="List of entries to add/update in the wiki index, with filename, title, type, and summary.")
    

class SelectedPages(BaseModel):
    """Schema for selected pages relevant to a job description."""
    filenames: List[str] = Field(..., description="List of filenames of pages relevant to the job description.")



    