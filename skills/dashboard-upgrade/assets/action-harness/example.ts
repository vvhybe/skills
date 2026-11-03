// Example scenario: five parallel check-ins for one client must write exactly one ledger row.
// Replace the imports and the body with the target repo's actions and tables (these are the reference implementation's).
import assert from "node:assert/strict";
import { randomUUID } from "node:crypto";

import { checkInClientAction } from "@/lib/actions/schedule/attendance";
import { db } from "@/services/database";
import * as s from "@/services/database/schema";

async function main() {
	// Warm the pool so the parallel calls really run on separate connections.
	await Promise.all(Array.from({ length: 10 }, () => db.$client`select pg_sleep(0.1)`));

	const tag = randomUUID().slice(0, 6);
	const [client] = await db
		.insert(s.clients)
		.values({ fullName: `Harness ${tag}`, phone: "+212600000000", birthDate: "1990-01-01", gender: "female" })
		.returning();
	const [wallet] = await db
		.insert(s.clientWallets)
		.values({ clientId: client.id, remainingCredits: 5, status: "active" })
		.returning();

	await Promise.allSettled(
		Array.from({ length: 5 }, () => checkInClientAction(client.id, `evt-${tag}`, "group")),
	);

	const ledger = await db.query.attendanceLedger.findMany({ where: (l, { eq }) => eq(l.walletId, wallet.id) });
	const after = await db.query.clientWallets.findFirst({ where: (w, { eq }) => eq(w.id, wallet.id) });
	assert.equal(ledger.length, 1, "one check-in recorded");
	assert.equal(after?.remainingCredits, 4, "one credit used");
	console.log("✓ five taps, one check-in");
	process.exit(0);
}

main().catch((error) => {
	console.error(error);
	process.exit(1);
});
