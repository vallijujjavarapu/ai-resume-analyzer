# ------------ Resume parsing helpers ------------
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse   # ✅ <- make sure it’s here
from io import BytesIO
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import io, re
import fitz  # PyMuPDF
import docx2txt
from typing import Dict, List, Tuple

SKILL_SYNONYMS = {
    # map common variants -> canonical skill name used in INTERNSHIPS
    "py": "python",
    "python3": "python",
    "js": "javascript",
    "reactjs": "react",
    "nodejs": "node",
    "postgres": "sql",
    "mysql": "sql",
    "ms sql": "sql",
    "scikit-learn": "sklearn",
    "scikitlearn": "sklearn",
}

WORD_SPLIT = re.compile(r"[^\w\+\#\.]+", re.UNICODE)  # keep words like c++, c#, node.js roughly intact

def read_text(file: UploadFile) -> str:
    raw = file.file.read()
    name = (file.filename or "").lower()
    if name.endswith(".pdf"):
        text = []
        with fitz.open(stream=raw, filetype="pdf") as doc:
            for page in doc:
                text.append(page.get_text("text"))
        return "\n".join(text)
    if name.endswith(".docx"):
        return docx2txt.process(io.BytesIO(raw)) or ""
    # fallback for .txt
    try:
        return raw.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def normalize_tokens(text: str) -> List[str]:
    tokens = [t.lower().strip(".") for t in WORD_SPLIT.split(text)]
    tokens = [t for t in tokens if t]  # remove empties
    # normalize synonyms
    out = []
    for t in tokens:
        out.append(SKILL_SYNONYMS.get(t, t))
    return out

def coverage(must_have: List[str], tokens: List[str]) -> Tuple[int, List[str]]:
    token_set = set(tokens)
    matched = [s for s in must_have if s.lower() in token_set]
    missing = [s for s in must_have if s.lower() not in token_set]
    return len(matched), missing

def score_resume(
    resume_text: str,
    internship: Dict,
    degree: str | None,
    cgpa: float | None,
    batch: str,  # "pre-final" | "final"
) -> Dict:
    tokens = normalize_tokens(resume_text)

    # 1) hard requirements
    must = internship.get("must_have_skills", [])
    nice = internship.get("nice_to_have_skills", [])
    n_matched, missing_must = coverage(must, tokens)
    must_cov = 0 if not must else round(100 * n_matched / len(must))

    # 2) nice-to-have
    nice_count = 0
    for s in nice:
        if s.lower() in tokens:
            nice_count += 1
    nice_cov = 0 if not nice else round(100 * nice_count / len(nice))

    # 3) degree + cgpa + batch gates
    degree_ok = True
    if degree:
        degree_ok = degree.upper() in (internship.get("degree_allowed") or [])
    gpa_ok = True
    if cgpa is not None and internship.get("min_gpa") is not None:
        gpa_ok = float(cgpa) >= float(internship["min_gpa"])
    batch_ok = (batch == "pre-final" and internship.get("allow_prefinal")) or (
        batch == "final" and internship.get("allow_final")
    )

    # 4) simple project/cert keywords (optional)
    missing_projects = []
    for p in internship.get("required_projects", []):
        if p.lower() not in tokens:
            missing_projects.append(p)
    missing_certs = []
    for c in internship.get("required_certs", []):
        if c.lower() not in tokens:
            missing_certs.append(c)

    # 5) weighted score
    # weights sum to 100
    w_must, w_nice, w_degree, w_gpa, w_batch, w_projects = 55, 15, 5, 10, 5, 10
    score = (
        must_cov * w_must / 100
        + nice_cov * w_nice / 100
        + (100 if degree_ok else 0) * w_degree / 100
        + (100 if gpa_ok else 0) * w_gpa / 100
        + (100 if batch_ok else 0) * w_batch / 100
        + (0 if missing_projects else 100) * w_projects / 100
    )
    score = round(score)

    # verdict rules
    verdict = "Pass"
    reasons: List[str] = []
    if not batch_ok:
        verdict = "Needs Work"
        reasons.append("Batch not allowed for this internship.")
    if not degree_ok:
        verdict = "Needs Work"
        reasons.append("Degree not in allowed list.")
    if not gpa_ok:
        verdict = "Needs Work"
        reasons.append(f"GPA below minimum {internship.get('min_gpa')}.")
    if must_cov < (internship.get("min_keyword_coverage") or 50):
        verdict = "Needs Work"
        reasons.append(f"Must-have skills coverage is only {must_cov}%.")

    advice: List[str] = []
    if missing_must:
        advice.append("Add these must-have skills to your resume: " + ", ".join(missing_must))
    if missing_projects:
        advice.append("Show a project related to: " + ", ".join(missing_projects))
    if not gpa_ok and cgpa is not None:
        advice.append("Consider highlighting strong coursework or projects to offset GPA.")
    if nice_cov < 60 and nice:
        advice.append("Bonus skills to mention: " + ", ".join([s for s in nice if s not in missing_must])[:120])

    return {
        "score": score,
        "must_coverage": must_cov,
        "nice_coverage": nice_cov,
        "degree_ok": degree_ok,
        "gpa_ok": gpa_ok,
        "batch_ok": batch_ok,
        "missing_must": missing_must,
        "missing_projects": missing_projects,
        "missing_certs": missing_certs,
        "verdict": verdict,
        "reasons": reasons,
        "advice": advice,
    }

