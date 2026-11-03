// Stands in for the app's session check outside Next.js: a fixed test user.
// Only for local harness runs against the local database.
export async function requireUser() {
	return { id: "00000000-0000-0000-0000-000000000001", email: "harness@localhost" };
}
