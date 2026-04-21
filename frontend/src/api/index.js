const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function submitCompare(text) {
  const res = await fetch(`${BASE_URL}/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error(`Compare failed: ${res.status}`);
  return res.json();
}
