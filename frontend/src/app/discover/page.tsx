import { redirect } from 'next/navigation';

export default function DiscoverPage() {
  redirect('/search?sort=newest');
}
