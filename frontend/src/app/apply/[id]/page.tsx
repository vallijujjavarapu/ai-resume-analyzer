"use client";

import { useState } from "react";
import Link from "next/link";
import { analyzeResume } from "@/lib/api";

export default function ApplyPage({ params }: { params: { id: string } }) {
  const internshipId = Number(params.id);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<null | { verdict: string; debug_len: number }>(null);

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const form = new FormData(e.currentTarget);
    form.set("internship_id", String(internshipId));

    try {
      const data = await analyzeResume(form);
      setResult({ verdict: data.verdict, debug_len: data.debug_len });
    } catch (err: any) {
      setError(err?.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="p-8 max-w-2xl mx-auto">
      <Link href="/" className="text-sm underline">&larr; Back</Link>
      <h1 className="text-2xl font-bold mt-2 mb-4">Apply & Analyze</h1>

      <form onSubmit={onSubmit} className="space-y-3 border rounded-xl p-4">
        <label className="text-sm">
          Student Name
          <input name="student_name" required className="block w-full border rounded-md p-2" />
        </label>
        <label className="text-sm">
          Email
          <input name="email" type="email" required className="block w-full border rounded-md p-2" />
        </label>
        <label className="text-sm">
          Degree (optional)
          <input name="degree" className="block w-full border rounded-md p-2" />
        </label>
        <label className="text-sm">
          CGPA (optional)
          <input name="cgpa" type="number" step="0.01" className="block w-full border rounded-md p-2" />
        </label>
        <label className="text-sm">
          Batch
          <select name="batch" required className="block w-full border rounded-md p-2">
            <option value="pre-final">Pre-Final</option>
            <option value="final">Final</option>
          </select>
        </label>
        <label className="text-sm">
          Resume (PDF/DOCX)
          <input name="resume" type="file" required accept=".pdf,.docx" className="block w-full" />
        </label>

        <button type="submit" disabled={loading} className="px-4 py-2 rounded-md border hover:bg-gray-50 disabled:opacity-50">
          {loading ? "Analyzing…" : "Upload & Analyze"}
        </button>
      </form>

      {error && <p className="mt-3 text-red-600 text-sm">Error: {error}</p>}

      {result && (
        <div className="mt-4 border rounded-xl p-4">
          <div className="text-lg font-semibold">Result: {result.verdict}</div>
          <div className="text-sm text-gray-600">Parsed text length: {result.debug_len} chars</div>
        </div>
      )}
    </main>
  );
}
