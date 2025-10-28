const API = "http://127.0.0.1:8000";

export async function getCompanies() {
  const res = await fetch(`${API}/companies`);
  return res.json();
}

export async function getInternships(companyId: number) {
  const res = await fetch(`${API}/companies/${companyId}/internships`);
  return res.json();
}

export async function analyzeResume(form: FormData) {
  const res = await fetch(`${API}/apply/analyze`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }

  return res.json();
}

