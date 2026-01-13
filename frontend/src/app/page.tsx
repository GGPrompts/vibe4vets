import { SearchBar } from '@/components/search-bar';
import { CategoryButtons } from '@/components/category-buttons';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="w-full max-w-2xl text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
          Vibe4Vets
        </h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Find employment, training, housing, and legal resources for veterans
          nationwide.
        </p>

        <div className="mt-8">
          <SearchBar />
        </div>

        <div className="mt-8">
          <CategoryButtons />
        </div>

        <p className="mt-12 text-sm text-muted-foreground">
          Built with transparency. We use AI and web scraping to aggregate
          resources beyond VA.gov.
        </p>
      </div>
    </main>
  );
}
