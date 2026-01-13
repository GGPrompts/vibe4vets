export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="max-w-2xl text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
          Vibe4Vets
        </h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Find employment, training, housing, and legal resources for veterans
          nationwide.
        </p>

        <div className="mt-8">
          <div className="relative">
            <input
              type="text"
              placeholder="Search for resources..."
              className="w-full rounded-full border border-input bg-background px-6 py-4 text-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <button className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full bg-primary px-6 py-2 text-primary-foreground">
              Search
            </button>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <CategoryButton label="Employment" emoji="💼" />
          <CategoryButton label="Training" emoji="📚" />
          <CategoryButton label="Housing" emoji="🏠" />
          <CategoryButton label="Legal" emoji="⚖️" />
        </div>

        <p className="mt-12 text-sm text-muted-foreground">
          Built with transparency. We use AI and web scraping to aggregate
          resources beyond VA.gov.
        </p>
      </div>
    </main>
  );
}

function CategoryButton({ label, emoji }: { label: string; emoji: string }) {
  return (
    <button className="flex items-center gap-2 rounded-lg border border-input bg-background px-4 py-2 text-sm font-medium hover:bg-accent hover:text-accent-foreground">
      <span>{emoji}</span>
      <span>{label}</span>
    </button>
  );
}
