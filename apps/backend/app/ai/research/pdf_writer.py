"""Native, Zero-Dependency PDF Writer for Phase 10L-D: Research Report Export.

Generates standards-compliant, publication-grade PDF 1.4 documents with multi-page pagination,
running headers and footers ("Page X of Y"), styled headings, word-wrapped paragraphs,
callout cards for epistemic claims and contradictions, formatted tables, and bibliography.
"""

from io import BytesIO
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple, Union
import structlog

logger = structlog.get_logger("pdf_writer")

# Page Dimensions (Standard A4 in points: 72 points per inch)
A4_WIDTH = 595.28
A4_HEIGHT = 841.89

# Typography & Color Palette
COLOR_PRIMARY = (0.08, 0.22, 0.40)      # Deep Navy #143866
COLOR_SECONDARY = (0.20, 0.35, 0.55)    # Slate Blue #33598c
COLOR_TEXT = (0.12, 0.14, 0.17)         # Charcoal #1f242b
COLOR_MUTED = (0.45, 0.48, 0.53)        # Cool Gray #737b87
COLOR_LIGHT_BG = (0.96, 0.97, 0.98)     # Soft Background #f5f7fa
COLOR_BORDER = (0.82, 0.85, 0.88)       # Border Gray #d1d9e0

# Epistemic Card Accent Colors
COLOR_FACT_BORDER = (0.13, 0.60, 0.35)       # Emerald Green
COLOR_FACT_BG = (0.94, 0.98, 0.95)
COLOR_INFERENCE_BORDER = (0.15, 0.45, 0.75)  # Sky/Navy Blue
COLOR_INFERENCE_BG = (0.94, 0.97, 1.00)
COLOR_CONTRA_BORDER = (0.85, 0.45, 0.10)     # Amber/Orange
COLOR_CONTRA_BG = (1.00, 0.97, 0.93)
COLOR_UNSUPPORTED_BORDER = (0.75, 0.25, 0.25)# Crimson/Gray
COLOR_UNSUPPORTED_BG = (0.99, 0.95, 0.95)


