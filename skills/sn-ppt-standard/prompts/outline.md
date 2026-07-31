# PPT 大纲规划

**重要：默认语言是中文。** 除非 `task_pack.params.language` 明确为 `en`，否则大纲中所有面向读者的文本（`title`、`subtitle`、`bullets[].head/detail`、`narrative`、`data_points[].label/context`、`visual_hints`、`asset_slots[].intent`）**必须全部使用中文**，不得中英文混杂，不得把中文概念翻译成英文。

Input: style_spec.json, info_pack.query_normalized, info_pack.document_digest (may be null), info_pack.user_assets.reference_images (list of standalone user-uploaded figure paths; may be empty), task_pack.params (incl. page_count).

**Goal**: produce an outline rich enough that each generated slide is **visually dense and informative**, not a sparse title + 3-bullet card. Under-filled pages look unprofessional. The downstream page-HTML generator will use every field you emit, so give it plenty to work with.

## Font strategy

下游 HTML 转换器支持 **Google Fonts 自动下载**（collect-fonts 阶段会扫描 HTML 中所有 Google Fonts 引用并自动下载 TTF）。请在 `visual_hints` 中主动引导使用美观的 Google Fonts 字体增强视觉表现。选择原则：标题用有特色的字体（如活泼场景用 ZCOOL KuaiLe、传统场景用 Ma Shan Zheng、手写场景用 Long Cang），正文保持清晰（如 Noto Sans SC）。具体字体名由下游 HTML 生成器根据风格和主题自行决定。

Output (JSON only):

```
{
  "pages": [
    {
      "page_no": 1,
      "page_kind": "cover | section_header | content | data | closing",
      "title": "<= 24 chars",
      "subtitle": "<= 60 chars, optional on cover / section_header>",
      "bullets": [
        {"head": "<= 20 chars", "detail": "<30-80 chars supporting the head>"},
        ...
      ],
      "narrative": "<60-200 chars — one short paragraph the slide should convey, used by page_html as additional prose when bullet format doesn't fit>",
      "data_points": [
        {"label": "<metric/name>", "value": "<number or phrase>", "context": "<optional>"},
        ...
      ],
      "visual_hints": "<30-120 chars: composition, mood, what the slide should feel like>",
      "use_table": {"doc_index": 0, "table_index": 2} | null,
      "use_image": {"doc_index": 0, "image_index": 0}
                 | {"reference_image_index": 0}
                 | null,
      "asset_slots": [
        {"slot_id": "hero", "intent": "<short phrase>", "aspect_ratio": "16:9"}
      ]
    }
  ]
}
```

## Language lock (hard — 中文优先)

All reader-visible text fields (`title`, `subtitle`, every `bullets[].head`/`detail`, `narrative`, `data_points[].label`/`context`, `visual_hints`, `asset_slots[].intent`) MUST be written in the language specified by `task_pack.params.language`.

- `zh` → **全部中文**。标题、要点、叙事、数据标签、视觉提示、配图意图全部使用中文，不得夹杂任何英文专业术语或缩写。
- `en` → 全部英文。
- **禁止中英混杂**。不要写"数据 Dashboard"、"目标 KPI"、"分析 Analytics"这种中英混合的表达。如果必须出现英文（如品牌名、产品名），确保在中文环境中是通用说法。
- The language flows downstream verbatim: rewriter writes the user query in this language, generator writes the HTML in this language. If the digest contains mixed-language source material, pick whatever fits `params.language` and don't carry the foreign-language originals through.

## Rules

- `pages` length MUST equal `page_count` exactly.
- **Page structure MUST include all of**: exactly 1 `cover` (page 1) + 1 `closing` (last page) + at least 1 `section_header` between `cover` and `closing` (if `page_count >= 5`, include 1–3 section_headers to break up the deck). Never mark every page as `content`.
- `title` <= 24 chars. Always required.
- `subtitle`: required on `cover` and `section_header`; optional on `closing`; absent on `content`/`data`.
- `bullets`: **3-6 items per page** (not 2, not fewer). Each item is an object with `head` (short punchy line) + `detail` (one-sentence expansion drawing from document_digest if available). Target **~4 bullets for content pages**, ~3 for cover / closing, ~5-6 for dense data pages.
- `narrative`: always fill. Treat as "what the slide tries to say in a paragraph". Lets the HTML generator produce a prose block when bullets would feel too sparse.
- `data_points`: include when `info_pack.document_digest.data_highlights` is non-empty or when `page_kind` is `data`. Distribute numbers / facts across relevant pages — do NOT bunch them all on one page.
- `visual_hints`: one sentence guiding composition (e.g. "split-screen with large hero left, 3-column KPI grid right").
- `asset_slots`: 0-2 per page. If `use_table` or `use_image` is non-null, **set asset_slots to `[]`** (this page already has its visual content from inherited material — no need for T2I decoration). Only pages without inherited material should have asset_slots.
- `use_table` / `use_image` **inherit from the input's source material**. Two separate pools can feed `use_image`:
  * **Pool A — document-embedded images**: walk `document_digest.inherited_images` (or, if digest is null, `raw_documents_excerpt` entries with non-empty `inherited_images`). Each item is `{doc_index, image_index}`.
  * **Pool B — standalone user-uploaded reference_images**: walk `available_reference_images` (from `info_pack.user_assets.reference_images`). Each item is referenced by its 0-based `reference_image_index`. The filename (e.g. `fig3_dram_market_share.png`, `fig7_historical_cycles.png`) gives strong semantic hints — match the image to the page whose topic its filename describes.
  * Walk through `document_digest.inherited_tables` and assign each to the most relevant page (ideally a `data` page) via `use_table`.
  * **Aim to use EVERY image across the deck** — if Pool A + Pool B together have 9 items and page_count=12, at least 9 pages should have `use_image` set (most likely via `reference_image_index`). Each image MUST be used at most once across the deck. Do not discard uploaded material just because digest was null.
  * If there are MORE images than pages, pick the most impactful (those matching key_points; high-level diagrams / market share charts over low-information screenshots).
  * `use_image` payload is EITHER `{"doc_index": D, "image_index": I}` (Pool A) OR `{"reference_image_index": N}` (Pool B). Never mix fields, never invent indices outside the pool bounds.
- Inherit domain facts from `document_digest` faithfully — do NOT invent metrics. If no digest is available, lean on `query_normalized.key_points` + general knowledge around the topic.
- JSON only, no markdown fences, no commentary.

## Density target

A typical 10-page deck should produce approximately:
- 10 titles, ~8 subtitles
- ~40 bullet items (each a head+detail object)
- ~10 narrative paragraphs
- ~15-25 data_points across data-heavy pages
- ~14-18 asset_slots total

If your output is substantially below this (e.g. only 20 bullets for 10 pages), pages will render sparse. Add more detail per page.
