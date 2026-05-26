from pathlib import Path
from datetime import datetime

from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from logger import Logger

logger = Logger().get_logger()


def init_files(
    schema_file: Path,
    index_file: Path,
    log_file: Path
)-> None:
    """Creating the initial required files."""

    if not schema_file.exists():
        schema_file.write_text(
            "# Career Wiki Schema\n\n"
            f"Created: {datetime.now().strftime('%Y-%m-%d')}\n\n"
            "## Page Types\n"
            "- `skill-<name>.md` — a technical or soft skill\n"
            "- `exp-<company>-<role>.md` — a work experience entry\n"
            "- `project-<name>.md` — a project\n"
            "- `edu-<degree>.md` — education\n"
            "- `cert-<name>.md` — certification\n"
            "- `tool-<name>.md` — a specific tool or technology\n\n"
            "## Operations\n"
            "- ingest(path, doc_type) — extract career data from a document\n"
            "- match_job(jd_text) — score yourself against a job description\n"
            "- generate_cover_letter(jd_text) — write a tailored cover letter\n"
            "- query(question) — ask about your own profile\n"
            "- lint() — find broken links and gaps\n",
            encoding="utf-8"
        )
        logger.debug("✅ Created SCHEMA.md")

    if not index_file.exists():
        index_file.write_text(
            "# Career Wiki Index\n\n"
            f"_Last updated: {datetime.now().strftime('%Y-%m-%d')}_\n\n"
            "## Skills\n\n"
            "## Experience\n\n"
            "## Projects\n\n"
            "## Education & Certifications\n\n"
            "## Achievements\n\n"
            "## Tools\n\n"
            "## Others\n\n",
            encoding="utf-8"
        )
        logger.debug("✅ Created wiki/index.md")

    if not log_file.exists():
        log_file.write_text(
            "# Ingest Log\n\n",
            encoding="utf-8"
        )
        logger.debug("✅ Created wiki/log.md")


#TODO: yield for long text
def load_source(path: Path)-> str:
        """Reading the source file"""

        ext = path.suffix.lower()
        logger.debug(f"📂 Loading {path.name}...")
 
        if ext == ".pdf":
            docs = PyPDFLoader(str(path)).load()
        elif ext in (".md", ".markdown"):
            docs = UnstructuredMarkdownLoader(str(path)).load()
        else:
            docs = TextLoader(str(path), encoding="utf-8").load()
 
        full_text = "\n\n".join(d.page_content for d in docs)
 
        if len(full_text) > 14_000:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=12_000, chunk_overlap=500
            )
            chunks = splitter.split_text(full_text)
            logger.debug(f"Split into {len(chunks)} chunks — processing first chunk")
            return chunks[0]
        return full_text