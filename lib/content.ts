import fs from "node:fs";
import path from "node:path";

export const SECTIONS = ["docs", "specs", "journal"] as const;
export type Section = (typeof SECTIONS)[number];

export const SECTION_LABELS: Record<Section, string> = {
  docs: "Documentation",
  specs: "Specifications",
  journal: "Lab Journal",
};

const ROOT = process.cwd();

export interface Entry {
  section: Section;
  slug: string;
  title: string;
  body: string;
}

function titleOf(body: string, fallback: string): string {
  const heading = body.split("\n").find((line) => line.startsWith("# "));
  return heading ? heading.slice(2).trim() : fallback;
}

export function listEntries(section: Section): Entry[] {
  const dir = path.join(ROOT, section);
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((f) => f.endsWith(".md"))
    .sort()
    .map((f) => {
      const slug = f.replace(/\.md$/, "");
      const body = fs.readFileSync(path.join(dir, f), "utf8");
      return { section, slug, title: titleOf(body, slug), body };
    });
}

export function getEntry(section: Section, slug: string): Entry | null {
  const file = path.join(ROOT, section, `${slug}.md`);
  if (!fs.existsSync(file)) return null;
  const body = fs.readFileSync(file, "utf8");
  return { section, slug, title: titleOf(body, slug), body };
}

export function getReadme(): string {
  return fs.readFileSync(path.join(ROOT, "README.md"), "utf8");
}
