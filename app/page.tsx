import { getReadme } from "@/lib/content";
import { Markdown } from "./markdown";

export default function Home() {
  return <article><Markdown>{getReadme()}</Markdown></article>;
}
