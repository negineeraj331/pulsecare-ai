"""
PulseCare AI - Professional Word Document Report Generator
Based on the Lovely Professional University (LPU) CSE494 MongoDB Project Report reference.
Author: Neeraj Negi (Reg No: 12303794)
Guide: Jaffar Amin Chacket
School of Computer Science and Engineering, LPU
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

OUTPUT_PATHS = [
    "/Users/neerajnegi/Desktop/mongodb_project/reports/PulseCare_AI_MongoDB_Project_Report.docx",
    "/Users/neerajnegi/Desktop/mongodb_project/PulseCare_AI_MongoDB_Project_Report.docx",
    "/Users/neerajnegi/Desktop/PulseCare_AI_MongoDB_Project_Report.docx"
]

SCREENSHOTS_DIR = "/Users/neerajnegi/Desktop/mongodb_project/reports/screenshots"

# Palette derived from reference PDF
COLOR_PRIMARY_NAVY = RGBColor(11, 27, 61)     # #0B1B3D
COLOR_SECONDARY_BLUE = RGBColor(2, 132, 199)  # #0284C7
COLOR_DARK_TEXT = RGBColor(30, 41, 59)        # #1E293B
COLOR_MUTED_GREY = RGBColor(100, 116, 139)    # #64748B
COLOR_WHITE = RGBColor(255, 255, 255)

HEX_NAVY = "0B1B3D"
HEX_LIGHT_BLUE = "F0F9FF"
HEX_BORDER_BLUE = "0284C7"
HEX_ALT_ROW = "F8FAFC"
HEX_HEADER_BG = "0B1B3D"
HEX_BORDER_GREY = "CBD5E1"
HEX_BORDER_DARK = "94A3B8"

def set_cell_background(cell, hex_color):
    """Sets cell background fill."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
    """Sets cell padding in twentieths of a point (dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color=HEX_BORDER_GREY, sz="4", val="single"):
    """Applies clean, subtle borders matching modern academic publications."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def make_row_header(row):
    """Configures row as table header (repeats on every page)."""
    trPr = row._tr.get_or_add_trPr()
    tblHeader = parse_xml(f'<w:tblHeader {nsdecls("w")}/>')
    trPr.append(tblHeader)
    cantSplit = parse_xml(f'<w:cantSplit {nsdecls("w")}/>')
    trPr.append(cantSplit)

def add_callout_box(doc, text, bold_prefix="Key contribution: "):
    """Creates a full-width callout box with light blue background and blue accent border."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(7.0)
    set_cell_background(cell, HEX_LIGHT_BLUE)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:color="{HEX_BORDER_BLUE}"/>'
        f'<w:left w:val="single" w:sz="24" w:color="{HEX_BORDER_BLUE}"/>'
        f'<w:bottom w:val="single" w:sz="6" w:color="{HEX_BORDER_BLUE}"/>'
        f'<w:right w:val="single" w:sz="6" w:color="{HEX_BORDER_BLUE}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    
    if bold_prefix:
        r_bold = p.add_run(bold_prefix)
        r_bold.font.name = 'Arial'
        r_bold.font.size = Pt(9.5)
        r_bold.font.bold = True
        r_bold.font.color.rgb = COLOR_PRIMARY_NAVY
    
    r_text = p.add_run(text)
    r_text.font.name = 'Arial'
    r_text.font.size = Pt(9.5)
    r_text.font.color.rgb = COLOR_DARK_TEXT
    
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(6)

def add_heading_1(doc, text):
    """Adds Section Heading 1 (18pt Bold Navy)."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = 'Arial'
    r.font.size = Pt(18)
    r.font.bold = True
    r.font.color.rgb = COLOR_PRIMARY_NAVY
    return p

def add_heading_2(doc, text):
    """Adds Subsection Heading 2 (13pt Bold Cyan/Navy)."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = 'Arial'
    r.font.size = Pt(13)
    r.font.bold = True
    r.font.color.rgb = COLOR_SECONDARY_BLUE
    return p

def add_heading_3(doc, text):
    """Adds Sub-subsection Heading 3 (11pt Bold Navy)."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.font.name = 'Arial'
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = COLOR_PRIMARY_NAVY
    return p

