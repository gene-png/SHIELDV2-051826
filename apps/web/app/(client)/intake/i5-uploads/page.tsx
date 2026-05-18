import Link from "next/link";

// Drag-and-drop document upload with mandatory redaction disclosure (Master
// Spec §12) lands with §6 file-upload router. Stub for now.
export default function I5UploadsPage() {
  return (
    <div>
      <h2 className="text-xl font-semibold text-navy">Upload supporting documents</h2>
      <p className="mt-2 text-sm text-n-700">
        Network diagrams, asset inventories, policies, prior assessment reports — anything that
        helps us avoid asking you the same questions again. You can add more after intake.
      </p>

      <div className="mt-4 rounded-card border border-warning/40 bg-warning/5 p-4 text-sm text-n-700">
        <strong>Heads up:</strong> uploaded files are scanned for PII before any AI analysis
        (emails, phone numbers, names, addresses, SSN/EIN/CAGE/contract numbers, signature
        blocks). Your consultant reviews redactions before the first AI call per engagement.
      </div>

      <div className="mt-6 rounded-card border border-dashed border-n-300 bg-white p-12 text-center text-n-500">
        Drag-and-drop uploader lands with the §6 file-upload router. Continue for now.
      </div>

      <div className="mt-6 flex justify-between">
        <Link
          href="/intake/i4-questionnaire"
          className="rounded-control border border-n-300 px-4 py-2 text-sm text-n-700 hover:bg-n-100"
        >
          ← Back
        </Link>
        <Link
          href="/intake/i6-submit"
          className="rounded-control bg-gov-blue px-5 py-2.5 text-sm font-semibold text-white shadow-card"
        >
          Continue
        </Link>
      </div>
    </div>
  );
}
