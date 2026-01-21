'use client';

import { EligibilityWizard } from '@/components/EligibilityWizard';

/**
 * DEV PREVIEW: Eligibility Wizard Component
 *
 * This page exists for development reference only.
 * The wizard filters (age, household, income, housing status, dietary needs)
 * could be integrated into the landing page as a "phase 2" enhancement
 * alongside the existing location + category filters.
 *
 * Access at: /wizard
 */
export default function WizardPreviewPage() {
  return (
    <main className="min-h-screen bg-gray-50 p-8 pt-24">
      <div className="mx-auto max-w-4xl">
        <div className="mb-6 rounded-lg bg-amber-50 border border-amber-200 p-4 text-sm text-amber-800">
          <strong>Dev Preview:</strong> This component is not yet integrated into the site.
          It shows additional eligibility filters that could enhance the landing page.
        </div>

        <h1 className="text-2xl font-bold mb-6">Eligibility Wizard</h1>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <EligibilityWizard />
        </div>
      </div>
    </main>
  );
}
