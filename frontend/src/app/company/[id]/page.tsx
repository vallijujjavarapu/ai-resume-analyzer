import Link from "next/link";
import { getInternships } from "@/lib/api";

export default async function CompanyPage({ params }: { params: { id: string } }) {
  const internships = await getInternships(Number(params.id));
  return (
    <main className="p-8 max-w-5xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Internships</h2>
      <div className="space-y-4">
        {internships.map((i: any) => (
          <div key={i.id} className="border rounded-xl p-4">
            <div className="font-semibold text-lg">{i.title}</div>
            <div className="text-sm text-gray-600">{i.location}</div>
            <p className="mt-2 text-sm">{i.description}</p>
            <div className="mt-2 text-xs">Must: {i.must_have_skills.join(", ")}</div>

            <Link
              href={`/apply/${i.id}`}
              className="inline-block mt-3 px-3 py-1 rounded-md border hover:bg-gray-50"
            >
              Apply & Analyze
            </Link>
          </div>
        ))}
      </div>
    </main>
  );
}

