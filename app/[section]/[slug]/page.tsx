import Link from "next/link";
import { notFound } from "next/navigation";
import { getEntry, listEntries, SECTIONS, SECTION_LABELS, type Section } from "@/lib/content";
import { Markdown } from "../../markdown";

export function generateStaticParams() {
  return SECTIONS.flatMap((section) =>
    listEntries(section).map((e) => ({ section, slug: e.slug })),
  );
}

export const dynamicParams = false;

export default async function EntryPage({
  params,
}: {
  params: Promise<{ section: string; slug: string }>;
}) {
  const { section, slug } = await params;
  if (!SECTIONS.includes(section as Section)) notFound();
  const entry = getEntry(section as Section, slug);
  if (!entry) notFound();
  return (
    <article>
      <p className="section-label">
        <Link href={`/${section}`}>{SECTION_LABELS[section as Section]}</Link>
      </p>
      <Markdown>{entry.body}</Markdown>
    </article>
  );
}
