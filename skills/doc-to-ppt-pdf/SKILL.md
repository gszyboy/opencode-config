---
name: doc-to-ppt-pdf
description: Convert Markdown documents (PRD, proposals, reports) into polished PPT presentations and professional PDF proposals. Triggers when user wants to create a presentation from a document, generate PPT+PDF from PRD, or produce a client-ready proposal from Markdown source. Works with any Markdown containing headers, tables, lists, and code blocks.
---

# Doc to PPT + PDF Skill

Converts Markdown documents into:
1. **PPT Presentation** - Concise, visual slides (10-20 pages)
2. **PDF Proposal** - Complete, professionally designed document

## When to Use This Skill

Use this skill when user says:
- "帮我把这个文档做成PPT" / "make a presentation from this"
- "生成PPT和PDF" / "generate PPT and PDF"
- "把PRD转成演示文稿" / "convert this PRD to slides"
- "做个提案文档" / "create a proposal document"
- User provides a Markdown file and wants visual outputs

## Workflow

### Step 1: Analyze Source Document

Read the Markdown file and identify:
- Document type (PRD, proposal, report, etc.)
- Key sections (use section headers)
- Content density (tables, lists, code blocks)
- Total length (affects slide count)

### Step 2: Generate PPT

Use `scripts/generate-ppt.js` with content structure:

```bash
node scripts/generate-ppt.js \
  --title "Document Title" \
  --output output.pptx \
  --slides 19
```

The script creates slides with:
- Cover page
- Table of contents
- Section slides with key data
- Charts/tables visualization
- Closing slide

### Step 3: Generate PDF

Use bundled `minimax-pdf` skill with `scripts/md-to-content-json.js`:

```bash
# Convert Markdown to content.json
node scripts/md-to-content-json.js \
  --input source.md \
  --output content.json

# Generate PDF using minimax-pdf
bash ~/.minimax-skills/skills/minimax-pdf/scripts/make.sh run \
  --title "Document Title" \
  --type proposal \
  --accent "#8B5A2B" \
  --content content.json \
  --out output.pdf
```

## Key Scripts

### generate-ppt.js

Generates PPTX using pptxgenjs. Configurable theme:

```javascript
const theme = {
  primary: "22223b",    // Deep purple-gray (headers, titles)
  secondary: "4a4e69",  // Medium gray (subtitles)
  accent: "9a8c98",     // Warm gray-pink (accents)
  light: "c9ada7",       // Light pink-gray (highlights)
  bg: "f2e9e4",          // Cream background
  white: "FFFFFF"
};
```

Slide structure:
- Slide 1: Cover (title, subtitle, version)
- Slide 2: TOC (numbered sections)
- Slides 3+: Content (market data, tables, diagrams, quotes)
- Final: Thank you / CTA

### md-to-content-json.js

Parses Markdown and outputs `content.json` for minimax-pdf.

Supported block types:
- `h1`, `h2`, `h3` - Headings with accent rules
- `body` - Justified paragraph text
- `bullet` - Unordered list (• prefix)
- `numbered` - Ordered list (auto-counter)
- `callout` - Highlighted insight box
- `table` - Data tables with headers
- `divider` - Full-width accent rule

## Design Guidelines

### PPT Theme (Purple-Gray Warm)

| Element | Color | Usage |
|---------|-------|-------|
| primary | #22223b | Headers, title backgrounds |
| secondary | #4a4e69 | Subtitles, secondary elements |
| accent | #9a8c98 | Decorative lines, page numbers |
| light | #c9ada7 | Text highlights |
| bg | #f2e9e4 | Slide backgrounds |

### PDF Accent Selection

Choose accent based on document content:

| Context | Accent | Example |
|---------|--------|---------|
| Business/Proposal | #8B5A2B | Brown (warm, trustworthy) |
| Tech/Startup | #2D5F8A | Steel blue |
| Academic/Research | #2A5A6B | Deep teal |
| Creative/Portfolio | #FF6B6B | Coral |

## Output Files

Generate two deliverables:

1. **PPT** (`*.pptx`) - For presentations/meetings
   - 10-20 slides depending on content
   - Visual-first design
   - Executive-friendly summary

2. **PDF** (`*.pdf`) - For reference/print
   - Complete content preservation
   - Professional layout
   - 10-20 pages

## Quality Checklist

- [ ] PPT opens without errors
- [ ] All sections represented in slides
- [ ] Tables render correctly
- [ ] Chinese text displays properly
- [ ] PDF has cover + body pages
- [ ] No placeholder text remains
- [ ] File sizes reasonable (PPT <5MB, PDF <1MB per 10 pages)