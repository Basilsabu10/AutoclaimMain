"use client";

export function PrintButton() {
  return (
    <button
      onClick={() => window.print()}
      className="no-print fixed bottom-6 right-6 z-50 bg-primary text-primary-foreground px-5 py-3 rounded-lg font-semibold text-sm shadow-lg hover:opacity-90 transition-opacity cursor-pointer"
    >
      Print / Save as PDF
    </button>
  );
}
