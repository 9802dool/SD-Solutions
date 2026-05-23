# SD Solutions (SDS)

**SD Solutions (SDS)** — evidence and case-document analysis for law-enforcement and prosecution teams.

Upload police documents and evidence bundles to assess strengths, weaknesses, bulletproofing actions, and anticipated King's Counsel cross-examination.

## Website (live)

**Production:** https://sd-solutions-neon.vercel.app  
**GitHub:** https://github.com/9802dool/SD-Solutions  
**Vercel dashboard:** https://vercel.com/simeon-doolarsinghs-projects/sd-solutions

The web app lives in [`web/`](web/) — a Next.js site on Vercel. Analysis runs **in the browser**; uploaded files are not sent to a server.

```powershell
cd web
npm install
npm run dev
```

Open http://localhost:3000

## Desktop launcher

Double-click **SD Solutions** on your desktop, or run:

```powershell
.\launchers\Launch-SDS.bat
```

## CLI (Python)

```powershell
python -m sds --demo
```

## Disclaimer

Decision-support only — not legal advice. All outputs require review by qualified legal counsel before court use.
