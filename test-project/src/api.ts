// Issue: hardcoded API URL
const API_URL = 'https://api.example.com';

export async function fetchData() {
  const response = await fetch(API_URL);
  return response.json();
}