# ------------ API: analyze ------------
@app.post("/apply/analyze")
async def analyze( 
from fastapi.responses import StreamingResponse
from io import BytesIO
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class ReportIn(BaseModel):
    student_name: str
    email: str
    internship_title: str
    company_name: str
    result: dict  # whatever /apply/analyze returned

def _make_pdf(data: ReportIn) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    y = h - 50

    def line(t, step=18):
        nonlocal y
        c.drawString(40, y, str(t)[:110]); y -= step

    c.setTitle("Resume Analysis Report")
    c.setFont("Helvetica-Bold", 16); line("Resume Analysis Report", 24)
    c.setFont("Helvetica", 11)
    line(f"Student: {data.student_name}")
    line(f"Email:   {data.email}")
    line(f"Company: {data.company_name}")
    line(f"Role:    {data.internship_title}")
    line("")

    r = data.result
    line(f"Verdict: {r.get('verdict','')}")
    if 'score' in r: line(f"Score: {r['score']}/100")
    if 'must_coverage' in r: line(f"Must-have coverage: {r['must_coverage']}%")
    if 'nice_coverage' in r: line(f"Nice-to-have coverage: {r['nice_coverage']}%")

    if r.get("reasons"):
        line(""); c.setFont("Helvetica-Bold", 12); line("Reasons"); c.setFont("Helvetica", 11)
        for s in r["reasons"]:
            line(f"• {s}")

    if r.get("advice"):
        line(""); c.setFont("Helvetica-Bold", 12); line("Suggestions"); c.setFont("Helvetica", 11)
        for s in r["advice"]:
            line(f"• {s}")

    c.showPage(); c.save()
    pdf = buf.getvalue(); buf.close()
    return pdf

@app.post("/apply/report")
async def report(payload: ReportIn):
    pdf_bytes = _make_pdf(payload)
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="resume-analysis-report.pdf"'},
    )

    internship_id: int = Form(...),
    student_name: str = Form(...),
    email: str = Form(...),
    degree: str = Form(None),
    cgpa: float = Form(None),
    batch: str = Form(...),  # "pre-final" | "final"
    resume: UploadFile = File(...),
):
    # find internship config
    internship = next((i for i in INTERNSHIPS if i["id"] == internship_id), None)
    if not internship:
        return {"error": "Unknown internship id."}

    text = read_text(resume)
    result = score_resume(text, internship, degree, cgpa, batch)

    return {
        "internship_id": internship_id,
        "student_name": student_name,
        "email": email,
        "debug_len": len(text),
        **result,
    }
