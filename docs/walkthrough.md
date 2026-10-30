# 3-minute walkthrough: LLM Data Quality Assistant

A timed script for a Loom recording of about 3 minutes (screen plus camera bubble, 1080p). Say it in your own words; the lines are a guide, not a teleprompter.

**Open these tabs before you press record:** README, `sample_artifacts/run_results.json`, `dq_assistant/parse.py`, `dq_assistant/report.py`, `dq_assistant/llm.py`, `tests/test_assistant.py`, GitHub Actions.

| Time | On screen | What to say |
|---|---|---|
| 0:00–0:20 | Portfolio card, then the README title | After a nightly dbt run, failures sit in a JSON file as cryptic test ids, and the business owner never hears about them. This turns them into a briefing data owners can act on. |
| 0:20–0:40 | README intro | The examples use sample dbt artifacts. At Bose I resolved metric discrepancies with the people who owned the numbers; this is the tool I'd want for that conversation. |
| 0:40–1:05 | `run_results.json`, then `parse.py` | It parses run_results and the manifest into findings, ranked worst first and mapped to the model each test checks. |
| 1:05–1:35 | The deterministic report | This report needs no API key and works offline: status, test, model and failing rows. The exit code is 1 when anything fails, so it can gate a CI job. |
| 1:35–2:05 | `llm.py` | With the flag on, Claude writes a short briefing: can reporting be trusted today, the business impact, likely causes and owners. It only sees the verified table of failing tests, and the prompt forbids inventing numbers or causes. |
| 2:05–2:30 | README: design choices | Ground truth first: the model rewrites verified facts and never queries data. If credentials or the network are missing, it falls back to the report instead of failing the pipeline. |
| 2:30–2:45 | `tests/test_assistant.py` and GitHub Actions | 7 tests cover parsing, ranking, the mapping, the CLI exit codes and the Claude call with a fake client, so CI runs offline. |
| 2:45–3:00 | Back to the README top | For a data team, that's test failures explained in business terms every morning, with every claim checkable underneath. Links are under the video. |

## Recording checklist
- Close email, chat and notifications. Zoom the browser to 125% so code is readable.
- Run `python -m dq_assistant --run-results sample_artifacts/run_results.json --manifest sample_artifacts/manifest.json` once so the report is on screen. Only show the `--llm` briefing if you have a key set.
- Keep to one take per section; Loom lets you trim. Aim for 2:45 to 3:10.
- Show real numbers on screen as you say them; never estimate on camera.
- Say "synthetic" out loud when you introduce the data. This is a skills demonstration, not a rebuild of client work.

## After recording
1. Copy the Loom share link.
2. In `README.md`, replace the walkthrough line with `- [x] [3-minute Loom walkthrough](<your Loom link>)` and add the link under the title.
3. Add the link to this project's card on saigwe.github.io.
