import type { Metadata } from "next";
import "./globals.css";
import { Inter, Roboto_Mono } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });
const mono = Roboto_Mono({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Campus Internships",
  description: "AI Resume Analyzer – demo",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased`}>{children}</body>
    </html>
  );
}
