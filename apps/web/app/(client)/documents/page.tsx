export default function DocumentsPage() {
  return (
    <div className="mx-auto max-w-5xl">
      <h1 className="text-2xl font-bold text-navy">Documents</h1>
      <p className="mt-1 text-sm text-n-500">
        What you&rsquo;ve shared with your consultant and what they&rsquo;ve released back.
      </p>

      <section className="mt-8 rounded-card border border-n-200 bg-white p-6 shadow-card">
        <h2 className="text-lg font-semibold text-navy">What you&rsquo;ve shared</h2>
        <p className="mt-2 text-sm text-n-500">
          Drag-and-drop uploads land with §3.6 file-storage wiring.
        </p>
      </section>

      <section className="mt-6 rounded-card border border-n-200 bg-white p-6 shadow-card">
        <h2 className="text-lg font-semibold text-navy">What you&rsquo;ve received</h2>
        <p className="mt-2 text-sm text-n-500">
          Released deliverables (PDF + XLSX) appear here when your consultant releases them.
        </p>
      </section>
    </div>
  );
}
