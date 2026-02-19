const sections = [
  { id: "abstract", number: "1", title: "Abstract" },
  { id: "problem", number: "2", title: "Problem Statement" },
  { id: "tech-stack", number: "3", title: "Technology Stack" },
  { id: "architecture", number: "4", title: "System Architecture" },
  { id: "database", number: "5", title: "Database Schema" },
  { id: "ai-pipeline", number: "6", title: "AI Pipeline (Core Innovation)" },
  { id: "verification", number: "7", title: "Verification Engine -- 16 Checks x 5 Phases" },
  { id: "cost-estimation", number: "8", title: "Repair Cost Estimation" },
  { id: "authentication", number: "9", title: "Authentication & Authorization" },
  { id: "api", number: "10", title: "REST API Endpoints" },
  { id: "frontend", number: "11", title: "Frontend Architecture" },
  { id: "fraud-detection", number: "12", title: "Fraud Detection Capabilities" },
  { id: "design-principles", number: "13", title: "Key Design Principles" },
  { id: "viva-questions", number: "14", title: "Anticipated Viva Questions & Answers" },
  { id: "future", number: "15", title: "Future Enhancements" },
  { id: "dependencies", number: "16", title: "Dependencies" },
];

export function TableOfContents() {
  return (
    <nav className="mb-16 border border-border rounded-lg p-8 bg-section">
      <h2 className="text-xl font-bold text-foreground mb-6">Table of Contents</h2>
      <ol className="space-y-2">
        {sections.map((s) => (
          <li key={s.id}>
            <a
              href={`#${s.id}`}
              className="flex gap-3 text-sm text-foreground/80 hover:text-primary transition-colors py-1"
            >
              <span className="font-mono text-muted-foreground w-6 shrink-0">{s.number}.</span>
              <span>{s.title}</span>
            </a>
          </li>
        ))}
      </ol>
    </nav>
  );
}