def add_body_paragraph(doc, text):
    """Adds standard body text (10pt Regular Dark Slate, 1.15 line spacing)."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text)
    r.font.name = 'Arial'
    r.font.size = Pt(10)
    r.font.color.rgb = COLOR_DARK_TEXT
    return p

def add_page_number_to_run(run):
    """Appends dynamic PAGE field to Word run."""
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)

def add_screenshot_figure(doc, img_name, fig_num, title, description):
    """Embeds screenshot with elegant academic border, centered figure caption, and description."""
    img_path = os.path.join(SCREENSHOTS_DIR, img_name)
    if not os.path.exists(img_path):
        print(f"Warning: Screenshot {img_path} not found!")
        return
    
    # Outer frame table for crisp outline
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    cell = table.cell(0, 0)
    cell.width = Inches(7.0)
    set_cell_background(cell, "FFFFFF")
    set_cell_margins(cell, top=60, bottom=60, left=60, right=60)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:color="{HEX_BORDER_GREY}"/>'
        f'<w:left w:val="single" w:sz="6" w:color="{HEX_BORDER_GREY}"/>'
        f'<w:bottom w:val="single" w:sz="6" w:color="{HEX_BORDER_GREY}"/>'
        f'<w:right w:val="single" w:sz="6" w:color="{HEX_BORDER_GREY}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p_img = cell.paragraphs[0]
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(2)
    p_img.paragraph_format.space_after = Pt(2)
    r_img = p_img.add_run()
    r_img.add_picture(img_path, width=Inches(6.8))
    
    # Caption
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(5)
    p_cap.paragraph_format.space_after = Pt(3)
    p_cap.paragraph_format.keep_with_next = True
    
    r_fig = p_cap.add_run(f"Figure {fig_num}. ")
    r_fig.font.name = 'Arial'
    r_fig.font.size = Pt(9)
    r_fig.font.bold = True
    r_fig.font.color.rgb = COLOR_PRIMARY_NAVY
    
    r_title = p_cap.add_run(title)
    r_title.font.name = 'Arial'
    r_title.font.size = Pt(9)
    r_title.font.italic = True
    r_title.font.color.rgb = COLOR_DARK_TEXT
    
    # Detailed technical description
    if description:
        p_desc = doc.add_paragraph()
        p_desc.paragraph_format.space_before = Pt(0)
        p_desc.paragraph_format.space_after = Pt(8)
        p_desc.paragraph_format.line_spacing = 1.15
        r_desc = p_desc.add_run(description)
        r_desc.font.name = 'Arial'
        r_desc.font.size = Pt(9.5)
        r_desc.font.color.rgb = COLOR_DARK_TEXT

def create_table(doc, headers, data, col_widths, alignment=None):
    """Generates a professional data table with navy header and alternating rows."""
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    set_table_borders(table)
    
    # Header Row
    header_row = table.rows[0]
    make_row_header(header_row)
    for col_idx, text in enumerate(headers):
        cell = header_row.cells[col_idx]
        cell.width = Inches(col_widths[col_idx])
        set_cell_background(cell, HEX_HEADER_BG)
        set_cell_margins(cell, top=140, bottom=140, left=160, right=160)
        p = cell.paragraphs[0]
        p.alignment = alignment[col_idx] if alignment else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = COLOR_WHITE
        
    # Data Rows
    for row_idx, row_data in enumerate(data):
        row = table.rows[row_idx + 1]
        bg_color = HEX_ALT_ROW if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, cell_value in enumerate(row_data):
            cell = row.cells[col_idx]
            cell.width = Inches(col_widths[col_idx])
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=100, bottom=100, left=160, right=160)
            p = cell.paragraphs[0]
            p.alignment = alignment[col_idx] if alignment else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            
            # Format bold first word or specific patterns if needed
            r = p.add_run(str(cell_value))
            r.font.name = 'Arial'
            r.font.size = Pt(9)
            r.font.color.rgb = COLOR_DARK_TEXT
            
    p_spacer = doc.add_paragraph()
    p_spacer.paragraph_format.space_before = Pt(0)
    p_spacer.paragraph_format.space_after = Pt(6)
    return table

def build_document():
    doc = Document()
    
    # Page Setup: Letter, 0.75" margins
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11.0)
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    section.header_distance = Inches(0.4)
    section.footer_distance = Inches(0.4)
    section.different_first_page_header_footer = True
    
    # -------------------------------------------------------------
    # Running Header and Footer (Pages 2+)
    # -------------------------------------------------------------
    header = section.header
    p_head = header.paragraphs[0]
    p_head.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_head.paragraph_format.space_before = Pt(0)
    p_head.paragraph_format.space_after = Pt(0)
    r_head = p_head.add_run("PulseCare AI | Project Report")
    r_head.font.name = 'Arial'
    r_head.font.size = Pt(8.5)
    r_head.font.color.rgb = COLOR_MUTED_GREY
    
    # Add subtle bottom line to header
    pPr = p_head._p.get_or_add_pPr()
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="4" w:space="4" w:color="{HEX_BORDER_GREY}"/></w:pBdr>')
    pPr.append(pBdr)
    
    footer = section.footer
    p_foot = footer.paragraphs[0]
    p_foot.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_foot.paragraph_format.space_before = Pt(0)
    p_foot.paragraph_format.space_after = Pt(0)
    
    # Subtle top border on footer
    pPr_f = p_foot._p.get_or_add_pPr()
    pBdr_f = parse_xml(f'<w:pBdr {nsdecls("w")}><w:top w:val="single" w:sz="4" w:space="4" w:color="{HEX_BORDER_GREY}"/></w:pBdr>')
    pPr_f.append(pBdr_f)
    
    r_foot_left = p_foot.add_run("MongoDB • Python • PyMongo")
    r_foot_left.font.name = 'Arial'
    r_foot_left.font.size = Pt(8.5)
    r_foot_left.font.color.rgb = COLOR_MUTED_GREY
    
    # Add tab to push page number to right
    p_foot.paragraph_format.tab_stops.add_tab_stop(Inches(7.0), WD_TAB_ALIGNMENT.RIGHT)
    r_foot_tab = p_foot.add_run("\t")
    r_foot_page = p_foot.add_run("Page ")
    r_foot_page.font.name = 'Arial'
    r_foot_page.font.size = Pt(8.5)
    r_foot_page.font.color.rgb = COLOR_MUTED_GREY
    add_page_number_to_run(p_foot.add_run())

    # =============================================================
    # PAGE 1: COVER PAGE
    # =============================================================
    
    # LPU Logo
    logo_path = os.path.join(SCREENSHOTS_DIR, "lpu_logo.png")
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(8)
        p_logo.paragraph_format.space_after = Pt(12)
        r_logo = p_logo.add_run()
        r_logo.add_picture(logo_path, width=Inches(3.4))
    else:
        # Fallback text banner
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_lpu = p_logo.add_run("LOVELY PROFESSIONAL UNIVERSITY\nSchool of Computer Science and Engineering")
        r_lpu.font.name = 'Arial'
        r_lpu.font.size = Pt(13)
        r_lpu.font.bold = True
        r_lpu.font.color.rgb = COLOR_PRIMARY_NAVY
    
    # Report Title Banner
    p_term = doc.add_paragraph()
    p_term.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_term.paragraph_format.space_before = Pt(0)
    p_term.paragraph_format.space_after = Pt(2)
    r_term1 = p_term.add_run("MONGODB PROJECT REPORT\n")
    r_term1.font.name = 'Arial'
    r_term1.font.size = Pt(13)
    r_term1.font.bold = True
    r_term1.font.color.rgb = COLOR_PRIMARY_NAVY
    
    r_term2 = p_term.add_run("(Project Term: January – May 2026)")
    r_term2.font.name = 'Arial'
    r_term2.font.size = Pt(9.5)
    r_term2.font.color.rgb = COLOR_MUTED_GREY
    
    # Accent Cyan Divider Line
    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_before = Pt(3)
    p_div.paragraph_format.space_after = Pt(12)
    pPr_d = p_div._p.get_or_add_pPr()
    pBdr_d = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="1" w:color="{HEX_BORDER_BLUE}"/></w:pBdr>')
    pPr_d.append(pBdr_d)
    
    # Project Title & Subtitle
    p_proj = doc.add_paragraph()
    p_proj.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_proj.paragraph_format.space_before = Pt(4)
    p_proj.paragraph_format.space_after = Pt(4)
    r_proj = p_proj.add_run("PulseCare AI: Emergency Healthcare & Clinical Resource Telemetry System")
    r_proj.font.name = 'Arial'
    r_proj.font.size = Pt(20)
    r_proj.font.bold = True
    r_proj.font.color.rgb = COLOR_PRIMARY_NAVY
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(2)
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run("A high-throughput clinical telemetry and automated resource orchestration platform built with MongoDB & PyMongo")
    r_sub.font.name = 'Arial'
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = COLOR_DARK_TEXT
    
    # Cover Architecture Diagram
    arch_path = os.path.join(SCREENSHOTS_DIR, "architecture_diagram.png")
    if os.path.exists(arch_path):
        p_arch = doc.add_paragraph()
        p_arch.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_arch.paragraph_format.space_before = Pt(4)
        p_arch.paragraph_format.space_after = Pt(4)
        r_arch = p_arch.add_run()
        r_arch.add_picture(arch_path, width=Inches(6.2))
        
        p_arch_sub = doc.add_paragraph()
        p_arch_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_arch_sub.paragraph_format.space_before = Pt(2)
        p_arch_sub.paragraph_format.space_after = Pt(16)
        r_asub = p_arch_sub.add_run("Real-time bedside vitals ingestion via atomic $push; protected operations enforce $jsonSchema validation")
        r_asub.font.name = 'Arial'
        r_asub.font.size = Pt(8.5)
        r_asub.font.color.rgb = COLOR_MUTED_GREY
        
    # Student & Supervisor Info
    p_subm = doc.add_paragraph()
    p_subm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subm.paragraph_format.space_before = Pt(4)
    p_subm.paragraph_format.space_after = Pt(2)
    r_subm_title = p_subm.add_run("Submitted by\n")
    r_subm_title.font.name = 'Arial'
    r_subm_title.font.size = Pt(9.5)
    r_subm_title.font.color.rgb = COLOR_MUTED_GREY
    
    r_stu = p_subm.add_run("Neeraj Negi | Reg. No: 12303794\n")
    r_stu.font.name = 'Arial'
    r_stu.font.size = Pt(12)
    r_stu.font.bold = True
    r_stu.font.color.rgb = COLOR_DARK_TEXT
    
    r_course = p_subm.add_run("Course Code: CSE494        Section: K2P23MP")
    r_course.font.name = 'Arial'
    r_course.font.size = Pt(10.5)
    r_course.font.color.rgb = COLOR_DARK_TEXT
    
    p_guid = doc.add_paragraph()
    p_guid.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_guid.paragraph_format.space_before = Pt(8)
    p_guid.paragraph_format.space_after = Pt(2)
    r_gtitle = p_guid.add_run("Under the Guidance of\n")
    r_gtitle.font.name = 'Arial'
    r_gtitle.font.size = Pt(9.5)
    r_gtitle.font.color.rgb = COLOR_MUTED_GREY
    
    r_prof = p_guid.add_run("Jaffar Amin Chacket\n")
    r_prof.font.name = 'Arial'
    r_prof.font.size = Pt(12)
    r_prof.font.bold = True
    r_prof.font.color.rgb = COLOR_DARK_TEXT
    
    r_dept = p_guid.add_run("School of Computer Science and Engineering\nLovely Professional University, Phagwara, Punjab — 144411")
    r_dept.font.name = 'Arial'
    r_dept.font.size = Pt(9.5)
    r_dept.font.color.rgb = COLOR_MUTED_GREY
    
    doc.add_page_break()

    # =============================================================
    # PAGE 2: TABLE OF CONTENTS
    # =============================================================
    add_heading_1(doc, "Table of Contents")
    
    toc_headers = ["Section", "Topic"]
    toc_widths = [1.2, 5.8]
    toc_data = [
        ["1", "Executive Summary"],
        ["2", "Introduction"],
        ["2.1", "Project Overview and Problem Statement"],
        ["2.2", "Motivation for MongoDB"],
        ["2.3", "Objectives and Scope"],
        ["3", "Methods and Database Engineering"],
        ["3.1", "Entity Identification"],
        ["3.2", "Conceptual and Logical Data Model"],
        ["3.3", "Collection Schemas and Field Definitions"],
        ["3.4", "MongoDB Validation Rules ($jsonSchema & Error 121)"],
        ["4", "Implementation Results"],
        ["4.1", "Application Architecture and PyMongo Integration"],
        ["4.2", "Authentication and Operational Workflows"],
        ["4.3", "Advanced Aggregation Pipelines & Analytics Surface"],
        ["4.4", "Application Screenshots"],
        ["5", "Technical Discussion and Architectural Trade-offs"],
        ["5.1", "Document Flexibility versus Governance"],
        ["5.2", "References versus Embedding"],
        ["5.3", "Cached Counters, Atomicity and Consistency"],
        ["5.4", "Current Limitations Identified from the Source"],
        ["6", "Future Scope and Scalability Roadmap"],
        ["7", "Conclusion"],
        ["8", "Source References"]
    ]
    
    create_table(doc, toc_headers, toc_data, toc_widths)
    
    add_callout_box(
        doc,
        "This report documents the design, implementation, database engineering, and analytical aggregation pipelines of PulseCare AI. All product names, workflows, schemas, endpoints, and technical statements below are derived from this project.",
        bold_prefix="Document note: "
    )
    
    doc.add_page_break()

    # =============================================================
    # PAGE 3: 1. EXECUTIVE SUMMARY & 2. INTRODUCTION
    # =============================================================
    add_heading_1(doc, "1. Executive Summary")
    
    add_body_paragraph(
        doc,
        "PulseCare AI is an intelligent, full-stack healthcare telemetry and hospital resource intelligence platform designed to resolve emergency department bottlenecks and coordinate acute clinical care. The system integrates a modern, high-contrast clinical command center frontend with a resilient Python and Flask REST API backend, backed by MongoDB 7.0 through the high-performance PyMongo driver. It supports real-time Emergency Severity Index (ESI 1–5) triage grading, high-velocity time-series bedside telemetry ingestion, automated bed and ventilator allocations, physician caseload balancing, and comprehensive administrative oversight."
    )
    
    add_body_paragraph(
        doc,
        "The database is organized around three principal collections: patients, doctors, and wards. A patient document captures the entire acute clinical encounter—including historical vital sign trends, medication orders, allergy registries, assigned doctor references, and bed location snapshots. Doctors maintain independent professional profiles, shift rosters, and active caseload thresholds, while wards record real-time bed inventories, occupancy metrics, and critical respiratory equipment. This hybrid document model aligns naturally with acute care requirements, allowing medical staff to retrieve a patient's complete diagnostic timeline in a single atomic disk seek (O(1)) without requiring expensive multi-table relational joins."
    )
    
    add_body_paragraph(
        doc,
        "The report documents the implemented database architecture, engine-level $jsonSchema validation rules, atomic PyMongo update operations ($push, $set, $inc), five multi-stage analytical aggregation pipelines, clinical workflows, and a practical roadmap for multi-cluster production scaling. It deliberately highlights how MongoDB addresses the velocity and polymorphism of real-world biomedical telemetry."
    )
    
    add_callout_box(
        doc,
        "a single operational command center that links high-frequency bedside telemetry to hospital resource orchestration, allowing emergency clinicians and department heads to act on the same atomic MongoDB data rather than maintaining disconnected records.",
        bold_prefix="Key contribution: "
    )
    
    add_heading_1(doc, "2. Introduction")
    
    add_heading_2(doc, "2.1 Project Overview and Problem Statement")
    add_body_paragraph(
        doc,
        "Hospital emergency departments (EDs) and Intensive Care Units (ICUs) operate under extreme physiological urgency and resource constraints. Patients arrive in diverse states of distress, requiring instantaneous triage categorization under the 5-tier Emergency Severity Index (ESI). Simultaneously, bedside monitoring monitors continuously stream biometric indicators—including heart rate, pulse oximetry (SpO2), systolic/diastolic blood pressure, and core body temperature. When these records and bed inventories are managed across disconnected paper charts or traditional relational databases, critical delays occur: triage acuity is misjudged, vital deterioration goes undetected, bed turnover stalls, and clinical teams lose precious intervention time."
    )
    add_body_paragraph(
        doc,
        "PulseCare AI resolves these challenges through a centralized, browser-based clinical command center. The dashboard surfaces live fleet KPIs: active admissions, critical ICU patients, telemetry anomalies, and available beds. Interactive clinical directories allow instant multi-field searching, detailed patient charts expose embedded vital timelines, and five multi-stage aggregation pipelines translate raw database documents into real-time hospital resource intelligence."
    )
    
    add_heading_2(doc, "2.2 Motivation for MongoDB")
    add_body_paragraph(
        doc,
        "MongoDB was selected as the operational data platform over traditional relational databases for three decisive architectural reasons:"
    )
    add_body_paragraph(
        doc,
        "1. Polymorphic Medical Encounters: Emergency patients present with wildly varying diagnostic profiles. Trauma cases record Glasgow Coma Scale (GCS) and fracture sites, cardiology admissions record troponin and rhythm strips, while toxicology encounters require substance logs. In MongoDB, documents naturally store polymorphic attributes without requiring dozens of sparse nullable columns or brittle DDL ALTER TABLE schema migrations."
    )
    add_body_paragraph(
        doc,
        "2. Single-Seek Read Latency for Critical Encounters: In resuscitation bays, seconds determine patient survival. Embedding historical vitals inside the patient document allows an attending physician to load the entire patient clinical history in a single atomic disk seek (O(1)), completely eliminating the join latency inherent in SQL foreign-key relationships."
    )
    add_body_paragraph(
        doc,
        "3. Atomic Multi-Field Operators: High-velocity bedside telemetry arrives at short intervals. MongoDB's $push operator appends new vital readings directly to embedded time-series arrays without rewriting the document or locking table spaces. Concurrently, the $inc operator atomically increments or decrements ward bed counts upon admission and discharge, guaranteeing transactional consistency without distributed locks."
    )
    
    add_heading_2(doc, "2.3 Objectives and Scope")
    
    obj_headers = ["Objective", "Implemented Scope"]
    obj_widths = [1.8, 5.2]
    obj_data = [
        ["Secure & Validated Ingestion", "Engine-level $jsonSchema validation enforcing types, ranges, regex, and enums; rejects invalid writes with MongoDB Error 121."],
        ["Patient Encounter Lifecycle", "Manage admissions, ESI Triage levels (1–5), clinical statuses (Triage, Admitted, ICU, Discharged), and assigned resources."],
        ["High-Velocity Telemetry", "Atomically $push time-series vitals (heart rate, SpO2, blood pressure, temperature) into embedded patient arrays."],
        ["Resource Orchestration", "Track doctors by shift/specialty and wards by total beds, occupied beds, and ventilators; manage bed allocation via $inc."],
        ["Operational Visibility & Analytics", "Provide live command center KPIs and 5 advanced aggregation pipelines (Triage Acuity, Ward Heatmap, Anomaly Detector, Doctor Caseload, $facet Command)."]
    ]
    create_table(doc, obj_headers, obj_data, obj_widths)
    
    doc.add_page_break()

    # =============================================================
    # PAGE 4: 3. METHODS AND DATABASE ENGINEERING
    # =============================================================
    add_heading_1(doc, "3. Methods and Database Engineering")
    
    add_heading_2(doc, "3.1 Entity Identification")
    add_body_paragraph(
        doc,
        "System analysis identified three persistent domain entities and one high-velocity telemetry event boundary:"
    )
    
    ent_headers = ["Entity", "Purpose", "Primary Relationships"]
    ent_widths = [1.3, 2.7, 3.0]
    ent_data = [
        ["Patient", "Core clinical record containing demographics, triage acuity, embedded vitals timeline, allergies, medications, and billing.", "References assigned Doctor via ObjectId; references assigned Ward via ObjectId."],
        ["Doctor", "Physician staff profile containing credentials, medical specialization, on-duty state, shift roster, and caseload quotas.", "Referenced by multiple Patient documents; aggregated in Pipeline 4 for caseload utilization."],
        ["Ward", "Hospital operational division recording total bed capacity, occupied beds, floor level, and available ventilator equipment.", "Referenced by Patient documents; bed occupancy counter atomically maintained via $inc."],
        ["Telemetry Reading", "Bedside IoT sensor vital signs readings (heart rate, SpO2, systolic/diastolic BP, temp, nurse signature).", "Embedded directly in Patient vitals_history array; analyzed in Pipeline 3 for physiological anomalies."]
    ]
    create_table(doc, ent_headers, ent_data, ent_widths)
    
    add_heading_2(doc, "3.2 Conceptual and Logical Data Model")
    
    # Re-embed Architecture Diagram
    if os.path.exists(arch_path):
        p_arch2 = doc.add_paragraph()
        p_arch2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_arch2.paragraph_format.space_before = Pt(4)
        p_arch2.paragraph_format.space_after = Pt(2)
        r_arch2 = p_arch2.add_run()
        r_arch2.add_picture(arch_path, width=Inches(6.2))
        
        p_cap1 = doc.add_paragraph()
        p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap1.paragraph_format.space_before = Pt(2)
        p_cap1.paragraph_format.space_after = Pt(6)
        r_fc1 = p_cap1.add_run("Figure 1. High-level application and persistence architecture.")
        r_fc1.font.name = 'Arial'
        r_fc1.font.size = Pt(9)
        r_fc1.font.italic = True
        r_fc1.font.color.rgb = COLOR_PRIMARY_NAVY
    
    add_body_paragraph(
        doc,
        "At runtime, the browser frontend communicates with the Flask REST API over HTTP/JSON. The API layer delegates incoming requests to dedicated CRUD and aggregation modules. PyMongo translates these requests into BSON commands executed against MongoDB 7.0. Before any patient document is written to disk, the database engine enforces strict $jsonSchema validation rules. Bedside telemetry readings are pushed atomically to the patient document, while ward occupancy counts are updated in-place using $inc."
    )
    
    doc.add_page_break()

    # =============================================================
    # PAGE 5: 3.3 COLLECTION SCHEMAS & 3.4 VALIDATION RULES
    # =============================================================
    add_heading_2(doc, "3.3 Collection Schemas and Field Definitions")
    
    add_heading_3(doc, "patients collection")
    pat_headers = ["Field", "Type / Constraint", "Meaning"]
    pat_widths = [1.8, 2.2, 3.0]
    pat_data = [
        ["patient_id", "String; unique, regex: ^PAT-[0-9]{4}-[0-9]{4}$", "Stable medical record identifier."],
        ["name", "String; minLength 2, maxLength 100", "Patient full legal name."],
        ["age, gender", "Int (0–125), Enum (Male, Female, Other)", "Demographic profile for clinical dosing."],
        ["blood_group", "Enum (A+, A-, B+, B-, AB+, AB-, O+, O-, Unknown)", "Blood group for transfusion readiness."],
        ["triage_level", "Enum (Level 1 - Resuscitation to Level 5 - Non-Urgent)", "Emergency Severity Index (ESI) triage acuity."],
        ["status", "Enum (Triage, Admitted, ICU, Under Observation, Discharged)", "Current clinical operational status."],
        ["contact", "Embedded Object (phone, emergency_contact)", "Next-of-kin emergency contact information."],
        ["assigned_doctor_id", "ObjectId; ref doctors", "Attending physician assigned to the case."],
        ["assigned_ward", "Embedded snapshot (ward_id Ref, ward_name, bed_number)", "Denormalized bed location for fast room lookups."],
        ["vitals_history", "Array of Objects (heart_rate, spo2, blood_pressure, temp)", "Chronological embedded time-series telemetry."],
        ["allergies, medications", "Arrays of Strings / Objects", "Clinical safety warnings and active drug orders."],
        ["billing", "Embedded Object (total_amount, insurance_covered, status)", "Encounter financial accounting audit record."]
    ]
    create_table(doc, pat_headers, pat_data, pat_widths)
    
    add_heading_3(doc, "doctors collection")
    doc_headers = ["Field", "Type / Constraint", "Meaning"]
    doc_widths = [1.8, 2.2, 3.0]
    doc_data = [
        ["doctor_id", "String; unique, regex: ^DOC-[0-9]{3}$", "Physician credential identifier."],
        ["name, specialization", "String; required", "Medical officer name and specialty (e.g., Critical Care)."],
        ["on_duty, shift", "Boolean, Enum (Morning, Evening, Night)", "Roster status and active working shift."],
        ["room_number, max_patients", "String, Int (default 15)", "Clinical room assignment and safe caseload ceiling."]
    ]
    create_table(doc, doc_headers, doc_data, doc_widths)
    
    add_heading_3(doc, "wards collection")
    ward_headers = ["Field", "Type / Constraint", "Meaning"]
    ward_widths = [1.8, 2.2, 3.0]
    ward_data = [
        ["ward_code", "String; unique, regex: ^WARD-[A-Z0-9-]+$", "Hospital physical wing identifier."],
        ["name, ward_type", "String, Enum (ICU, Emergency, Cardiology, Trauma, General)", "Clinical department and level of care provided."],
        ["total_beds, occupied_beds", "Int; non-negative", "Physical capacity and real-time occupied bed count."],
        ["floor, ventilators_available", "Int; non-negative", "Facility location and life-support ventilator inventory."]
    ]
    create_table(doc, ward_headers, ward_data, ward_widths)
    
    add_heading_2(doc, "3.4 MongoDB Validation Rules ($jsonSchema & Error 121)")
    add_body_paragraph(
        doc,
        "In strict compliance with Course Outcome CO5, data governance is enforced directly at the MongoDB storage engine level using $jsonSchema validation. During database initialization in backend/db.py, collections are provisioned with schema validators that restrict types, numerical ranges, string formats, and enum choices. Any write operation that violates these rules (e.g., an age of 250, an unrecognized triage tier, or an invalid patient ID pattern) is aborted by the database engine with Error Code 121 (Document failed validation), guaranteeing integrity regardless of client-side bugs."
    )
    
    doc.add_page_break()

    # =============================================================
    # PAGE 6: 4. IMPLEMENTATION RESULTS & WORKFLOWS
    # =============================================================
    add_heading_1(doc, "4. Implementation Results")
    
    add_heading_2(doc, "4.1 Application Architecture and PyMongo Integration")
    add_body_paragraph(
        doc,
        "The PulseCare AI backend is implemented in Python 3.13 utilizing the Flask web microframework and PyMongo 4.19 driver. PyMongo establishes a connection pool to MongoDB 7.0, maintaining an operational ping latency under 3.5ms. Indexes are automatically built at startup to guarantee fast response times: unique B-Tree indexes on patient_id, doctor_id, and ward_code; single-field indexes on triage_level and status; a compound index on {assigned_doctor_id: 1, status: 1} to accelerate physician caseload aggregations; and a text index on {name: 'text', primary_complaint: 'text'} for rapid clinical keyword searches."
    )
    
    add_heading_2(doc, "4.2 Authentication and Operational Workflows")
    
    wf_headers = ["Area", "Endpoint Examples", "Result"]
    wf_widths = [1.5, 2.5, 3.0]
    wf_data = [
        ["Health & Telemetry", "GET /api/health\nGET /api/stats", "Reports server latency, collection counts, and live system KPIs."],
        ["Patient Directory", "GET /api/patients\nPOST /api/patients", "Lists filtered patients with regex search; inserts validated patient documents."],
        ["Clinical Chart", "GET /api/patients/<id>\nPUT /api/patients/<id>/status", "Retrieves complete clinical encounter; transitions patient status atomically ($set)."],
        ["Telemetry Stream", "POST /api/patients/<id>/vitals", "Appends real-time bedside IoT vital reading into embedded vitals_history ($push)."],
        ["Discharge & Allocation", "POST /api/patients/<id>/discharge", "Sets status to Discharged and atomically decrements ward bed count ($inc: -1)."],
        ["Analytical Pipelines", "GET /api/analytics/triage-acuity\nGET /api/analytics/ward-capacity", "Executes 5 multi-stage aggregation pipelines for operational intelligence."],
        ["Viva Sandbox", "POST /api/sandbox/run-query", "Evaluates arbitrary MongoDB queries live with execution timing for defense examination."]
    ]
    create_table(doc, wf_headers, wf_data, wf_widths)
    
    add_heading_2(doc, "4.3 Advanced Aggregation Pipelines & Analytics Surface")
    add_body_paragraph(
        doc,
        "To fulfill Course Outcome CO6, the platform implements five multi-stage MongoDB aggregation pipelines:"
    )
    add_body_paragraph(
        doc,
        "• Pipeline 1 (Triage Acuity & Length-of-Stay Analysis): Employs $match (active inpatients), mathematical $project to derive hours stayed since admission_date, $group by triage_level, and $sort to highlight urgent ER backlogs."
    )
    add_body_paragraph(
        doc,
        "• Pipeline 2 (Ward Capacity & Ventilator Utilization Heatmap): Uses correlated $lookup to match active patient admissions with physical ward documents, computing real-time occupancy percentages and ventilator availability to prevent bed bottlenecks."
    )
    add_body_paragraph(
        doc,
        "• Pipeline 3 (Telemetry Vitals Anomaly & Critical Risk Detector): Unrolls embedded vitals arrays via $unwind, filters critical physiological thresholds (SpO2 < 92%, Heart Rate > 120 bpm, Systolic BP > 160 mmHg), groups by patient, joins attending physicians via $lookup, and assigns clinical risk levels using conditional logic ($cond)."
    )
    add_body_paragraph(
        doc,
        "• Pipeline 4 (Physician Caseload & ICU Caseload Matrix): Correlates doctors with assigned admissions via $lookup, calculates active caseloads and high-acuity ICU ratios using $filter and $size, and evaluates utilization percentages against doctor safety quotas."
    )
    add_body_paragraph(
        doc,
        "• Pipeline 5 (360° Hospital Command Multi-Stream Performance): Uses $facet to compute four analytical streams concurrently in a single round-trip: triage distributions, status counters, age demographic intervals using $bucket, and financial totals."
    )
    
    doc.add_page_break()

    # =============================================================
    # PAGES 7 - 13: 4.4 APPLICATION SCREENSHOTS (Figures 2 to 8)
    # =============================================================
    add_heading_2(doc, "4.4 Application Screenshots")
    add_body_paragraph(
        doc,
        "The following screenshots document the live execution of PulseCare AI, providing visual evidence of all system components, CRUD operations, aggregation pipelines, and query sandbox tools."
    )
    
    # Figure 2: Command Center Overview
    add_screenshot_figure(
        doc,
        "01_command_center_overview.png",
        2,
        "Hospital Command Center Overview showing live database connection telemetry, glowing KPI metrics, active admissions, telemetry anomaly alerts, and ward capacity meters.",
        "The Command Center view acts as the primary operational cockpit for emergency coordinators. The top status bar confirms live connection to the 'pulsecare_hospital_db' database with an instantaneous ping latency of 3.07ms. Four glowing KPI cards summarize Active Admissions (9), Critical ICU Patients (2), Telemetry Anomalies (4 detected by Pipeline 3), and Available Beds (33). Below, the left card renders live telemetry anomaly alerts with colored severity badges (CRITICAL EMERGENCY vs. HIGH RISK WARNING), while the right card displays ward capacity utilization meters computed in real-time."
    )
    
    doc.add_page_break()
    
    # Figure 3: Patient CRUD Directory
    add_screenshot_figure(
        doc,
        "02_patient_crud_directory.png",
        3,
        "Patient Management Directory with formatted triage acuity badges, clinical statuses, and dynamic PyMongo query preview.",
        "The Patient Management Directory demonstrates comprehensive CRUD reading with responsive data formatting. Each patient record showcases clinical identity (Patient ID, Name, Age, Gender), Emergency Severity Index badges (Level 1 Resuscitation in Red, Level 2 Emergent in Orange), clinical state (ICU, Admitted, Triage), latest vital telemetry readings, assigned clinician, and ward bed. At the top, a live PyMongo code banner dynamically mirrors the exact find query and sort criteria executed against MongoDB."
    )
    
    doc.add_page_break()
    
    # Figure 4: Search & Filtering
    add_screenshot_figure(
        doc,
        "03_patient_search_filtering.png",
        4,
        "Full-Text Regex Search and Multi-Field Filtering demonstrating instantaneous query execution against MongoDB.",
        "This view illustrates the multi-field query capabilities implemented in backend/crud.py. When a user types a search query (e.g., 'Eleanor Vance') and applies categorical filters for Triage Level and Inpatient Status, the application constructs a compound MongoDB query utilizing $regex with case-insensitivity ('$options': 'i') across name, patient_id, and primary_complaint fields. The query executed is displayed transparently: db.patients.find({'$or': [...]}).sort('admission_date', -1)."
    )
    
    doc.add_page_break()
    
    # Figure 5: Patient Clinical Chart Modal
    add_screenshot_figure(
        doc,
        "04_patient_clinical_chart_vitals.png",
        5,
        "Patient Clinical Chart Modal exhibiting attending physician, assigned ward, allergy history, and chronological embedded vitals timeline.",
        "The Clinical Chart Modal displays the full depth of the embedded document model. Opening a patient's chart retrieves all clinical details in a single seek (O(1)): demographic profile, attending physician details, assigned ward and bed number, known drug allergies, active medications, and the chronological vitals_history array. The table renders successive telemetry readings with recording timestamps, heart rate, blood pressure, SpO2, temperature, and nurse initials."
    )
    
    doc.add_page_break()
    
    # Figure 6: Aggregation Dashboard
    add_screenshot_figure(
        doc,
        "05_aggregation_analytics_dashboard.png",
        6,
        "Aggregation Analytics Dashboard visualizing the analytical results of all five multi-stage MongoDB pipelines.",
        "The Aggregation Analytics Dashboard provides executive decision-makers with live visualizations of hospital performance. Pipeline 1 displays average length-of-stay hours by triage category; Pipeline 2 renders ward capacity and ventilator surplus heatmaps; Pipeline 3 isolates patients with anomalous vitals requiring rapid response; Pipeline 4 evaluates physician caseload quotas; and Pipeline 5 presents executive distributions across age brackets, clinical statuses, and financial metrics."
    )
    
    doc.add_page_break()
    
    # Figure 7: Pipeline Code Viewer
    add_screenshot_figure(
        doc,
        "06_aggregation_pipeline_code.png",
        7,
        "Aggregation Pipeline BSON Code Inspector displaying the multi-stage MongoDB pipeline definitions and execution handles.",
        "The Aggregation Pipeline Code Inspector provides full architectural transparency for academic evaluation. Evaluators can select any of the five analytical pipelines from tabs to review the raw BSON pipeline stages ($match, $project, $group, $lookup, $unwind, $facet, $bucket) alongside detailed stage-by-stage descriptions and the corresponding PyMongo backend execution code."
    )
    
    doc.add_page_break()
    
    # Figure 8: Viva Sandbox
    add_screenshot_figure(
        doc,
        "07_viva_query_sandbox.png",
        8,
        "Interactive Viva Query Sandbox enabling evaluators to run custom MongoDB queries live with execution timing.",
        "The Interactive Viva Query Sandbox is specifically built for evaluation defense. It allows professors and evaluators to select preset oral defense queries or input custom MongoDB filters, projections, and sorts. The screenshot shows the live execution of the query for 'ICU Patients > 30 yrs' (matching patients like Eleanor Vance and Marcus Sterling), returning results in 3.65ms alongside the generated PyMongo code."
    )
    
    doc.add_page_break()

    # =============================================================
    # PAGE 14: 5. TECHNICAL DISCUSSION & 6. FUTURE SCOPE
    # =============================================================
    add_heading_1(doc, "5. Technical Discussion and Architectural Trade-offs")
    
    add_heading_2(doc, "5.1 Document Flexibility versus Governance")
    add_body_paragraph(
        doc,
        "MongoDB's document-oriented architecture provides the agility required by healthcare applications. Medical specialties can attach unique clinical observations (e.g., arterial blood gas values or neurological scores) to a patient record without requiring global schema refactoring. However, unchecked flexibility risks data corruption. PulseCare AI achieves balance by enforcing engine-level $jsonSchema validation rules: mandatory keys, regex patterns, and numerical ranges are validated by MongoDB before writes are accepted."
    )
    
    add_heading_2(doc, "5.2 References versus Embedding")
    add_body_paragraph(
        doc,
        "The schema intentionally balances normalization and denormalization. Bedside telemetry readings (vitals_history) and billing records are embedded because they belong exclusively to a single patient encounter and are always reviewed together during triage. Conversely, doctors and wards are referenced via ObjectId. Physicians treat dozens of patients across rotating shifts, and wards maintain physical room counts; embedding them would cause massive data duplication and dangerous update anomalies when doctor shifts or ward inventories change."
    )
    
    add_heading_2(doc, "5.3 Cached Counters, Atomicity and Consistency")
    add_body_paragraph(
        doc,
        "To avoid expensive full-collection count queries during peak emergency admissions, ward documents maintain an occupied_beds counter. This counter is updated atomically using MongoDB's $inc operator ($inc: {'occupied_beds': 1} on admission, $inc: {'occupied_beds': -1} on discharge). This delivers O(1) bed availability checks. To guard against counter drift from abrupt server terminations, Pipeline 2 periodically executes a correlated $lookup sub-pipeline to reconcile the cached occupied_beds counter against active patient documents."
    )
    
    add_heading_2(doc, "5.4 Current Limitations Identified from the Source")
    
    lim_headers = ["Observation", "Impact", "Recommended Direction"]
    lim_widths = [1.8, 2.2, 3.0]
    lim_data = [
        ["Single-Node Local Replica Set", "Lacks cross-region failover and disaster recovery.", "Deploy a 3-member replica set with automated primary election."],
        ["Polling-based UI Refresh", "Client issues periodic HTTP GET requests for vitals telemetry.", "Implement MongoDB Change Streams over WebSockets for instant push notifications."],
        ["Unbounded Time-Series Growth", "Long ICU stays could theoretically exceed the 16MB document limit.", "Migrate historical vitals to MongoDB Time-Series collections with automated archival."],
        ["Application-Level Token Security", "Basic session tokens require production hardening.", "Implement HTTPS, secure HttpOnly cookie flags, and JWT token rotation."]
    ]
    create_table(doc, lim_headers, lim_data, lim_widths)
    
    add_heading_1(doc, "6. Future Scope and Scalability Roadmap")
    add_body_paragraph(
        doc,
        "The current implementation delivers an operational prototype suitable for hospital ward deployments. The following phased roadmap scales the architecture for regional healthcare enterprise operations:"
    )
    
    road_headers = ["Stage", "Enhancement", "Expected Value"]
    road_widths = [0.9, 3.1, 3.0]
    road_data = [
        ["1", "Environment-based API configuration, HTTPS, secure HttpOnly cookies, and centralized error logging.", "Production-grade deployment and zero-trust security."],
        ["2", "MongoDB Change Streams with WebSockets for real-time telemetry broadcasts to clinician tablets.", "Sub-second alerts for life-threatening vital anomalies."],
        ["3", "Compound and partial B-Tree indexes for high-volume triage queries; verify via explain('executionStats').", "Predictable sub-millisecond query execution."],
        ["4", "Automated PyMongo integration test suite covering $jsonSchema boundaries and atomic transitions.", "Repeatable release confidence and regression prevention."],
        ["5", "Migration of high-frequency sensor readings to native MongoDB Time-Series collections.", "Columnar compression and scalable retention for billions of vitals."],
        ["6", "Horizontal sharding using compound shard keys on assigned_ward.ward_type and patient_id.", "Linear horizontal scaling across regional hospital clusters."]
    ]
    create_table(doc, road_headers, road_data, road_widths)
    
    doc.add_page_break()

    # =============================================================
    # PAGE 15: 7. CONCLUSION & 8. SOURCE REFERENCES
    # =============================================================
    add_heading_1(doc, "7. Conclusion")
    
    add_body_paragraph(
        doc,
        "PulseCare AI demonstrates the immense potential of MongoDB as a clinical telemetry and healthcare resource intelligence platform. By combining a modern clinical command center frontend with a resilient Python and Flask backend and MongoDB 7.0, the project successfully bridges the gap between high-velocity bedside physiological telemetry and emergency resource orchestration."
    )
    
    add_body_paragraph(
        doc,
        "The implementation fully satisfies all requirements of Academic Task 2 in CSE494 (Intelligent NoSQL Databases):"
    )
    add_body_paragraph(
        doc,
        "1. Suitable Document Modeling (CO4): Implemented a hybrid embedded-referenced document architecture that balances single-seek O(1) clinical chart retrieval with entity normalization for doctors and wards."
    )
    add_body_paragraph(
        doc,
        "2. Schema Validation & CRUD (CO5): Enforced database-level $jsonSchema validation rules rejecting malformed writes with Error Code 121, and integrated atomic PyMongo operators ($push, $set, $inc, insert_one, find, delete_one)."
    )
    add_body_paragraph(
        doc,
        "3. Advanced Aggregation Pipelines (CO6): Engineered five multi-stage analytical pipelines ($match, $project, $group, $lookup, $unwind, $facet, $bucket, $cond) delivering actionable real-time hospital intelligence."
    )
    add_body_paragraph(
        doc,
        "4. Operational Verification: Delivered an interactive web platform with an evaluation sandbox and a standalone terminal oral defense suite."
    )
    
    add_body_paragraph(
        doc,
        "The project proves that a well-architected NoSQL document database eliminates the latency, schema rigidity, and locking bottlenecks of traditional relational systems in acute healthcare environments."
    )
    
    add_heading_1(doc, "8. Source References")
    
    refs = [
        "1. Project Source Repository: backend/app.py (Flask API), backend/db.py (MongoDB Connection & $jsonSchema), backend/crud.py (PyMongo CRUD Operations), backend/aggregations.py (5 Aggregation Pipelines), backend/seed_data.py, templates/index.html.",
        "2. PyMongo Official Documentation: MongoDB Inc., 'PyMongo 4.19.0 Documentation: Working with BSON and MongoDB in Python', docs.mongodb.com/drivers/pymongo/.",
        "3. MongoDB Server Manual: MongoDB Inc., 'MongoDB 7.0 Manual: Aggregation Pipeline Stages, Operators, and $jsonSchema Schema Validation', mongodb.com/docs/v7.0/.",
        "4. Emergency Severity Index (ESI) Implementation Handbook: Agency for Healthcare Research and Quality (AHRQ), 'A Triage Tool for Emergency Department Care', 5th Edition.",
        "5. Course Syllabus & Reference Document: Course Code CSE494 (Intelligent NoSQL Databases), School of Computer Science and Engineering, Lovely Professional University, Punjab."
    ]
    for ref in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_before = Pt(2)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.line_spacing = 1.15
        r_ref = p_ref.add_run(ref)
        r_ref.font.name = 'Arial'
        r_ref.font.size = Pt(9)
        r_ref.font.color.rgb = COLOR_DARK_TEXT
        
    p_end = doc.add_paragraph()
    p_end.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_end.paragraph_format.space_before = Pt(24)
    p_end.paragraph_format.space_after = Pt(12)
    pPr_e = p_end._p.get_or_add_pPr()
    pBdr_e = parse_xml(f'<w:pBdr {nsdecls("w")}><w:top w:val="single" w:sz="8" w:space="8" w:color="{HEX_BORDER_BLUE}"/></w:pBdr>')
    pPr_e.append(pBdr_e)
    r_end = p_end.add_run("End of Report")
    r_end.font.name = 'Arial'
    r_end.font.size = Pt(11)
    r_end.font.bold = True
    r_end.font.color.rgb = COLOR_PRIMARY_NAVY
    
    # Save document to outputs
    for path in OUTPUT_PATHS:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            doc.save(path)
            print(f"Report saved successfully to: {path}")
        except Exception as e:
            print(f"Notice: Could not save to {path}: {e}")

if __name__ == "__main__":
    build_document()
