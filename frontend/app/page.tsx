export default async function Home() {
  const api = process.env.NEXT_PUBLIC_API_URL;

  const res = await fetch(`${api}/`, { cache: "no-store" });
  const data = await res.json();

  return (
    <main style={{ padding: 24, fontFamily: "Arial" }}>
      <h1>Hazm Tuwaiq Platform</h1>
      <p><b>Status:</b> {data.status}</p>
      <p><b>Service:</b> {data.service}</p>
      <p><b>Time (UTC):</b> {data.time_utc}</p>

      <hr style={{ margin: "20px 0" }} />

      <a href={`${api}/docs`} target="_blank" rel="noreferrer">
        Open API Docs
      </a>
    </main>
  );
}
