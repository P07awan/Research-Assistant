# import necessary libraries
import os
import re
import time
from typing import Iterator, Dict, Any
from io import BytesIO
from docling.datamodel.base_models import InputFormat
from docling_core.types.io import DocumentStream
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from langchain_core.documents import Document as LCDocument
from langchain_core.document_loaders import BaseLoader
from docling.datamodel.accelerator_options import (
    AcceleratorDevice,
    AcceleratorOptions
)

# Preprocessing Patterns 
PAT_FORMULA = re.compile(r"<!--\s*formula-not-decoded\s*-->", flags=re.IGNORECASE)
PAT_IMAGE = re.compile(r"<!--\s*image\s*-->", flags=re.IGNORECASE)
PAT_HTML_COMMENT = re.compile(r"<!--.*?-->", flags=re.DOTALL)
PAT_MULTI_NL = re.compile(r"\n{3,}")

# Text Preprocessing 
def text_preprocessing(raw_text: str) -> str:
    """Clean up Docling markdown output."""
    text = PAT_FORMULA.sub(" [FORMULA] ", raw_text)
    text = PAT_IMAGE.sub(" [IMAGE] ", text)
    text = PAT_HTML_COMMENT.sub("", text)
    text = PAT_MULTI_NL.sub("\n\n", text)
    return text.strip()


# Docling PDF Loader
class DoclingPDFLoader(BaseLoader):
    """
    Load a local PDF, convert to markdown using Docling,
    and return as LangChain LCDocument objects.
    """

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.metadata: Dict[str, Any] = {}

        # Accelerator options for faster processing
        accelerator_options = AcceleratorOptions(
            num_threads=8, device=AcceleratorDevice.AUTO
        )

        # Pipeline configuration
        pipeline_options = PdfPipelineOptions()
        pipeline_options.accelerator_options = accelerator_options
        pipeline_options.do_ocr = False
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.do_cell_matching = True
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

        # Document converter
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options,
                )
            }
        )

    def lazy_load(self) -> Iterator[LCDocument]:
        """Stream LangChain Documents after converting local PDF to markdown."""

        process_start = time.time()

        # Read PDF from local storage as bytes
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")
        try:
            with open(self.file_path, "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read local file: {e}")

        # Wrap bytes into a BytesIO stream
        buf = BytesIO(pdf_bytes)
        source = DocumentStream(name=os.path.basename(self.file_path), stream=buf)

        # Convert using Docling
        docling_doc = self.converter.convert(source).document
        process_time = time.time() - process_start
        print(f"✅ Book processed successfully in {process_time:.2f} seconds")

        # Export to markdown
        print("🔄 Converting to markdown format...")
        convert_start = time.time()
        text = docling_doc.export_to_markdown()
        convert_time = time.time() - convert_start
        print(f"✅ Conversion complete in {convert_time:.2f} seconds")

        # Metadata
        self.metadata = {
            "source": self.file_path,
            "format": "paper",
            "page_count": len(getattr(docling_doc, "pages", [])),
            "process_time": process_time,
            "convert_time": convert_time,
        }

        # Yield LangChain Document
        yield LCDocument(
            page_content=text_preprocessing(text),
            metadata=self.metadata
        )
