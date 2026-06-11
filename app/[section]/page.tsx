import Link from "next/link";
import { notFound } from "next/navigation";
import { listEntries, SECTIONS, SECTION_LABELS, type Section } from "@/lib/content";

export function generateStaticParams() {
  return SECTIONS.map((section) => ({ section }));
}

export const dynamicParams = false;

export default async function SectionIndex({
  params,
}: {
  params: Promise<{ section: string }>;
}) {
  const { section } = await params;
  if (!SECTIONS.includes(section as Section)) notFound();
  const entries = listEntries(section as Section);
  return (
    <div>
      <p className="section-label">{SECTION_LABELS[section as Section]}</p>
      <ul className="entry-list">
        {entries.map((e) => (
          <li key={e.slug}>
            <Link href={`/${e.section}/${e.slug}`}>{e.title}</Link>
            <span className="slug">{e.slug}.md</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
