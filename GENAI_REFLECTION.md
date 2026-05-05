# Generative AI (GenAI): Declaration and Critical Reflection

This document meets the COMP/XJCO3011 Coursework 2 requirements for **GenAI declaration** and **critical evaluation (approximately 15% of the module mark)**. You may use it as an outline when recording your video. Please edit any bracketed or “fill in” placeholders so they match **your actual** use of tools.

---

## 1. Declaration: which tools were used, and for what purpose

| Tool (fill in accurately) | Main purpose |
|---------------------------|--------------|
| For example: the University’s **Microsoft Copilot (secure access)** / **Cursor inline assistant**, etc. | Explaining common patterns for `requests` and `BeautifulSoup`; discussing which fields the inverted index should store; drafting `argparse` subcommand structure; sketching example tests with `pytest` and `unittest.mock`; reading stack traces and suggesting debugging directions |
| (If none were used, write **None** and go to Section 6.) | |

**Principle:** Core algorithmic choices (e.g. conjunctive multi-word queries via URL intersection, ranking by frequency and span) and product decisions such as **restricting the crawl to listing pages** were made by me after reading the brief. GenAI mainly sped up documentation, boilerplate, and test drafts; **I can explain every line of submitted code.**

---

## 2. Specific help: where GenAI was genuinely useful

1. **Beautiful Soup and page parsing**  
   When extracting `.quote`, `.text`, `.author`, `.tag`, and related structures, GenAI helped cross-check ideas against documentation and reduced time spent searching the official docs line by line. **Final selectors were validated on the real site** so I did not accidentally index navigation chrome as content.

2. **Politeness window implementation**  
   The brief requires **at least six seconds** between successive requests. GenAI suggested different patterns—e.g. “always `sleep(6)` after each request” versus “compute remaining wait from the last request timestamp”. I chose **timestamp-based waiting** and verified the delay logic in tests by mocking `time.sleep` and `time.time`. **Choosing between those patterns was my own decision after understanding the trade-offs.**

3. **Tests and mocking**  
   GenAI provided useful patterns for stubbing `requests.Session.get`, simulating non-HTML `Content-Type` headers, and simulating request failures in `pytest`, which shortened the path from an empty test file to a runnable suite. **Edge cases** such as empty text pages and continuing the crawl queue after a failed fetch were **added by me** against the coursework rubric.

4. **Project layout and README checks**  
   Against the required `src/`, `tests/`, and `data/` layout, GenAI helped catch omissions such as `requirements.txt` entries or missing CLI usage examples, reducing small but costly mistakes.

---

## 3. Specific hindrances: where GenAI was unhelpful or had to be corrected

1. **“Crawl everything” bias**  
   If I had followed a naive “follow every internal link” suggestion, tag and author pages would **duplicate** the same quotes in the index. Given the goal of an **efficient, searchable quote corpus**, I restricted crawling to the **home page and `/page/n/` only**, and documented the rationale in `README.md`. This is an example of **rejecting early AI advice in favour of domain-appropriate scope**.

2. **Inverted index field design**  
   GenAI sometimes suggested storing only a **document list** without positions. The brief explicitly asks for **statistics** (e.g. frequency, position). I kept **`frequency` and `positions`** in the index so `print` behaves as specified and `find` can use simple ranking signals.

3. **Correctness cannot be assumed**  
   Generated snippets occasionally mismatched the current `SearchEngine` API or omitted details such as creating parent directories for `Path` before saving. I caught these issues through **`pytest` and manual CLI runs**. **GenAI accelerates drafting; it does not replace testing and code review.**

---

## 4. Evaluation of the quality of AI-assisted code

- **Readability and modularity:** Splitting `crawler`, `indexer`, `search`, and `main` follows single responsibility and is easy to explain in the video; type hints and data structures are generally clear.  
- **Correctness:** Judged against tests and the brief; the current test suite passes, but **if the live site or network behaviour changes, crawler rules may still need manual maintenance**.  
- **Gap vs. an “outstanding” narrative:** GenAI cannot replace **verbal justification of design trade-offs** in the video. If advanced features (e.g. TF–IDF, full-site crawling) are **not** implemented, the reflection should honestly state **scope choices** rather than overstating novelty.

---

## 5. Reflection on learning and time management

- **Impact on learning:** GenAI reduced time spent looking up APIs, but skipping the official docs risks “runs but I cannot explain it”. For this project I deliberately cross-checked critical calls against the **Requests**, **BeautifulSoup**, and **pytest** documentation to consolidate module learning.  
- **Debugging challenges:** Understanding the gap between mocked HTTP and real asynchronous network behaviour still required breakpoints and prints—**modelling work that cannot be outsourced to AI**.  
- **Time management:** Time saved on test scaffolding should be reinvested in **edge cases, the video demonstration, and meaningful Git commit messages**; otherwise marks tied to non-code deliverables still dominate part of the grade.

---

## 6. If you did not use GenAI (optional section)

If you did not use any generative tools, replace the sections above with an honest statement emphasising **time spent reading documentation independently**, your **debugging strategy**, and whether you felt you understood data structures **more deeply** without AI assistance. The brief also accepts a “no GenAI” reflection path.

---

## 7. Short spoken script for the video (~30–60 seconds; speak naturally)

> I used **[fill in: Copilot / Cursor / etc.]**, mainly for quick reference on Beautiful Soup selectors, `argparse` subcommands, and `pytest` mocking patterns.  
> A helpful example was mocking HTTP failures and non-HTML responses in tests, which saved documentation lookup time.  
> A hindering example was the model’s tendency to suggest crawling **every** internal link, which would duplicate quotes; I restricted the crawl to the home page and paginated listing URLs and documented that in the README.  
> I verified every AI-generated fragment with tests and manual CLI runs; I kept **frequency** and **positions** in the inverted index to meet the brief’s statistics requirement.  
> Overall, GenAI increased typing speed, but **design decisions and correctness remain my responsibility**; I reinvested the time saved into edge-case tests and preparing this demonstration.

---

**Academic integrity (University of Leeds):** The statements above must reflect your **true** use of tools and must **match** what you say in the video. Non-declaration or misleading declaration of GenAI use may constitute **academic misconduct**.
