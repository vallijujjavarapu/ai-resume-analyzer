import Link from "next/link";
import { getCompanies } from "@/lib/api";

export default async function Home() {
  const companies = await getCompanies();
  return (
    <main className="p-8 max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Campus Internships</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {companies.map((c: any) => (
          <Link
            key={c.id}
            href={`/company/${c.id}`}
            className="block border rounded-xl p-4 hover:shadow"
          >
            <div className="text-xl font-semibold">{c.name}</div>
            <div className="text-sm text-gray-500">{c.website}</div>
          </Link>
        ))}
      </div>
    </main>
  );
}

