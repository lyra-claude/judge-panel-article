#!/usr/bin/env python3
"""Convert DRAFT markdown to a LaTeX doc and compile with lualatex.

No pandoc available; this is a targeted converter for THIS article's markdown
subset: ATX headings (#, ##), fenced code block (```python), bullet lists (- ),
bold (**...**), italics (*...*), indented literal math lines, and unicode Greek.
lualatex + fontspec renders unicode (rho phi kappa Sigma lambda) natively.
"""
import re
import subprocess
import sys

SRC = "/home/lyra/projects/judge-panel-article/DRAFT-2026-09-11.md"
OUT_TEX = "/home/lyra/projects/judge-panel-article/_article.tex"
OUT_PDF = "/home/lyra/projects/judge-panel-article/2026-09-11-judge-panel-neff-article.pdf"

TITLE = "You're Paying for Nine Judges and Getting Two"
AUTHOR = "Lyra"
DATE = "2026-09-11"
RECIPIENT = "Claudius"
COMMIT_FULL = "8d5456a40317e47f9ecdd093f7af9f8f859278bc"
REPO = "lyra-claude/judge-panel-article"
NOTE = "Draft practitioner article for review — not a finalized result."


def esc(text: str) -> str:
    """Escape LaTeX specials in running prose (not code)."""
    # backslash first
    text = text.replace("\\", r"\textbackslash{}")
    repl = {
        "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#",
        "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for k, v in repl.items():
        text = text.replace(k, v)
    return text


def inline(text: str) -> str:
    """Escape then apply bold/italic markdown. Bold before italic."""
    text = esc(text)
    # inline code `...`
    text = re.sub(r"`([^`]+)`", lambda m: r"\texttt{" + m.group(1) + "}", text)
    # bold **...**
    text = re.sub(r"\*\*([^*]+)\*\*", lambda m: r"\textbf{" + m.group(1) + "}", text)
    # italic *...*
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", lambda m: r"\emph{" + m.group(1) + "}", text)
    return text


def convert(md: str) -> str:
    lines = md.split("\n")
    out = []
    i = 0
    in_list = False
    while i < len(lines):
        line = lines[i]

        # fenced code block
        if line.strip().startswith("```"):
            if in_list:
                out.append(r"\end{itemize}")
                in_list = False
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            out.append(r"\begin{lstlisting}")
            out.extend(code)
            out.append(r"\end{lstlisting}")
            continue

        # headings (skip H1 title line; handled by title page)
        if line.startswith("## "):
            if in_list:
                out.append(r"\end{itemize}")
                in_list = False
            out.append(r"\section*{" + inline(line[3:].strip()) + "}")
            i += 1
            continue
        if line.startswith("# "):
            # top-level title line in the body -> skip (title page carries it)
            i += 1
            continue

        # bullet list
        if line.startswith("- "):
            if not in_list:
                out.append(r"\begin{itemize}")
                in_list = True
            out.append(r"\item " + inline(line[2:].strip()))
            i += 1
            continue

        # indented literal (math display lines: 4-space indent)
        if line.startswith("    ") and line.strip():
            if in_list:
                out.append(r"\end{itemize}")
                in_list = False
            # collect the block of indented lines
            block = []
            while i < len(lines) and lines[i].startswith("    ") and lines[i].strip():
                block.append(lines[i][4:])
                i += 1
            out.append(r"\begin{quote}\ttfamily")
            for b in block:
                out.append(esc(b) + r"\\")
            out.append(r"\end{quote}")
            continue

        # blank line
        if not line.strip():
            if in_list:
                out.append(r"\end{itemize}")
                in_list = False
            out.append("")
            i += 1
            continue

        # normal paragraph line
        if in_list:
            out.append(r"\end{itemize}")
            in_list = False
        out.append(inline(line))
        i += 1

    if in_list:
        out.append(r"\end{itemize}")
    return "\n".join(out)


PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{amssymb}
\usepackage[margin=1in]{geometry}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{newunicodechar}
\usepackage[hidelinks]{hyperref}
% --- unicode glyph mapping for pdflatex (luaotfload absent, so no fontspec) ---
\newunicodechar{ρ}{\ensuremath{\rho}}
\newunicodechar{φ}{\ensuremath{\varphi}}
\newunicodechar{κ}{\ensuremath{\kappa}}
\newunicodechar{Σ}{\ensuremath{\Sigma}}
\newunicodechar{λ}{\ensuremath{\lambda}}
\newunicodechar{²}{\ensuremath{^{2}}}
\newunicodechar{×}{\ensuremath{\times}}
\newunicodechar{−}{\ensuremath{-}}
\newunicodechar{≈}{\ensuremath{\approx}}
\newunicodechar{·}{\ensuremath{\cdot}}
\newunicodechar{≥}{\ensuremath{\geq}}
\newunicodechar{≤}{\ensuremath{\leq}}
\newunicodechar{₁}{\ensuremath{_{1}}}
\newunicodechar{₂}{\ensuremath{_{2}}}
\newunicodechar{—}{---}
\newunicodechar{–}{--}
\newunicodechar{‘}{`}
\newunicodechar{’}{'}
\newunicodechar{“}{``}
\newunicodechar{”}{''}
\newunicodechar{}{\ensuremath{\bar{\varphi}}}
\lstset{
  basicstyle=\ttfamily\small,
  breaklines=true,
  columns=fullflexible,
  keepspaces=true,
  showstringspaces=false,
  frame=single,
  framesep=6pt,
  xleftmargin=6pt,
}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.6em}
\title{\vspace{-2em}}
\date{}
\begin{document}
"""

TITLEPAGE = (
    r"\thispagestyle{empty}" "\n"
    r"\begin{center}" "\n"
    r"{\LARGE\bfseries " + esc(TITLE) + r"}\\[1.5em]" "\n"
    r"\end{center}" "\n"
    r"\begin{flushleft}" "\n"
    r"\textbf{Author:} " + esc(AUTHOR) + r"\\[0.3em]" "\n"
    r"\textbf{Date:} " + esc(DATE) + r"\\[0.3em]" "\n"
    r"\textbf{Recipient:} " + esc(RECIPIENT) + r"\\[0.3em]" "\n"
    r"\textbf{Source commit:} \texttt{" + esc(COMMIT_FULL) + r"}, repo \texttt{" + esc(REPO) + r"}\\[0.3em]" "\n"
    r"\textit{" + esc(NOTE) + r"}" "\n"
    r"\end{flushleft}" "\n"
    r"\vspace{1.2em}\hrule\vspace{1.2em}" "\n"
)


def main():
    with open(SRC, encoding="utf-8") as f:
        md = f.read()
    # collapse the two-codepoint combining sequence phi + U+0304 (macron)
    # into a single private-use sentinel that maps to \bar{\varphi}
    md = md.replace("φ̄", "")
    body = convert(md)
    doc = PREAMBLE + TITLEPAGE + body + "\n\\end{document}\n"
    with open(OUT_TEX, "w", encoding="utf-8") as f:
        f.write(doc)

    # compile twice for hyperref/refs stability
    for run in range(2):
        r = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
             "-output-directory=/home/lyra/projects/judge-panel-article",
             OUT_TEX],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            sys.stderr.write("PDFLATEX FAILED on run %d\n" % run)
            sys.stderr.write(r.stdout[-3000:])
            sys.exit(1)
    # rename _article.pdf -> target
    import os
    src_pdf = "/home/lyra/projects/judge-panel-article/_article.pdf"
    os.replace(src_pdf, OUT_PDF)
    print("OK", OUT_PDF)


if __name__ == "__main__":
    main()
