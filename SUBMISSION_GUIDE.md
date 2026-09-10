# SIH 2026 Submission Guide — InfraSight

## Repository content

- [x] Source code in `src/` and `scripts/`
- [x] README with proposed-platform overview, PS details, MVP proof, stack, setup, and run
- [x] Architecture and data-source documentation in `docs/`
- [x] Screenshot folder and capture instructions
- [x] Presentation and demo-video templates
- [ ] Replace team-member placeholders in `README.md`
- [ ] Add final screenshots to `assets/screenshots/`
- [ ] Add final PPT/PPTX or public viewer link to `submission/PRESENTATION.md`
- [ ] Add public demo-video link to `submission/DEMO.md` if available
- [ ] Make repository public and verify every submitted link while logged out/incognito

## Positioning

PPT, video, README, and screenshots should lead with proposed InfraSight platform: auditable source ingestion, validated records, explainable peer scoring, reviewer workflow, and admin oversight. Current repository is MVP evidence for core workflow, not claim of completed production deployment. State sample/data boundaries truthfully.

## Do not upload

- Passwords, API keys, access tokens, or private credentials
- `.env` files containing secrets
- Screenshots/videos exposing unrelated tabs, personal details, or confidential information

## Reviewer smoke test

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn src.api:app --reload
```

Open dashboard and press **Fetch snapshot entries**. It should show saved official snapshot entries without live portal access.
