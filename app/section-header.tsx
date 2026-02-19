export function SectionHeader({ number, title }: { number: string; title: string }) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-3 mb-2">
        <span className="text-sm font-mono text-accent font-bold">
          {number.padStart(2, "0")}
        </span>
        <div className="flex-1 h-px bg-border" />
      </div>
      <h2 className="text-2xl font-bold text-foreground text-balance">{title}</h2>
    </div>
  );
}
