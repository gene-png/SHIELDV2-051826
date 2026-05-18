import { redirect } from "next/navigation";

// `/intake` lands clients on step I1. The route exists so the welcome page
// and post-signup redirect have a stable target.
export default function IntakeIndexPage() {
  redirect("/intake/i1-services");
}
