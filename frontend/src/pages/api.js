// API utility for fetching sweets
export async function fetchSweets(page = 1, size = 20) {
  const res = await fetch(`/api/sweets/search?page=${page}&size=${size}`);
  if (!res.ok) throw new Error("Failed to fetch sweets");
  return res.json();
}