class NativePDFWriter:
    """Pure-Python, zero-dependency PDF document generator implementing standard PDF 1.4 specification."""

    def __init__(self, doc_title: str = "Research Report") -> None:
        self.doc_title = self._sanitize_text(doc_title)
        self.pages_content: List[List[str]] = []
        self.current_stream: List[str] = []
        
        # Margins & Geometry
        self.margin_left = 50.0
        self.margin_right = 50.0
        self.margin_top = 55.0
        self.margin_bottom = 55.0
        self.content_width = A4_WIDTH - self.margin_left - self.margin_right
        self.current_y = A4_HEIGHT - self.margin_top

        # Begin first page
        self._new_page()

    def _sanitize_text(self, text: Any) -> str:
        """Transliterates Unicode characters to safe WinAnsi/ASCII equivalents for standard Type 1 fonts."""
        if text is None:
            return ""
        s = str(text)
        # Unicode replacements for common punctuation & typographic symbols
        replacements = [
            ("\u2014", " -- "),   # em-dash
            ("\u2013", "-"),      # en-dash
            ("\u2018", "'"),      # left single quote
            ("\u2019", "'"),      # right single quote
            ("\u201c", '"'),      # left double quote
            ("\u201d", '"'),      # right double quote
            ("\u2022", "*"),      # bullet
            ("\u2026", "..."),    # ellipsis
            ("\u00a0", " "),      # non-breaking space
            ("\u2192", "->"),     # right arrow
            ("\u2190", "<-"),     # left arrow
            ("\u03b1", "alpha"),  # Greek letters
            ("\u03b2", "beta"),
            ("\u03b3", "gamma"),
            ("\u03c0", "pi"),
            ("\u2265", ">="),     # greater or equal
            ("\u2264", "<="),     # less or equal
            ("\u00b1", "+/-"),    # plus-minus
            ("\u00d7", "x"),      # multiplication
        ]
        for src, target in replacements:
            s = s.replace(src, target)

        # Remove control characters except newline and tab
        s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", s)
        # Encode as latin-1, replacing unmappable characters with '?'
        return s.encode("latin-1", "replace").decode("latin-1")

    def _escape_pdf_string(self, text: str) -> str:
        """Escapes parentheses and backslashes for PDF string literals."""
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def _estimate_char_width(self, font_name: str, font_size: float) -> float:
        """Estimates average character width in points for Helvetica."""
        if font_name == "/F2":  # Helvetica-Bold
            return font_size * 0.58
        elif font_name == "/F4":  # Courier (monospace)
            return font_size * 0.60
        else:  # Helvetica
            return font_size * 0.52

    def _wrap_text(self, text: str, max_width: float, font_name: str, font_size: float) -> List[str]:
        """Wraps text into lines that fit within max_width."""
        words = text.split(" ")
        lines: List[str] = []
        current_line: List[str] = []
        char_w = self._estimate_char_width(font_name, font_size)
        max_chars = max(10, int(max_width / char_w))

        curr_len = 0
        for w in words:
            w_len = len(w)
            if current_line and (curr_len + 1 + w_len) > max_chars:
                lines.append(" ".join(current_line))
                current_line = [w]
                curr_len = w_len
            else:
                current_line.append(w)
                curr_len += (w_len + 1 if current_line else w_len)

        if current_line:
            lines.append(" ".join(current_line))

        return lines or [""]

    def _check_space_or_page(self, required_height: float) -> None:
        """If current remaining space on page is less than required_height, starts a new page."""
        if (self.current_y - required_height) < self.margin_bottom:
            self._new_page()

    def _new_page(self) -> None:
        """Completes current page and initializes next page."""
        if self.current_stream:
            self.pages_content.append(self.current_stream)
        self.current_stream = []
        self.current_y = A4_HEIGHT - self.margin_top

    # -------------------------------------------------------------------------
    # Content Building Methods
    # -------------------------------------------------------------------------

    def add_title_block(
        self,
        title: str,
        research_question: str,
        confidence_str: str,
        model_name: str,
        report_id: str,
        detail_level: str,
    ) -> None:
        """Renders an academic cover header with colored title banner and metadata grid."""
        title_clean = self._sanitize_text(title)
        q_clean = self._sanitize_text(research_question)
        
        # Title block background banner
        banner_height = 80.0
        self._check_space_or_page(banner_height + 40.0)

        top_y = self.current_y
        # Soft accent rectangle behind title
        self.current_stream.append(
            f"q {COLOR_LIGHT_BG[0]:.3f} {COLOR_LIGHT_BG[1]:.3f} {COLOR_LIGHT_BG[2]:.3f} rg "
            f"{self.margin_left:.2f} {top_y - banner_height:.2f} {self.content_width:.2f} {banner_height:.2f} re f Q\n"
        )
        # Left accent stripe
        self.current_stream.append(
            f"q {COLOR_PRIMARY[0]:.3f} {COLOR_PRIMARY[1]:.3f} {COLOR_PRIMARY[2]:.3f} rg "
            f"{self.margin_left:.2f} {top_y - banner_height:.2f} 4.0 {banner_height:.2f} re f Q\n"
        )

        # Title text
        self.current_y = top_y - 24.0
        title_lines = self._wrap_text(title_clean, self.content_width - 24.0, "/F2", 16.0)
        for t_line in title_lines[:2]:
            self.current_stream.append(
                f"BT /F2 16.0 Tf {COLOR_PRIMARY[0]:.3f} {COLOR_PRIMARY[1]:.3f} {COLOR_PRIMARY[2]:.3f} rg "
                f"{self.margin_left + 14.0:.2f} {self.current_y:.2f} Td "
                f"({self._escape_pdf_string(t_line)}) Tj ET\n"
            )
            self.current_y -= 18.0

        # Subtitle / Research Question
        q_lines = self._wrap_text(f"Inquiry: {q_clean}", self.content_width - 24.0, "/F1", 9.5)
        for q_l in q_lines[:2]:
            self.current_stream.append(
                f"BT /F1 9.5 Tf {COLOR_SECONDARY[0]:.3f} {COLOR_SECONDARY[1]:.3f} {COLOR_SECONDARY[2]:.3f} rg "
                f"{self.margin_left + 14.0:.2f} {self.current_y:.2f} Td "
                f"({self._escape_pdf_string(q_l)}) Tj ET\n"
            )
            self.current_y -= 12.0

        self.current_y = top_y - banner_height - 12.0

        # Metadata badges row
        meta_text = f"Detail: {detail_level.upper()}  |  Confidence: {confidence_str}  |  Model: {model_name}  |  Report ID: {report_id}"
        self.current_stream.append(
            f"BT /F1 8.5 Tf {COLOR_MUTED[0]:.3f} {COLOR_MUTED[1]:.3f} {COLOR_MUTED[2]:.3f} rg "
            f"{self.margin_left:.2f} {self.current_y:.2f} Td "
            f"({self._escape_pdf_string(meta_text)}) Tj ET\n"
        )
        self.current_y -= 14.0

        # Divider line
        self.add_divider()

    def add_heading(self, text: str, level: int = 1) -> None:
        """Renders an H1, H2, or H3 heading with appropriate spacing and weights."""
        clean_text = self._sanitize_text(text)
        if level == 1:
            font_size = 13.0
            font = "/F2"
            color = COLOR_PRIMARY
            space_before = 18.0
            space_after = 8.0
            underline = True
        elif level == 2:
            font_size = 11.0
            font = "/F2"
            color = COLOR_SECONDARY
            space_before = 12.0
            space_after = 6.0
            underline = False
        else:
            font_size = 9.5
            font = "/F2"
            color = COLOR_TEXT
            space_before = 8.0
            space_after = 4.0
            underline = False

        self._check_space_or_page(space_before + font_size + space_after + 5.0)
        self.current_y -= space_before

        lines = self._wrap_text(clean_text, self.content_width, font, font_size)
        for l in lines:
            self.current_stream.append(
                f"BT {font} {font_size:.1f} Tf {color[0]:.3f} {color[1]:.3f} {color[2]:.3f} rg "
                f"{self.margin_left:.2f} {self.current_y:.2f} Td "
                f"({self._escape_pdf_string(l)}) Tj ET\n"
            )
            self.current_y -= (font_size + 2.0)

        if underline and level == 1:
            line_y = self.current_y + 2.0
            self.current_stream.append(
                f"q 0.75 w {COLOR_SECONDARY[0]:.3f} {COLOR_SECONDARY[1]:.3f} {COLOR_SECONDARY[2]:.3f} RG "
                f"{self.margin_left:.2f} {line_y:.2f} m {self.margin_left + self.content_width:.2f} {line_y:.2f} l S Q\n"
            )
            self.current_y -= 4.0

        self.current_y -= space_after

    def add_paragraph(
        self,
        text: str,
        font_size: float = 9.5,
        italic: bool = False,
        indent: float = 0.0,
    ) -> None:
        """Renders a word-wrapped paragraph of body text."""
        clean_text = self._sanitize_text(text)
        font = "/F3" if italic else "/F1"
        line_height = font_size + 3.5
        max_w = self.content_width - indent

        lines = self._wrap_text(clean_text, max_w, font, font_size)
        for l in lines:
            self._check_space_or_page(line_height)
            self.current_stream.append(
                f"BT {font} {font_size:.1f} Tf {COLOR_TEXT[0]:.3f} {COLOR_TEXT[1]:.3f} {COLOR_TEXT[2]:.3f} rg "
                f"{self.margin_left + indent:.2f} {self.current_y:.2f} Td "
                f"({self._escape_pdf_string(l)}) Tj ET\n"
            )
            self.current_y -= line_height

        self.current_y -= 3.0  # paragraph spacing

    def add_bullet(self, text: str, font_size: float = 9.0) -> None:
        """Renders a bulleted item with hanging indent."""
        clean_text = self._sanitize_text(text)
        font = "/F1"
        line_height = font_size + 3.0
        bullet_indent = 12.0
        max_w = self.content_width - bullet_indent

        lines = self._wrap_text(clean_text, max_w, font, font_size)
        for i, l in enumerate(lines):
            self._check_space_or_page(line_height)
            if i == 0:
                # Bullet symbol
                self.current_stream.append(
                    f"BT /F2 {font_size:.1f} Tf {COLOR_SECONDARY[0]:.3f} {COLOR_SECONDARY[1]:.3f} {COLOR_SECONDARY[2]:.3f} rg "
                    f"{self.margin_left:.2f} {self.current_y:.2f} Td (*) Tj ET\n"
                )
            self.current_stream.append(
                f"BT {font} {font_size:.1f} Tf {COLOR_TEXT[0]:.3f} {COLOR_TEXT[1]:.3f} {COLOR_TEXT[2]:.3f} rg "
                f"{self.margin_left + bullet_indent:.2f} {self.current_y:.2f} Td "
                f"({self._escape_pdf_string(l)}) Tj ET\n"
            )
            self.current_y -= line_height

        self.current_y -= 2.0

    def add_callout(self, title: str, text: str, style: str = "fact") -> None:
        """Renders a styled card with background fill and left colored accent border."""
        if style == "fact":
            border_c = COLOR_FACT_BORDER
            bg_c = COLOR_FACT_BG
        elif style == "inference":
            border_c = COLOR_INFERENCE_BORDER
            bg_c = COLOR_INFERENCE_BG
        elif style == "conflict":
            border_c = COLOR_CONTRA_BORDER
            bg_c = COLOR_CONTRA_BG
        else:  # unsupported
            border_c = COLOR_UNSUPPORTED_BORDER
            bg_c = COLOR_UNSUPPORTED_BG

        clean_title = self._sanitize_text(title)
        clean_text = self._sanitize_text(text)
        
        font_size = 8.5
        line_h = font_size + 2.5
        lines = self._wrap_text(clean_text, self.content_width - 20.0, "/F1", font_size)
        
        box_height = 14.0 + (len(lines) * line_h) + 8.0
        self._check_space_or_page(box_height + 6.0)

        top_y = self.current_y

        # Background fill
        self.current_stream.append(
            f"q {bg_c[0]:.3f} {bg_c[1]:.3f} {bg_c[2]:.3f} rg "
            f"{self.margin_left:.2f} {top_y - box_height:.2f} {self.content_width:.2f} {box_height:.2f} re f Q\n"
        )
        # Left border stroke
        self.current_stream.append(
            f"q {border_c[0]:.3f} {border_c[1]:.3f} {border_c[2]:.3f} rg "
            f"{self.margin_left:.2f} {top_y - box_height:.2f} 3.5 {box_height:.2f} re f Q\n"
        )
        # Light outer border
        self.current_stream.append(
            f"q 0.5 w {COLOR_BORDER[0]:.3f} {COLOR_BORDER[1]:.3f} {COLOR_BORDER[2]:.3f} RG "
            f"{self.margin_left:.2f} {top_y - box_height:.2f} {self.content_width:.2f} {box_height:.2f} re S Q\n"
        )

        # Card Title
        self.current_y = top_y - 12.0
        self.current_stream.append(
            f"BT /F2 9.0 Tf {border_c[0]:.3f} {border_c[1]:.3f} {border_c[2]:.3f} rg "
            f"{self.margin_left + 10.0:.2f} {self.current_y:.2f} Td "
            f"({self._escape_pdf_string(clean_title)}) Tj ET\n"
        )
        self.current_y -= 11.0

        # Card Body text
        for l in lines:
            self.current_stream.append(
                f"BT /F1 {font_size:.1f} Tf {COLOR_TEXT[0]:.3f} {COLOR_TEXT[1]:.3f} {COLOR_TEXT[2]:.3f} rg "
                f"{self.margin_left + 10.0:.2f} {self.current_y:.2f} Td "
                f"({self._escape_pdf_string(l)}) Tj ET\n"
            )
            self.current_y -= line_h

        self.current_y = top_y - box_height - 6.0

    def add_table(
        self,
        headers: List[str],
        rows: List[List[str]],
        col_widths: Optional[List[float]] = None,
    ) -> None:
        """Renders a data table with colored header, alternating row fills, and cell borders."""
        if not headers or not rows:
            return

        num_cols = len(headers)
        if not col_widths or len(col_widths) != num_cols:
            col_widths = [self.content_width / num_cols] * num_cols

        # Header Row Height
        header_h = 18.0
        self._check_space_or_page(header_h + 30.0)

        # Draw Header Background
        self.current_stream.append(
            f"q {COLOR_PRIMARY[0]:.3f} {COLOR_PRIMARY[1]:.3f} {COLOR_PRIMARY[2]:.3f} rg "
            f"{self.margin_left:.2f} {self.current_y - header_h:.2f} {self.content_width:.2f} {header_h:.2f} re f Q\n"
        )

        # Draw Header Text
        curr_x = self.margin_left
        for i, h in enumerate(headers):
            w = col_widths[i]
            h_clean = self._sanitize_text(h)
            self.current_stream.append(
                f"BT /F2 8.5 Tf 1.0 1.0 1.0 rg "
                f"{curr_x + 4.0:.2f} {self.current_y - 12.0:.2f} Td "
                f"({self._escape_pdf_string(h_clean[:int(w / 5.5)])}) Tj ET\n"
            )
            curr_x += w

        self.current_y -= header_h

        # Rows
        for r_idx, row in enumerate(rows):
            # Compute row height based on cell text lengths
            row_clean = [self._sanitize_text(c) for c in row]
            wrapped_cells = [
                self._wrap_text(row_clean[c_i] if c_i < len(row_clean) else "", col_widths[c_i] - 6.0, "/F1", 8.0)
                for c_i in range(num_cols)
            ]
            max_lines = max(len(c_lines) for c_lines in wrapped_cells) if wrapped_cells else 1
            row_h = max(15.0, max_lines * 9.5 + 4.0)

            self._check_space_or_page(row_h)

            # Alternate row background
            if r_idx % 2 == 1:
                self.current_stream.append(
                    f"q {COLOR_LIGHT_BG[0]:.3f} {COLOR_LIGHT_BG[1]:.3f} {COLOR_LIGHT_BG[2]:.3f} rg "
                    f"{self.margin_left:.2f} {self.current_y - row_h:.2f} {self.content_width:.2f} {row_h:.2f} re f Q\n"
                )

            # Row bottom border
            self.current_stream.append(
                f"q 0.5 w {COLOR_BORDER[0]:.3f} {COLOR_BORDER[1]:.3f} {COLOR_BORDER[2]:.3f} RG "
                f"{self.margin_left:.2f} {self.current_y - row_h:.2f} m {self.margin_left + self.content_width:.2f} {self.current_y - row_h:.2f} l S Q\n"
            )

            # Cell text
            curr_x = self.margin_left
            for c_i, c_lines in enumerate(wrapped_cells):
                w = col_widths[c_i]
                y_text = self.current_y - 9.0
                for line in c_lines:
                    self.current_stream.append(
                        f"BT /F1 8.0 Tf {COLOR_TEXT[0]:.3f} {COLOR_TEXT[1]:.3f} {COLOR_TEXT[2]:.3f} rg "
                        f"{curr_x + 4.0:.2f} {y_text:.2f} Td "
                        f"({self._escape_pdf_string(line)}) Tj ET\n"
                    )
                    y_text -= 9.5
                curr_x += w

            self.current_y -= row_h

        self.current_y -= 6.0

    def add_divider(self) -> None:
        """Renders a thin horizontal rule line."""
        self._check_space_or_page(10.0)
        self.current_stream.append(
            f"q 0.5 w {COLOR_BORDER[0]:.3f} {COLOR_BORDER[1]:.3f} {COLOR_BORDER[2]:.3f} RG "
            f"{self.margin_left:.2f} {self.current_y:.2f} m {self.margin_left + self.content_width:.2f} {self.current_y:.2f} l S Q\n"
        )
        self.current_y -= 10.0

    # -------------------------------------------------------------------------
    # PDF Compilation & Object Construction
    # -------------------------------------------------------------------------

    def build_pdf(self) -> bytes:
        """Assembles all pages, injects running headers & footers, builds xref, and returns PDF bytes."""
        # Flush active page
        if self.current_stream:
            self.pages_content.append(self.current_stream)
            self.current_stream = []

        total_pages = len(self.pages_content)
        if total_pages == 0:
            total_pages = 1
            self.pages_content = [[]]

        # Injects running header and running footer on each page
        for p_idx, stream_lines in enumerate(self.pages_content, start=1):
            page_decorations: List[str] = []

            # Running Header (pages 2+)
            if p_idx > 1:
                header_text = f"Nova-AI Scientific Research  |  {self.doc_title[:45]}"
                page_decorations.append(
                    f"BT /F1 8.0 Tf {COLOR_MUTED[0]:.3f} {COLOR_MUTED[1]:.3f} {COLOR_MUTED[2]:.3f} rg "
                    f"{self.margin_left:.2f} {A4_HEIGHT - 35.0:.2f} Td "
                    f"({self._escape_pdf_string(header_text)}) Tj ET\n"
                )
                page_decorations.append(
                    f"q 0.5 w {COLOR_BORDER[0]:.3f} {COLOR_BORDER[1]:.3f} {COLOR_BORDER[2]:.3f} RG "
                    f"{self.margin_left:.2f} {A4_HEIGHT - 40.0:.2f} m {self.margin_left + self.content_width:.2f} {A4_HEIGHT - 40.0:.2f} l S Q\n"
                )

            # Running Footer (all pages)
            footer_rule_y = self.margin_bottom - 15.0
            page_decorations.append(
                f"q 0.5 w {COLOR_BORDER[0]:.3f} {COLOR_BORDER[1]:.3f} {COLOR_BORDER[2]:.3f} RG "
                f"{self.margin_left:.2f} {footer_rule_y:.2f} m {self.margin_left + self.content_width:.2f} {footer_rule_y:.2f} l S Q\n"
            )
            # Left footer: classification note
            left_footer = "Nova-AI Research Intelligence Engine -- Evidence-Grounded Synthesis"
            page_decorations.append(
                f"BT /F1 7.5 Tf {COLOR_MUTED[0]:.3f} {COLOR_MUTED[1]:.3f} {COLOR_MUTED[2]:.3f} rg "
                f"{self.margin_left:.2f} {self.margin_bottom - 26.0:.2f} Td "
                f"({self._escape_pdf_string(left_footer)}) Tj ET\n"
            )
            # Right footer: Page X of Y
            page_str = f"Page {p_idx} of {total_pages}"
            page_decorations.append(
                f"BT /F2 8.0 Tf {COLOR_SECONDARY[0]:.3f} {COLOR_SECONDARY[1]:.3f} {COLOR_SECONDARY[2]:.3f} rg "
                f"{self.margin_left + self.content_width - 55.0:.2f} {self.margin_bottom - 26.0:.2f} Td "
                f"({self._escape_pdf_string(page_str)}) Tj ET\n"
            )

            # Prepend/append decorations to page stream
            stream_lines.extend(page_decorations)

        # Binary PDF Construction
        out = BytesIO()
        out.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        offsets: Dict[int, int] = {}
        obj_num = 1

        def write_obj(content: bytes) -> int:
            nonlocal obj_num
            current_num = obj_num
            obj_num += 1
            offsets[current_num] = out.tell()
            out.write(f"{current_num} 0 obj\n".encode("ascii"))
            out.write(content)
            out.write(b"\nendobj\n")
            return current_num

        # 1. Fonts Objects
        font_f1 = write_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
        font_f2 = write_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
        font_f3 = write_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>")
        font_f4 = write_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>")

        # 2. Pages Content Streams
        content_stream_ids: List[int] = []
        for stream_lines in self.pages_content:
            stream_body = "".join(stream_lines).encode("latin-1")
            stream_obj = (
                f"<< /Length {len(stream_body)} >>\n"
                f"stream\n"
            ).encode("ascii") + stream_body + b"\nendstream"
            content_stream_ids.append(write_obj(stream_obj))

        # 3. Page Objects
        page_ids: List[int] = []
        # Pre-calculate pages root obj_id
        pages_root_id = obj_num + total_pages

        for stream_id in content_stream_ids:
            page_obj = (
                f"<< /Type /Page /Parent {pages_root_id} 0 R\n"
                f"/MediaBox [0 0 {A4_WIDTH:.2f} {A4_HEIGHT:.2f}]\n"
                f"/Resources << /Font << /F1 {font_f1} 0 R /F2 {font_f2} 0 R /F3 {font_f3} 0 R /F4 {font_f4} 0 R >> >>\n"
                f"/Contents {stream_id} 0 R >>"
            ).encode("ascii")
            page_ids.append(write_obj(page_obj))

        # 4. Pages Root Object
        kids_str = " ".join(f"{pid} 0 R" for pid in page_ids)
        pages_root_obj = (
            f"<< /Type /Pages /Kids [{kids_str}] /Count {len(page_ids)} >>"
        ).encode("ascii")
        actual_pages_root = write_obj(pages_root_obj)

        # 5. Catalog Root Object
        catalog_obj = f"<< /Type /Catalog /Pages {actual_pages_root} 0 R >>".encode("ascii")
        catalog_id = write_obj(catalog_obj)

        # 6. Cross-Reference (XRef) Table
        xref_start = out.tell()
        total_objects = obj_num
        out.write(f"xref\n0 {total_objects}\n".encode("ascii"))
        out.write(b"0000000000 65535 f \n")
        for i in range(1, total_objects):
            offset_val = offsets.get(i, 0)
            out.write(f"{offset_val:010d} 00000 n \n".encode("ascii"))

        # 7. Trailer
        out.write(
            f"trailer\n<< /Size {total_objects} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF\n".encode("ascii")
        )

        pdf_bytes = out.getvalue()
        logger.debug("PDF built successfully", pages=total_pages, size_bytes=len(pdf_bytes))
        return pdf_bytes

