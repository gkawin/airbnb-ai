import getPocketbase from "@/helpers/pocketbase";

export default async function Home() {
  const pb = await getPocketbase();

  const allusers = await pb.health.check();

  return (
    <main className="bg-white">
      <pre>{JSON.stringify(allusers, null, 2)}</pre>
    </main>
  );
}
