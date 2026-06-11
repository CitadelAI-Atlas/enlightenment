import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Enlightenment: an open experiment in meditation music",
  description:
    "Designing, generating, and empirically testing long-form meditation music. Theory, models, hypotheses, and mistakes published as they happen.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header>
          <nav>
            <Link href="/" className="wordmark">
              enlightenment
            </Link>
            <span className="links">
              <Link href="/docs">docs</Link>
              <Link href="/specs">specs</Link>
              <Link href="/journal">journal</Link>
              <a
                href="https://github.com/CitadelAI-Atlas/enlightenment"
                target="_blank"
                rel="noreferrer"
              >
                github
              </a>
            </span>
          </nav>
        </header>
        <main>{children}</main>
        <footer>
          An open experiment. Theory, models, hypotheses, and mistakes are
          published as they happen.
        </footer>
      </body>
    </html>
  );
}
