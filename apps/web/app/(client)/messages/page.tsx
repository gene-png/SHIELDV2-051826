export default function MessagesPage() {
  return (
    <div className="mx-auto max-w-4xl">
      <h1 className="text-2xl font-bold text-navy">Messages</h1>
      <p className="mt-1 text-sm text-n-500">
        Lightweight, audit-logged thread between you and your consultant. No attachments — upload via
        <a href="/documents" className="text-gov-blue underline">
          {" "}
          /documents
        </a>
        .
      </p>

      <section className="mt-8 rounded-card border border-dashed border-n-300 bg-white p-12 text-center text-n-500">
        Threads + post-box land with §12 of the execution plan.
      </section>
    </div>
  );
}
