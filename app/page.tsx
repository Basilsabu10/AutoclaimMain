import { PrintButton } from "./print-button";
import { TableOfContents } from "./table-of-contents";
import { SectionHeader } from "./section-header";

export default function ProjectReport() {
  return (
    <main className="min-h-screen bg-background">
      {/* Print button - floating */}
      <PrintButton />

      {/* Cover Page */}
      <section className="min-h-screen flex flex-col items-center justify-center px-6 py-16 bg-primary text-primary-foreground text-center">
        <div className="max-w-3xl mx-auto">
          <p className="text-sm tracking-[0.3em] uppercase mb-6 opacity-80">
            Project Report
          </p>
          <h1 className="text-5xl font-bold tracking-tight mb-4 text-balance leading-tight">
            AutoClaim
          </h1>
          <p className="text-xl opacity-90 mb-10 text-pretty leading-relaxed">
            AI-Powered Vehicle Insurance Claim Processing System
          </p>
          <div className="w-24 h-0.5 bg-accent mx-auto mb-10" />
          <div className="text-sm opacity-80 leading-relaxed">
            <p className="mb-1">Version 2.0.0</p>
            <p className="mb-1">Full-Stack Application with Multi-Stage AI Pipeline</p>
            <p className="mb-4">FastAPI + React + YOLOv8 + Groq Vision + Rule-Based Verification</p>
            <p className="mt-8 opacity-60">February 2026</p>
          </div>
        </div>
      </section>

      {/* Document body */}
      <div className="max-w-4xl mx-auto px-6 py-16">
        {/* Table of Contents */}
        <TableOfContents />

        {/* ── Section 1: Abstract ──────────────────────────────────────── */}
        <section id="abstract" className="mb-16">
          <SectionHeader number="1" title="Abstract" />
          <p className="leading-relaxed text-foreground/90">
            AutoClaim is a full-stack web application that automates the vehicle
            insurance claim verification process. Traditional claim processing
            is slow (5-15 days), inconsistent (agent-dependent), and vulnerable
            to fraud. AutoClaim replaces this with a multi-stage AI pipeline
            that combines computer vision, OCR, metadata forensics, and a
            deterministic rule-based verification engine to process claims in
            seconds. The system extracts factual data from images using AI, then
            applies 16 Python-coded verification rules across 5 phases to make
            auditable, deterministic decisions -- approve, flag, or reject.
          </p>
        </section>

        {/* ── Section 2: Problem Statement ─────────────────────────────── */}
        <section id="problem" className="mb-16">
          <SectionHeader number="2" title="Problem Statement" />
          <div className="bg-section border border-border rounded-lg p-6 mb-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {[
                { label: "Slow", desc: "Manual review takes 5-15 business days per claim" },
                { label: "Inconsistent", desc: "Different agents make different decisions on identical claims" },
                { label: "Fraud Vulnerable", desc: "Hard to detect fake/edited images, pre-existing damage, or vehicle mismatches" },
                { label: "Expensive", desc: "Requires large teams of human adjusters and investigators" },
              ].map((item) => (
                <div key={item.label} className="flex gap-3">
                  <div className="w-2 h-2 rounded-full bg-accent mt-2 shrink-0" />
                  <div>
                    <p className="font-semibold text-foreground">{item.label}</p>
                    <p className="text-sm text-muted-foreground">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <p className="leading-relaxed text-foreground/90">
            AutoClaim addresses all four challenges by automating the entire
            pipeline with AI-driven data extraction and Python rule-based
            decision making, ensuring speed, consistency, auditability, and
            fraud detection.
          </p>
        </section>

        {/* ── Section 3: Technology Stack ──────────────────────────────── */}
        <section id="tech-stack" className="mb-16 page-break">
          <SectionHeader number="3" title="Technology Stack" />
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-primary text-primary-foreground">
                  <th className="text-left p-3 font-semibold">Layer</th>
                  <th className="text-left p-3 font-semibold">Technology</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["Frontend", "React 19 + Vite 7 + React Router 7 + Bootstrap 5"],
                  ["Backend", "Python FastAPI v2.0"],
                  ["Database", "SQLite via SQLAlchemy ORM"],
                  ["AI - Vision / LLM", "Groq API (LLaMA 3.2 11B Vision + LLaMA 4 Scout fallback)"],
                  ["AI - Object Detection", "YOLOv8 (Self-hosted, Hugging Face model)"],
                  ["AI - OCR", "EasyOCR (Self-hosted, number plate extraction)"],
                  ["Image Metadata", "Pillow (EXIF) + Geopy (Reverse Geocoding)"],
                  ["Authentication", "JWT (HS256) + PBKDF2-SHA256 password hashing"],
                  ["Cost Estimation", "Custom Repair Estimator with USD-to-INR conversion"],
                ].map(([layer, tech], i) => (
                  <tr
                    key={layer}
                    className={i % 2 === 0 ? "bg-background" : "bg-section"}
                  >
                    <td className="p-3 border-b border-border font-medium">{layer}</td>
                    <td className="p-3 border-b border-border text-muted-foreground">{tech}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* ── Section 4: System Architecture ───────────────────────────── */}
        <section id="architecture" className="mb-16">
          <SectionHeader number="4" title="System Architecture" />
          <p className="leading-relaxed text-foreground/90 mb-6">
            The system follows a classic client-server architecture. The React
            frontend communicates with the FastAPI backend via REST APIs. Claim
            analysis is processed asynchronously using FastAPI BackgroundTasks,
            so the user gets an immediate response while the AI pipeline runs
            in the background.
          </p>
          <div className="bg-foreground text-primary-foreground rounded-lg p-6 font-mono text-xs leading-relaxed overflow-x-auto">
            <pre>{`[User / Admin / Agent Browser]
        |
   [React Frontend (Vite 7)]
        |  HTTP REST + JWT Auth
   [FastAPI Backend (v2.0)]
        |
   +----+------------------+
   |    |                  |
[SQLite DB]    [AI Pipeline (Background Tasks)]
                     |
         +-----------+-----------+----------+
         |           |           |          |
  [EXIF Service] [OCR Service] [YOLOv8] [Groq Vision API]
         |           |           |          |
         +-----------+-----------+----------+
                     |
          [Forensic Mapper (Data Transform)]
                     |
          [Verification Rules Engine v2.0]
          [   16 Checks x 5 Phases       ]
                     |
             [APPROVE / FLAG / REJECT]`}</pre>
          </div>
        </section>

        {/* ── Section 5: Database Schema ───────────────────────────────── */}
        <section id="database" className="mb-16 page-break">
          <SectionHeader number="5" title="Database Schema" />
          <p className="leading-relaxed text-foreground/90 mb-6">
            The database contains 5 tables managed via SQLAlchemy ORM. The
            ForensicAnalysis table is the most important, storing 60+ columns
            of results from every stage of the AI pipeline.
          </p>

          {/* Users */}
          <h3 className="text-lg font-semibold text-foreground mt-8 mb-3">
            5.1 Users
          </h3>
          <div className="overflow-x-auto mb-6">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-muted">
                  <th className="text-left p-2 border border-border font-semibold">Column</th>
                  <th className="text-left p-2 border border-border font-semibold">Type</th>
                  <th className="text-left p-2 border border-border font-semibold">Notes</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["id", "Integer", "Primary key"],
                  ["email", "String", "Unique, indexed"],
                  ["hashed_password", "String", "PBKDF2-SHA256"],
                  ["role", "String", "user / admin / agent"],
                  ["name", "String", "Display name"],
                  ["policy_id", "String", "Legacy policy reference"],
                  ["vehicle_number", "String", "Vehicle registration"],
                  ["created_at", "DateTime", "Auto-set on creation"],
                ].map(([col, type, notes]) => (
                  <tr key={col}>
                    <td className="p-2 border border-border font-mono text-xs">{col}</td>
                    <td className="p-2 border border-border">{type}</td>
                    <td className="p-2 border border-border text-muted-foreground">{notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* PolicyPlans */}
          <h3 className="text-lg font-semibold text-foreground mt-8 mb-3">
            5.2 PolicyPlans
          </h3>
          <div className="overflow-x-auto mb-6">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-muted">
                  <th className="text-left p-2 border border-border font-semibold">Column</th>
                  <th className="text-left p-2 border border-border font-semibold">Type</th>
                  <th className="text-left p-2 border border-border font-semibold">Notes</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["id", "Integer", "Primary key"],
                  ["name", "String", "Plan name"],
                  ["description", "Text", "Plan details"],
                  ["coverage_amount", "Integer", "Maximum coverage in INR"],
                  ["premium_monthly", "Integer", "Monthly premium in INR"],
                ].map(([col, type, notes]) => (
                  <tr key={col}>
                    <td className="p-2 border border-border font-mono text-xs">{col}</td>
                    <td className="p-2 border border-border">{type}</td>
                    <td className="p-2 border border-border text-muted-foreground">{notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Policies */}
          <h3 className="text-lg font-semibold text-foreground mt-8 mb-3">
            5.3 Policies
          </h3>
          <div className="overflow-x-auto mb-6">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-muted">
                  <th className="text-left p-2 border border-border font-semibold">Column</th>
                  <th className="text-left p-2 border border-border font-semibold">Type</th>
                  <th className="text-left p-2 border border-border font-semibold">Notes</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["id", "Integer", "Primary key"],
                  ["user_id", "Integer", "FK -> Users"],
                  ["plan_id", "Integer", "FK -> PolicyPlans"],
                  ["vehicle_make", "String", "e.g., Toyota"],
                  ["vehicle_model", "String", "e.g., Camry"],
                  ["vehicle_year", "Integer", "Manufacturing year"],
                  ["vehicle_registration", "String", "License plate number"],
                  ["start_date / end_date", "DateTime", "Policy validity window"],
                  ["status", "String", "active / expired / cancelled"],
                ].map(([col, type, notes]) => (
                  <tr key={col}>
                    <td className="p-2 border border-border font-mono text-xs">{col}</td>
                    <td className="p-2 border border-border">{type}</td>
                    <td className="p-2 border border-border text-muted-foreground">{notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Claims */}
          <h3 className="text-lg font-semibold text-foreground mt-8 mb-3">
            5.4 Claims
          </h3>
          <div className="overflow-x-auto mb-6">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-muted">
                  <th className="text-left p-2 border border-border font-semibold">Column</th>
                  <th className="text-left p-2 border border-border font-semibold">Type</th>
                  <th className="text-left p-2 border border-border font-semibold">Notes</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["id", "Integer", "Primary key"],
                  ["user_id", "Integer", "FK -> Users"],
                  ["policy_id", "Integer", "FK -> Policies (nullable)"],
                  ["description", "Text", "User's claim narrative"],
                  ["image_paths", "JSON", "Array of damage image paths"],
                  ["front_image_path", "String", "Front view for OCR"],
                  ["estimate_bill_path", "String", "Uploaded repair estimate"],
                  ["status", "String", "pending / processing / completed / approved / rejected / failed"],
                  ["vehicle_number_plate", "String", "OCR-extracted plate"],
                  ["ai_recommendation", "String", "APPROVE / FLAG / REJECT"],
                  ["estimated_cost_min/max", "Integer", "Repair cost range in INR"],
                ].map(([col, type, notes]) => (
                  <tr key={col}>
                    <td className="p-2 border border-border font-mono text-xs">{col}</td>
                    <td className="p-2 border border-border">{type}</td>
                    <td className="p-2 border border-border text-muted-foreground">{notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* ForensicAnalysis */}
          <h3 className="text-lg font-semibold text-foreground mt-8 mb-3">
            5.5 ForensicAnalysis (60+ columns)
          </h3>
          <p className="text-sm text-muted-foreground mb-4">
            One-to-one relationship with Claims. Stores results from every AI
            pipeline stage. Key column groups:
          </p>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {[
              { group: "EXIF Metadata", fields: "timestamp, GPS lat/lon, location name, camera make/model" },
              { group: "OCR Results", fields: "plate text, confidence score, raw texts" },
              { group: "YOLO Detection", fields: "damage detected, detections JSON, severity, summary" },
              { group: "Vehicle Identity", fields: "make, model, year, color, plate text, match status" },
              { group: "Damage Assessment", fields: "type, severity score, panels, impact point, airbags, fluid leaks" },
              { group: "Forensic Indicators", fields: "screen recapture, UI elements, watermarks, blur, shadows" },
              { group: "Pre-existing Damage", fields: "detected flag, indicators, description, confidence" },
              { group: "Scene Context", fields: "location type, time of day, weather, debris, traffic" },
              { group: "Risk Assessment", fields: "risk flags, fraud probability, fraud score, confidence score" },
              { group: "Final Decision", fields: "recommendation, reasoning, human review priority" },
            ].map((item) => (
              <div key={item.group} className="bg-section border border-border rounded-lg p-4">
                <p className="font-semibold text-sm text-foreground mb-1">{item.group}</p>
                <p className="text-xs text-muted-foreground">{item.fields}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── Section 6: AI Pipeline ───────────────────────────────────── */}
        <section id="ai-pipeline" className="mb-16 page-break">
          <SectionHeader number="6" title="AI Pipeline (Core Innovation)" />
          <p className="leading-relaxed text-foreground/90 mb-6">
            The claim analysis happens in 5 sequential stages orchestrated by{" "}
            <code className="font-mono text-sm bg-muted px-1 rounded">ai_orchestrator.py</code>.
            The key design principle is: <strong>AI extracts facts. Python rules make decisions.</strong>
          </p>

          {/* Stage 1 */}
          <div className="border-l-4 border-accent pl-6 mb-8">
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Stage 1: EXIF Metadata Extraction
            </h3>
            <p className="text-sm text-muted-foreground mb-1">
              <span className="font-mono bg-muted px-1 rounded text-xs">exif_service.py</span>
            </p>
            <ul className="list-disc list-inside text-sm text-foreground/90 leading-relaxed">
              <li>Reads EXIF data from uploaded images using Pillow</li>
              <li>Extracts: timestamp, GPS coordinates, camera make/model</li>
              <li>Falls back to filename parsing (supports Google Pixel, Samsung, iPhone, WhatsApp naming patterns)</li>
              <li>Uses Geopy/Nominatim for reverse geocoding GPS to location names</li>
            </ul>
          </div>

          {/* Stage 2 */}
          <div className="border-l-4 border-accent pl-6 mb-8">
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Stage 2: OCR Number Plate Extraction
            </h3>
            <p className="text-sm text-muted-foreground mb-1">
              <span className="font-mono bg-muted px-1 rounded text-xs">ocr_service.py</span>
            </p>
            <ul className="list-disc list-inside text-sm text-foreground/90 leading-relaxed">
              <li>Uses EasyOCR on the front-view image (self-hosted, no API cost)</li>
              <li>Filters for alphanumeric text with 4-15 characters containing both letters and numbers</li>
              <li>Returns best match plate text + confidence score</li>
            </ul>
          </div>

          {/* Stage 3 */}
          <div className="border-l-4 border-accent pl-6 mb-8">
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Stage 3: YOLOv8 Damage Detection
            </h3>
            <p className="text-sm text-muted-foreground mb-1">
              <span className="font-mono bg-muted px-1 rounded text-xs">yolov8_damage_service.py</span>
            </p>
            <ul className="list-disc list-inside text-sm text-foreground/90 leading-relaxed">
              <li>Self-hosted model, runs locally (GPU-accelerated if CUDA available)</li>
              <li>Uses specialized car damage model from Hugging Face: <code className="font-mono text-xs bg-muted px-1 rounded">nezahatkorkmaz/car-damage-level-detection-yolov8</code></li>
              <li>Falls back to base YOLOv8n if specialized model is unavailable</li>
              <li>Returns: damage detected (bool), bounding box detections, area %, severity (minor/moderate/severe), affected parts</li>
            </ul>
          </div>

          {/* Stage 4 */}
          <div className="border-l-4 border-accent pl-6 mb-8">
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Stage 4: Groq Vision AI Data Extraction
            </h3>
            <p className="text-sm text-muted-foreground mb-1">
              <span className="font-mono bg-muted px-1 rounded text-xs">groq_service.py</span>
            </p>
            <ul className="list-disc list-inside text-sm text-foreground/90 leading-relaxed">
              <li>Sends up to 2 images (resized to 1280x720, JPEG quality 80) to Groq API</li>
              <li>Uses <code className="font-mono text-xs bg-muted px-1 rounded">llama-3.2-11b-vision-preview</code> model (falls back to LLaMA 4 Scout)</li>
              <li>Temperature = 0.0 (deterministic), max 1500 tokens, JSON response format</li>
              <li>Extracts 4 categories of pure facts: Identity, Damage, Forensics, Scene</li>
              <li>AI only extracts facts -- it NEVER makes decisions</li>
            </ul>
          </div>

          {/* Stage 5 */}
          <div className="border-l-4 border-primary pl-6 mb-8">
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Stage 5: Rule-Based Verification Engine v2.0
            </h3>
            <p className="text-sm text-muted-foreground mb-1">
              <span className="font-mono bg-muted px-1 rounded text-xs">verification_rules.py</span> -- 1,164 lines of deterministic logic
            </p>
            <p className="text-sm text-foreground/90 mb-4">
              This is the core decision-making engine. It runs 16 checks across
              5 phases, producing a fully auditable result with rule ID, name,
              reason, severity, and phase for every check.
            </p>
          </div>
        </section>

        {/* ── Section 7: Verification Engine Detail ────────────────────── */}
        <section id="verification" className="mb-16 page-break">
          <SectionHeader number="7" title="Verification Engine -- 16 Checks x 5 Phases" />

          {/* Phase A */}
          <h3 className="text-base font-semibold text-primary mt-6 mb-3">Phase A: Integrity & Source Checks</h3>
          <div className="overflow-x-auto mb-6">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-primary text-primary-foreground">
                  <th className="p-2 text-left font-semibold w-8">#</th>
                  <th className="p-2 text-left font-semibold">Check Name</th>
                  <th className="p-2 text-left font-semibold">Severity</th>
                  <th className="p-2 text-left font-semibold">Description</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["1", "Image Quality Gate", "CRITICAL / HIGH", "Screen recapture = CRITICAL; blur = HIGH; low quality = MEDIUM"],
                  ["2", "Metadata Verification", "HIGH / LOW", "Missing EXIF timestamp = HIGH; missing GPS = LOW; GPS mismatch = MEDIUM"],
                  ["3", "Reverse Image Search", "CRITICAL / MEDIUM", "Detects stock or recycled internet photos"],
                  ["4", "Digital Forgery Detection", "CRITICAL", "Editing, inconsistent lighting/shadows, watermarks, compression artifacts"],
                ].map(([num, name, severity, desc]) => (
                  <tr key={num} className="border-b border-border">
                    <td className="p-2 font-mono text-xs">{num}</td>
                    <td className="p-2 font-medium">{name}</td>
                    <td className="p-2 text-xs font-mono">{severity}</td>
                    <td className="p-2 text-muted-foreground text-xs">{desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Phase B */}
          <h3 className="text-base font-semibold text-primary mt-6 mb-3">Phase B: Vehicle & Damage Verification</h3>
          <div className="overflow-x-auto mb-6">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-primary text-primary-foreground">
                  <th className="p-2 text-left font-semibold w-8">#</th>
                  <th className="p-2 text-left font-semibold">Check Name</th>
                  <th className="p-2 text-left font-semibold">Severity</th>
                  <th className="p-2 text-left font-semibold">Description</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["5", "Vehicle Match", "CRITICAL", "Make/model vs policy; also checks color mismatch (MEDIUM)"],
                  ["6", "License Plate Match", "CRITICAL", "OCR plate text vs policy registration (strict exact match)"],
                  ["7", "Chase Number (VIN) Match", "HIGH", "VIN/chassis number verification"],
                  ["8", "Pre-existing Damage", "HIGH", "Rust, dirt in damage area, faded paint indicators"],
                  ["9", "YOLO Damage Corroboration", "HIGH / MEDIUM", "Cross-validates YOLO vs Groq AI severity (v2 NEW)"],
                  ["10", "Totalled Vehicle Markers", "HIGH", "Expects airbag/fluid/parts markers when severity = totaled (v2 NEW)"],
                ].map(([num, name, severity, desc]) => (
                  <tr key={num} className="border-b border-border">
                    <td className="p-2 font-mono text-xs">{num}</td>
                    <td className="p-2 font-medium">{name}</td>
                    <td className="p-2 text-xs font-mono">{severity}</td>
                    <td className="p-2 text-muted-foreground text-xs">{desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Phase C */}
          <h3 className="text-base font-semibold text-primary mt-6 mb-3">Phase C: Contextual Consistency</h3>
          <div className="overflow-x-auto mb-6">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-primary text-primary-foreground">
                  <th className="p-2 text-left font-semibold w-8">#</th>
                  <th className="p-2 text-left font-semibold">Check Name</th>
                  <th className="p-2 text-left font-semibold">Severity</th>
                  <th className="p-2 text-left font-semibold">Description</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["11", "Narrative Consistency", "HIGH", "User description vs visual evidence alignment"],
                  ["12", "Multi-Image Consistency", "HIGH", "Detects mixed-incident photos across uploads (v2 NEW)"],
                ].map(([num, name, severity, desc]) => (
                  <tr key={num} className="border-b border-border">
                    <td className="p-2 font-mono text-xs">{num}</td>
                    <td className="p-2 font-medium">{name}</td>
                    <td className="p-2 text-xs font-mono">{severity}</td>
                    <td className="p-2 text-muted-foreground text-xs">{desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Phase D */}
          <h3 className="text-base font-semibold text-primary mt-6 mb-3">Phase D: Financial Sanity</h3>
          <div className="overflow-x-auto mb-6">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-primary text-primary-foreground">
                  <th className="p-2 text-left font-semibold w-8">#</th>
                  <th className="p-2 text-left font-semibold">Check Name</th>
                  <th className="p-2 text-left font-semibold">Severity</th>
                  <th className="p-2 text-left font-semibold">Description</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["13", "Amount Threshold", "MEDIUM", "Auto-approve under Rs.20,000; flag above"],
                  ["14", "Damage-Cost Sanity", "CRITICAL / HIGH", "No damage + claim = CRITICAL; inflated estimate = HIGH (v2 NEW)"],
                ].map(([num, name, severity, desc]) => (
                  <tr key={num} className="border-b border-border">
                    <td className="p-2 font-mono text-xs">{num}</td>
                    <td className="p-2 font-medium">{name}</td>
                    <td className="p-2 text-xs font-mono">{severity}</td>
                    <td className="p-2 text-muted-foreground text-xs">{desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Phase E */}
          <h3 className="text-base font-semibold text-primary mt-6 mb-3">Phase E: Policy & History Validation</h3>
          <div className="overflow-x-auto mb-6">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-primary text-primary-foreground">
                  <th className="p-2 text-left font-semibold w-8">#</th>
                  <th className="p-2 text-left font-semibold">Check Name</th>
                  <th className="p-2 text-left font-semibold">Severity</th>
                  <th className="p-2 text-left font-semibold">Description</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["15", "Policy Active & Coverage", "CRITICAL", "Validates policy status, date window, coverage limit (v2 NEW)"],
                  ["16", "Duplicate / Repeat Claim Guard", "HIGH", "Same plate/user within 30 days flagged; fraud ring detection (v2 NEW)"],
                ].map(([num, name, severity, desc]) => (
                  <tr key={num} className="border-b border-border">
                    <td className="p-2 font-mono text-xs">{num}</td>
                    <td className="p-2 font-medium">{name}</td>
                    <td className="p-2 text-xs font-mono">{severity}</td>
                    <td className="p-2 text-muted-foreground text-xs">{desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Decision Matrix */}
          <h3 className="text-base font-semibold text-foreground mt-8 mb-3">Decision Matrix</h3>
          <div className="bg-section border border-border rounded-lg p-6">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="flex gap-3 items-start">
                <div className="w-3 h-3 rounded-full bg-green-600 mt-1 shrink-0" />
                <div>
                  <p className="font-semibold text-sm">APPROVED</p>
                  <p className="text-xs text-muted-foreground">No failures, or only LOW severity (score {"<"} 2)</p>
                </div>
              </div>
              <div className="flex gap-3 items-start">
                <div className="w-3 h-3 rounded-full bg-amber-500 mt-1 shrink-0" />
                <div>
                  <p className="font-semibold text-sm">FLAGGED</p>
                  <p className="text-xs text-muted-foreground">{"Score >= 2 but < 10; requires human review"}</p>
                </div>
              </div>
              <div className="flex gap-3 items-start">
                <div className="w-3 h-3 rounded-full bg-red-600 mt-1 shrink-0" />
                <div>
                  <p className="font-semibold text-sm">REJECTED</p>
                  <p className="text-xs text-muted-foreground">{"Any CRITICAL failure, or score >= 10"}</p>
                </div>
              </div>
              <div className="flex gap-3 items-start">
                <div className="w-3 h-3 rounded-full bg-primary mt-1 shrink-0" />
                <div>
                  <p className="font-semibold text-sm">Compounding Multiplier</p>
                  <p className="text-xs text-muted-foreground">{"3+ HIGH/CRITICAL failures -> score x 1.5"}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Section 8: Repair Cost Estimation ────────────────────────── */}
        <section id="cost-estimation" className="mb-16 page-break">
          <SectionHeader number="8" title="Repair Cost Estimation" />
          <p className="leading-relaxed text-foreground/90 mb-4">
            The system maintains a curated Part Price Table with 30+ vehicle
            parts (bumpers, doors, fenders, hood, windshield, headlights,
            mirrors, frame, engine, suspension, etc.). Prices are in USD
            (industry standard) and converted to INR at a rate of 84.0.
          </p>
          <ul className="list-disc list-inside text-sm text-foreground/90 leading-relaxed mb-6">
            <li>Groq AI identifies damaged panels from images</li>
            <li>Repair estimator maps panel names to canonical keys (includes fuzzy alias matching)</li>
            <li>Returns part-by-part breakdown with USD and INR min/max ranges</li>
            <li>Handles aliases like {"\"bonnet\" -> \"hood\""}, {"\"bumper_front\" -> \"front_bumper\""}</li>
          </ul>
        </section>

        {/* ── Section 9: Authentication ────────────────────────────────── */}
        <section id="authentication" className="mb-16">
          <SectionHeader number="9" title="Authentication & Authorization" />
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-primary text-primary-foreground">
                  <th className="p-3 text-left font-semibold">Feature</th>
                  <th className="p-3 text-left font-semibold">Implementation</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["Token Type", "JWT with HS256 algorithm, 60-minute expiry"],
                  ["Password Hashing", "PBKDF2-SHA256 via passlib"],
                  ["User Roles", "user, agent, admin (enforced on both frontend + backend)"],
                  ["Token Transport", "OAuth2PasswordBearer (Authorization header)"],
                  ["Admin Auto-creation", "admin@autoclaim.com created on server startup"],
                  ["Agent Registration", "Admin-only endpoint /admin/register-agent"],
                  ["Frontend Guards", "ProtectedRoute component with role-based redirection"],
                ].map(([feature, impl], i) => (
                  <tr key={feature} className={i % 2 === 0 ? "bg-background" : "bg-section"}>
                    <td className="p-3 border-b border-border font-medium">{feature}</td>
                    <td className="p-3 border-b border-border text-muted-foreground">{impl}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* ── Section 10: API Endpoints ────────────────────────────────── */}
        <section id="api" className="mb-16 page-break">
          <SectionHeader number="10" title="REST API Endpoints" />
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-primary text-primary-foreground">
                  <th className="p-2 text-left font-semibold">Method</th>
                  <th className="p-2 text-left font-semibold">Endpoint</th>
                  <th className="p-2 text-left font-semibold">Auth</th>
                  <th className="p-2 text-left font-semibold">Description</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["POST", "/register", "Public", "Register new user"],
                  ["POST", "/login", "Public", "Get JWT token"],
                  ["GET", "/me", "User", "Get current user info"],
                  ["POST", "/claims", "User", "Submit claim with images (async AI processing)"],
                  ["GET", "/claims/my", "User", "Get user's own claims"],
                  ["GET", "/claims/all", "Admin", "Get all claims from all users"],
                  ["GET", "/claims/{id}", "Owner/Admin", "Get full claim details + forensic analysis"],
                  ["PUT", "/claims/{id}/status", "Admin", "Update claim status"],
                  ["POST", "/claims/{id}/analyze", "Admin", "Re-run AI analysis on a claim"],
                  ["POST", "/admin/register-agent", "Admin", "Register a new agent account"],
                  ["GET", "/admin/agents", "Admin", "List all agents"],
                  ["GET", "/health", "Public", "Health check with AI service status"],
                ].map(([method, endpoint, auth, desc]) => (
                  <tr key={endpoint} className="border-b border-border">
                    <td className="p-2 font-mono text-xs font-bold">{method}</td>
                    <td className="p-2 font-mono text-xs">{endpoint}</td>
                    <td className="p-2 text-xs">{auth}</td>
                    <td className="p-2 text-muted-foreground text-xs">{desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* ── Section 11: Frontend ─────────────────────────────────────── */}
        <section id="frontend" className="mb-16">
          <SectionHeader number="11" title="Frontend Architecture" />
          <p className="leading-relaxed text-foreground/90 mb-6">
            Built with React 19 + Vite 7 + React Router 7 + Bootstrap 5. Key
            features include real-time polling (every 3 seconds while processing),
            multi-file upload, role-based routing, and a comprehensive forensic
            results display.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="bg-primary text-primary-foreground">
                  <th className="p-2 text-left font-semibold">Route</th>
                  <th className="p-2 text-left font-semibold">Component</th>
                  <th className="p-2 text-left font-semibold">Access</th>
                  <th className="p-2 text-left font-semibold">Purpose</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ["/", "Homepage", "Public", "Landing page with 'How it Works'"],
                  ["/login", "Login", "Public", "User authentication"],
                  ["/register", "Register", "Public", "User registration"],
                  ["/upload", "ClaimUpload", "Auth", "Multi-file upload form"],
                  ["/dashboard", "UserDashboard", "User", "View own claims, filter, stats"],
                  ["/admin", "AdminDashboard", "Admin", "All claims, approve/reject, manage agents"],
                  ["/claim/:id", "ViewClaim", "Auth", "Full forensic analysis view"],
                ].map(([route, comp, access, purpose]) => (
                  <tr key={route} className="border-b border-border">
                    <td className="p-2 font-mono text-xs">{route}</td>
                    <td className="p-2 font-medium text-xs">{comp}</td>
                    <td className="p-2 text-xs">{access}</td>
                    <td className="p-2 text-muted-foreground text-xs">{purpose}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* ── Section 12: Fraud Detection ──────────────────────────────── */}
        <section id="fraud-detection" className="mb-16 page-break">
          <SectionHeader number="12" title="Fraud Detection Capabilities" />
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {[
              { title: "Fake/Edited Images", desc: "Screen recaptures, UI elements, watermarks, inconsistent lighting/shadows" },
              { title: "Wrong Vehicle Photos", desc: "Vehicle make/model/color mismatch with policy data" },
              { title: "Wrong Vehicle Plate", desc: "OCR plate text vs policy registration number comparison" },
              { title: "Pre-existing Damage", desc: "Rust, dirt accumulation in damage area, faded paint around impact" },
              { title: "Inflated Cost Claims", desc: "Damage severity vs claimed amount sanity check (2x limit)" },
              { title: "Duplicate Claims", desc: "Same vehicle/user claiming within 30-day window" },
              { title: "Stripped Metadata", desc: "Missing EXIF indicates possible screenshot or edited image" },
              { title: "Stock Photos", desc: "Detection of professional/staged imagery from the internet" },
              { title: "Narrative Conflicts", desc: "Description says 'rear-ended' but damage is on front bumper" },
              { title: "Totalled Vehicle Fraud", desc: "Claims totalled without airbag/fluid leak/missing parts evidence" },
            ].map((item) => (
              <div key={item.title} className="bg-section border border-border rounded-lg p-4">
                <p className="font-semibold text-sm text-foreground mb-1">{item.title}</p>
                <p className="text-xs text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── Section 13: Design Principles ────────────────────────────── */}
        <section id="design-principles" className="mb-16">
          <SectionHeader number="13" title="Key Design Principles" />
          <div className="space-y-4">
            {[
              { principle: "AI Extracts, Rules Decide", detail: "Groq Vision extracts structured facts. Python code makes all decisions. Every decision has a clear audit trail with rule ID, reason, and severity. This is critical for regulatory compliance in insurance." },
              { principle: "Defense in Depth", detail: "16 verification checks across 5 phases catch different types of fraud. No single check is the sole gatekeeper -- correlated failures are detected via the compounding multiplier." },
              { principle: "Self-Hosted Where Possible", detail: "YOLOv8 and EasyOCR run locally (free, fast, no API costs). Only Groq uses an external API. This keeps operational costs low." },
              { principle: "Asynchronous Processing", detail: "Claims are processed via FastAPI BackgroundTasks. Users get an immediate response while the AI pipeline runs. Frontend polls for updates." },
              { principle: "Deterministic Decisions", detail: "Temperature = 0.0 for Groq API. RuleConfig stores all thresholds. Same input always produces the same output." },
              { principle: "Separation of Concerns", detail: "Each service (EXIF, OCR, YOLO, Groq, Verification, Repair Estimator) is an independent module. The orchestrator coordinates them." },
            ].map((item, i) => (
              <div key={i} className="flex gap-4">
                <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold shrink-0">
                  {i + 1}
                </div>
                <div>
                  <p className="font-semibold text-foreground">{item.principle}</p>
                  <p className="text-sm text-muted-foreground leading-relaxed">{item.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ── Section 14: Viva Questions ───────────────────────────────── */}
        <section id="viva-questions" className="mb-16 page-break">
          <SectionHeader number="14" title="Anticipated Viva Questions & Answers" />
          <div className="space-y-6">
            {[
              {
                q: "Why not let the AI make decisions directly?",
                a: "AI models are probabilistic and can hallucinate. By separating data extraction (AI) from decision-making (Python rules), every decision has a clear audit trail with a rule ID, reason, and severity. This is critical for regulatory compliance in insurance. The rule engine is deterministic -- same input always gives the same output."
              },
              {
                q: "Why use both YOLOv8 and Groq for damage detection?",
                a: "YOLOv8 is a specialized damage detection model that runs locally (free, fast). Groq provides broader understanding (vehicle identity, forensics, scene context). Check 9 in the verification engine cross-validates both -- if they disagree on severity, it's flagged. This is defense-in-depth: if one model is fooled, the other catches it."
              },
              {
                q: "How do you handle images without EXIF data?",
                a: "The system falls back to filename parsing -- it supports Google Pixel (PXL_), Samsung (IMG_), iPhone, WhatsApp (IMG-...-WA), and Screenshot patterns. If no metadata is available at all, it's flagged as HIGH severity in Check 2 because it could indicate a screenshot or digitally edited image."
              },
              {
                q: "What if the Groq API is down?",
                a: "The system gracefully degrades. YOLOv8 still provides damage detection results locally. The claim gets flagged for manual review rather than failing silently. The health endpoint reports AI service status."
              },
              {
                q: "How is the repair cost estimated?",
                a: "We maintain a curated Part Price Table with 30+ vehicle parts and USD industry-standard pricing. The Groq AI identifies damaged panels, and our repair estimator maps those to the price table with fuzzy alias matching. Costs are converted to INR at rate 84.0. Returns part-by-part breakdown."
              },
              {
                q: "What database are you using and why?",
                a: "SQLite via SQLAlchemy ORM. It's lightweight, file-based, and perfect for a project demo. The ORM layer means switching to PostgreSQL for production only requires changing the connection string -- zero code changes."
              },
              {
                q: "How is authentication implemented?",
                a: "JWT tokens with HS256 algorithm and 60-minute expiry. Passwords are hashed with PBKDF2-SHA256. Backend uses FastAPI's dependency injection with OAuth2PasswordBearer for clean, reusable auth guards. Three roles: user, agent, admin."
              },
              {
                q: "What is the confidence score?",
                a: "A weighted 0-100 score computed by the verification engine. It starts with the raw pass rate (passed / total checks), then penalizes by severity score (each CRITICAL reduces confidence more than LOW). The formula: max(0, (pass_rate - severity_penalty)) x 100."
              },
              {
                q: "How does the compounding multiplier work?",
                a: "If a claim has 3 or more HIGH/CRITICAL failures across different checks, the total severity score is multiplied by 1.5x. This catches correlated fraud patterns where individually each issue seems moderate, but together they indicate fraud."
              },
              {
                q: "Can the system be gamed?",
                a: "No system is foolproof, but AutoClaim uses defense-in-depth: EXIF checks catch edited images, OCR catches wrong vehicles, YOLO cross-validates Groq damage assessment, pre-existing indicators catch old damage, and duplicate detection catches repeat fraud. Claims must pass all 16 checks."
              },
              {
                q: "What are the v2.0 improvements?",
                a: "7 new checks added: Image Quality Gate (Check 1), YOLO Damage Corroboration (Check 9), Totalled Vehicle Markers (Check 10), Damage-Cost Sanity (Check 14), Multi-Image Consistency (Check 12), Policy Active & Coverage (Check 15), Duplicate Claim Guard (Check 16). Also added the compounding multiplier and weighted confidence scoring."
              },
              {
                q: "How does background processing work?",
                a: "User submits claim -> immediate HTTP 200 with claim_id (status: 'processing'). FastAPI BackgroundTasks runs the full 5-stage AI pipeline. Results stored in ForensicAnalysis table. Claim status updated to 'completed' or 'failed'. Frontend polls every 3 seconds for updates."
              },
            ].map((item, i) => (
              <div key={i} className="border border-border rounded-lg overflow-hidden">
                <div className="bg-primary/5 px-4 py-3 border-b border-border">
                  <p className="font-semibold text-sm text-foreground">
                    Q{i + 1}: {item.q}
                  </p>
                </div>
                <div className="px-4 py-3">
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {item.a}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ── Section 15: Future Enhancements ──────────────────────────── */}
        <section id="future" className="mb-16">
          <SectionHeader number="15" title="Future Enhancements" />
          <ul className="list-disc list-inside text-sm text-foreground/90 leading-loose">
            <li>Migrate from SQLite to PostgreSQL for production deployment</li>
            <li>Add real-time WebSocket updates instead of polling</li>
            <li>Implement multi-image consistency analysis with cross-image comparison</li>
            <li>Integrate telematics data (speed, impact force) from vehicle IoT sensors</li>
            <li>Deploy on cloud with GPU for faster YOLOv8 inference</li>
            <li>Add weather API integration for cross-verification with scene context</li>
            <li>Implement 3D damage modeling from multiple angle photographs</li>
            <li>Add PDF report generation for claim reports</li>
            <li>Integrate with insurance provider APIs for real-time policy validation</li>
          </ul>
        </section>

        {/* ── Section 16: Python Dependencies ──────────────────────────── */}
        <section id="dependencies" className="mb-16">
          <SectionHeader number="16" title="Dependencies" />
          <h3 className="text-base font-semibold text-foreground mt-4 mb-3">Backend (Python)</h3>
          <div className="bg-foreground text-primary-foreground rounded-lg p-4 font-mono text-xs leading-relaxed mb-6">
            <pre>{`fastapi          # Web framework
uvicorn          # ASGI server
sqlalchemy       # ORM
psycopg2-binary  # PostgreSQL driver (for future migration)
pyjwt            # JWT token handling
passlib[bcrypt]  # Password hashing (PBKDF2-SHA256)
python-multipart # File upload support
python-dotenv    # Environment variables
easyocr          # Number plate OCR
pillow           # Image processing + EXIF extraction
geopy            # Reverse geocoding
ultralytics      # YOLOv8 framework
torch            # PyTorch (YOLO backend)
torchvision      # Vision utilities
huggingface-hub  # Model downloads
groq             # Groq API client`}</pre>
          </div>
          <h3 className="text-base font-semibold text-foreground mt-4 mb-3">Frontend (Node.js)</h3>
          <div className="bg-foreground text-primary-foreground rounded-lg p-4 font-mono text-xs leading-relaxed">
            <pre>{`react@19         # UI framework
react-dom@19     # React DOM renderer
react-router@7   # Client-side routing
bootstrap@5      # CSS framework
axios            # HTTP client
vite@7           # Build tool`}</pre>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-border pt-8 mt-16 text-center">
          <p className="text-sm text-muted-foreground">
            AutoClaim v2.0.0 -- AI-Powered Vehicle Insurance Claim Processing System
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            Project Report generated February 2026
          </p>
        </footer>
      </div>
    </main>
  );
}
