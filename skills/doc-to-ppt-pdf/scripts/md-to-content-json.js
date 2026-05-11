#!/usr/bin/env node
const fs = require("fs");

const args = process.argv.slice(2);
let inputFile = "";
let outputFile = "content.json";

for (let i = 0; i < args.length; i++) {
  if (args[i] === "--input" && args[i + 1]) inputFile = args[++i];
  if (args[i] === "--output" && args[i + 1]) outputFile = args[++i];
}

if (!inputFile) {
  console.error("Usage: node md-to-content-json.js --input source.md --output content.json");
  process.exit(1);
}

function parseMarkdown(md) {
  const lines = md.split("\n");
  const content = [];
  let inTable = false;
  let tableHeaders = [];
  let tableRows = [];
  let currentBody = [];
  let numberedCount = 0;

  function flushBody() {
    if (currentBody.length > 0) {
      currentBody.forEach(text => {
        if (text.trim()) {
          content.push({ type: "body", text: text.trim() });
        }
      });
      currentBody = [];
    }
  }

  function flushTable() {
    if (tableHeaders.length > 0) {
      content.push({
        type: "table",
        headers: tableHeaders,
        rows: tableRows
      });
    }
    tableHeaders = [];
    tableRows = [];
    inTable = false;
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith("```")) {
      flushBody();
      const codeLines = [];
      i++;
      while (i < lines.length && !lines[i].startsWith("```")) {
        codeLines.push(lines[i]);
        i++;
      }
      content.push({
        type: "code",
        text: codeLines.join("\n")
      });
      continue;
    }

    if (line.match(/^\|.*\|$/)) {
      flushBody();
      inTable = true;
      const cells = line.split("|").filter(c => c.trim() && !c.match(/^-+$/));
      if (tableHeaders.length === 0) {
        tableHeaders = cells.map(c => c.trim());
      } else {
        tableRows.push(cells.map(c => c.trim()));
      }
      continue;
    }

    if (inTable) {
      flushTable();
    }

    if (line.match(/^#{3}\s+(.+)/)) {
      flushBody();
      content.push({
        type: "h3",
        text: line.match(/^#{3}\s+(.+)/)[1]
      });
    } else if (line.match(/^##\s+(.+)/)) {
      flushBody();
      numberedCount = 0;
      content.push({
        type: "h2",
        text: line.match(/^##\s+(.+)/)[1]
      });
    } else if (line.match(/^#\s+(.+)/)) {
      flushBody();
      numberedCount = 0;
      content.push({
        type: "h1",
        text: line.match(/^#\s+(.+)/)[1]
      });
    } else if (line.match(/^[-*]\s+(.+)/)) {
      flushBody();
      const text = line.match(/^[-*]\s+(.+)/)[1];
      if (text.startsWith("[ ]") || text.startsWith("[x]")) {
        currentBody.push(text);
      } else {
        content.push({ type: "bullet", text });
      }
    } else if (line.match(/^\d+\.\s+(.+)/)) {
      flushBody();
      numberedCount++;
      content.push({
        type: "numbered",
        text: line.match(/^\d+\.\s+(.+)/)[1]
      });
    } else if (line.match(/^>\s+(.+)/)) {
      flushBody();
      content.push({
        type: "callout",
        text: line.match(/^>\s+(.+)/)[1]
      });
    } else if (line.match(/^---/)) {
      flushBody();
      content.push({ type: "divider" });
    } else if (line.trim()) {
      const text = line.trim();
      if (!text.startsWith("|") && !text.match(/^[-*]\s/)) {
        currentBody.push(text);
      }
    } else {
      if (currentBody.length > 0) {
        flushBody();
      }
    }
  }

  flushBody();
  flushTable();

  return content;
}

function convert(inputPath, outputPath) {
  const md = fs.readFileSync(inputPath, "utf-8");
  const content = parseMarkdown(md);

  const result = {
    title: "Document",
    author: "",
    date: new Date().getFullYear().toString(),
    content
  };

  fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
  console.log("Converted:", inputPath, "->", outputPath);
  console.log("Blocks generated:", content.length);
}

if (require.main === module) {
  convert(inputFile, outputFile);
}

module.exports = { parseMarkdown, convert };