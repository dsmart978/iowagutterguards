export async function onRequest({ request, env }) {
  // Only allow POST
  if (request.method !== "POST") {
    return new Response("Method Not Allowed", {
      status: 405,
      headers: { "Allow": "POST" },
    });
  }

  // Helper: normalize keys like "Home size" -> "homesiz", "Phone Number" -> "phonenumber"
  const normKey = (k) =>
    String(k || "")
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "");

  // Read body (supports form posts + JSON)
  let raw = {};
  const ct = request.headers.get("content-type") || "";

  try {
    if (ct.includes("application/json")) {
      raw = (await request.json()) || {};
    } else {
      const fd = await request.formData();
      raw = Object.fromEntries(fd.entries());
    }
  } catch (e) {
    return new Response("Bad Request: unable to parse body", { status: 400 });
  }

  // Build a normalized lookup map
  const norm = {};
  for (const [k, v] of Object.entries(raw)) {
    norm[normKey(k)] = String(v ?? "").trim();
  }

  // Honeypot: any "website" field filled => pretend success, no email, redirect.
  const websiteTrap =
    norm.website || norm.web || norm.url || norm.yourwebsite || norm.companywebsite || "";
  if (websiteTrap) {
    return Response.redirect("/thanks/", 303);
  }

  // Accept multiple possible field names from your form
  const pick = (...keys) => {
    for (const k of keys) {
      const v = norm[normKey(k)];
      if (v) return v;
    }
    return "";
  };

  const name = pick("name", "fullname", "yourname");
  const email = pick("email", "emailaddress");
  const phone = pick("phone", "phonenumber", "mobile", "cell");
  const city  = pick("city", "town");
  const address = pick("address", "streetaddress");
  const notes = pick("message", "notes", "details", "projectdetails");

  // Minimum viable lead: name + (email or phone)
  if (!name || (!email && !phone)) {
    return new Response("Missing required fields.", {
      status: 400,
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  }

  // Compose email text: include EVERYTHING submitted (except honeypot)
  const lines = [];
  const sortedKeys = Object.keys(raw).sort((a, b) => a.localeCompare(b));
  for (const k of sortedKeys) {
    const nk = normKey(k);
    if (nk === "website" || nk === "url" || nk === "yourwebsite" || nk === "companywebsite") continue;
    const v = String(raw[k] ?? "").trim();
    if (!v) continue;
    lines.push(`${k}: ${v}`);
  }

  // Fall back if the above somehow ends up empty
  if (lines.length === 0) {
    lines.push(`Name: ${name}`);
    if (email) lines.push(`Email: ${email}`);
    if (phone) lines.push(`Phone: ${phone}`);
    if (city) lines.push(`City: ${city}`);
    if (address) lines.push(`Address: ${address}`);
    if (notes) lines.push(`Notes: ${notes}`);
  }

  const subject = `New IGG Lead: ${name}${city ? ` (${city})` : ""}`;

  // Env sanity
  const apiKey = (env.RESEND_API_KEY || "").trim();
  const from = (env.LEAD_FROM || "").trim();
  const to = (env.LEAD_TO || "").trim();

  if (!apiKey || !from || !to) {
    return new Response(
      `Server not configured. Missing env vars:\n` +
      `RESEND_API_KEY=${apiKey ? "set" : "MISSING"}\n` +
      `LEAD_FROM=${from ? "set" : "MISSING"}\n` +
      `LEAD_TO=${to ? "set" : "MISSING"}\n`,
      { status: 500, headers: { "Content-Type": "text/plain; charset=utf-8" } }
    );
  }

  // Send email via Resend
  let resendResp;
  let resendText = "";
  try {
    resendResp = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from,
        to: [to],
        subject,
        text: lines.join("\n"),
        reply_to: email || undefined,
      }),
    });

    resendText = await resendResp.text();
  } catch (e) {
    return new Response(`Resend request failed: ${String(e)}`, {
      status: 502,
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  }

  if (!resendResp.ok) {
    return new Response(
      `Resend error (${resendResp.status} ${resendResp.statusText}):\n${resendText}`,
      { status: 502, headers: { "Content-Type": "text/plain; charset=utf-8" } }
    );
  }

  // Success -> redirect to static thank-you page
  return Response.redirect("/thanks/", 303);
}