from curses import raw
from pathlib import Path
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from logger import Logger
from proposal_automation.utils.prompt import *
from proposal_automation.utils.schema import *
from proposal_automation.utils.helper import *
from proposal_automation.utils.prompt_builder import *
from proposal_automation.llm.llm import invoke_llm

logger = Logger().get_logger()


class PortfolioWiki:
    """Intelligent Portfolio Wikipedia"""

    def __init__(self,root=".", model="gpt-4o-mini"):
        """init wiki files and llm model"""

        self.root = Path(root)
        self.sources_dir = self.root/"sources"
        self.wiki_dir = self.root/"portfolio_wiki"
        self.schema_file = self.root/"SCHEMA.md"
        self.index_file = self.wiki_dir/"index.md"
        self.log_file = self.wiki_dir/"log.md"

        self.sources_dir.mkdir(parents=True, exist_ok=True)
        self.wiki_dir.mkdir(parents=True, exist_ok=True)

        self.llm = ChatOpenAI(model=model, temperature=0.0)

        init_files(self.schema_file,self.index_file, self.log_file)

    def _read_index(self):
        return self.index_file.read_text("utf-8")
    
    def _read_all_wiki(self):
        pages = ""
        for f in sorted(self.wiki_dir.glob("*.md")):
            if f.name in ("index.md", "log.md"):
                continue
            pages += f"\n\n{'='*40}\n### {f.stem}\n{'='*40}\n"
            pages += f.read_text(encoding="utf-8")
        return pages
    
    def _write_page(self,filename: str, content: str):
        (self.wiki_dir / filename).write_text(content, encoding="utf-8")
        logger.debug(f" Write {filename} file.")

    # not used right now, only if we want to update wiki
    def _update_index(self, entries: list[IndexEntry]):
        text = self._read_index()
        lines = text.splitlines()

        section_map = {
            "skill":       "## Skills",
            "experience":  "## Experience",
            "project":     "## Projects",
            "education":   "## Education & Certifications",
            "certification": "## Education & Certifications",
            'achievement': "## Achievements",
            "tool":        "## Tools",
            "others":      "## Others"
        }

        for entry in entries:
            fn      = entry.filename
            title   = entry.title
            etype   = entry.type
            summary = entry.summary or ""
            row     = f"- **[{title}]({fn})** — {summary}"

            # removes old entry if exists 
            lines = [l for l in lines if fn not in l]

            # find the right section and insert
            section = section_map.get(etype, "## Others")
            for i, line in enumerate(lines):
                if line.strip() == section:
                    lines.insert(i + 1, row)
                    break
        
        # Update timestamp
        lines = [
            f"_Last updated: {datetime.now().strftime('%Y-%m-%d')}_"
            if l.startswith("_Last updated") else l
            for l in lines
        ]
        self.index_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _log(self, source_name: str, entities: list[str]):
        entry = (
            f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"**Source:** `{source_name}`\n"
            f"**Entities:** {', '.join(entities)}\n"
        )
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(entry)


    def show_index(self):
        """Print the current career wiki index."""
        logger.debug(f"Career Wiki Index: {len(self._read_index())} indexes")


    def list_pages(self) -> list[str]:
        return [
            f.name for f in sorted(self.wiki_dir.glob("*.md"))
            if f.name not in ("index.md", "log.md")
        ]
    

    def _read_selected_wiki(self, filenames: list[str]) -> str:
        """Read ONLY the specified wiki pages."""
        pages = ""
        for filename in filenames:
            p = self.wiki_dir / filename
            if p.exists():
                pages += f"\n\n{'='*40}\n### {p.stem}\n{'='*40}\n"
                pages += p.read_text(encoding="utf-8")
            else:
                logger.warning(f"Page not found: {filename}")
        return pages
    
    def ingest(self, source_path: str, doc_type: str = "auto") -> IngestedDocument:
        """
        Ingest a career document.
        Uses llm_ingest (structured output → IngestResult) — no JSON parsing.
        """
        path = Path(source_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {source_path}")
 
        logger.debug(f" 🔄 Ingesting: {path.name}  [type: {doc_type}]")

        source_text = load_source(path)
        index_text  = self._read_index()

        if not source_text:
            logger.warning("Source text is empty after loading.")
            return IngestedDocument(entities_found=[], pages=[], index_entries=[])
        
        logger.debug(f" 🤖 Extracting career entities... from source len: {len(source_text)}")

        # Returns a validated IngestResult Pydantic model with structured output parsing
        ingest_prompt = build_ingest_prompt(index_text, doc_type, source_text)

        #structured
        ingested_docs: IngestedDocument = invoke_llm(self.llm,ingest_prompt,IngestedDocument)

        for page in ingested_docs.pages:
            self._write_page(page.filename, page.content)
 
        if ingested_docs.index_entries:
            self._update_index(ingested_docs.index_entries)
 
        self._log(path.name, ingested_docs.entities_found)
 
        logger.debug(f" ✅ Done! Entities: {ingested_docs.entities_found}")
        return ingested_docs
    

    def _select_pages(self,job_title: str, job_description: str) -> list[str]:
        """
        Call 1 of 2: LLM reads the index (tiny) and returns
        only the filenames relevant to the task.
        """
        index_text = self._read_index()
        all_pages  = [f.name for f in self.wiki_dir.glob("*.md")
                      if f.name not in ("index.md", "log.md")]
 
        if not all_pages:
            return []
 
        select_pages_prompt = build_select_pages_prompt(index_text,job_description,job_description)

        #structured
        selcectd_pages: SelectedPages = invoke_llm(self.llm,select_pages_prompt,SelectedPages)

        #TODO Fallback: extract anything that looks like a filename
        valid = [f for f in selcectd_pages.filenames if f in all_pages]

        logger.debug(f" 📋 Fallback selected {len(valid)} pages: {valid}")
        logger.debug(f"Len of vailid and selected: {len(selcectd_pages.filenames)}, {len(valid)}")

        return valid
    
    def write_proposal(self,job_title:str, job_description: str, tone: str="professional") -> str:
        """Call 2 of 2: LLM reads the selected wiki pages + job description and writes a cover letter."""
        selected_files = self._select_pages(job_title,job_description)
        if not selected_files:
            logger.warning("No relevant pages found for the job description.")
            return ""
 
        selected_content = self._read_selected_wiki(selected_files)

        cover_letter_prompt = build_proposal_prompt(selected_content,job_title, job_description, tone)
        self.llm.temperature = 0.7
        response = self.llm.invoke(cover_letter_prompt)
        return response.content
    

    
    
    
    


    
    