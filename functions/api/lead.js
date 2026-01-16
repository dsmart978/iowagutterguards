export async function onRequest(context) {
  const { request, env } = context;

  // Only POST is supported (forms submit POST)
  if (request.method !== "POST") {
    return new Response("Method Not Allowed", {
      status: 405,
      headers: { "Allow": "POST", "content-type": "text/plain; charset=utf-8" },
    });
  }

  const wantsJson = looksLikeJsonAccept(request);

  try {
    // ---- Parse incoming body ----
    const ct = contentType(request);
    let data = {};

    if (ct.includes("application/json")) {
      data = await request.json();
      data = normalizeObjectStrings(data);
    } else {
      // Works for x-www-form-urlencoded and multipart/form-data
      const fd = await request.formData();
      data = toPlainObjectFromFormData(fd);
    }

    const lead = normalizeLeadFields(data);

    // Honeypot: bots fill it, humans don't
    if (lead.website) {
      console.log("Honeypot hit. Dropping.");
      return wantsJson
        ? json(200, { ok: true, dropped: "honeypot" })
        : redirect303("/thanks/");
    }

    // Validation: require name + (email OR phone)
    if (!lead.name || (!lead.email && !lead.phone)) {
      const err = "Missing required fields: name and (email or phone).";
      return wantsJson ? json(400, { ok: false, error: err }) : text(400, err);
    }

    // Build email body
    const emailText = buildEmailText(lead);

    console.log("Lead received:", {
      name: lead.name,
      email: lead.email || null,
      phone: lead.phone || null,
      city: lead.city || null,
      extrasCount: Object.keys(lead.extras || {}).length,
    });

    // Send email via Resend
    const sent = await sendResendEmail({ env, lead, text: emailText });

    if (!sent.ok) {
      console.error("Resend failed:", sent.error);
      return wantsJson
        ? json(sent.status, { ok: false, error: sent.error, detail: sent.detail || null })
        : text(sent.status, sent.error);
    }

    // Success
    return wantsJson
      ? json(200, { ok: true, resend: sent.data })
      : redirect303("/thanks/");

  } catch (err) {
    // No more mystery 1101 crashes without context
    const msg = err && typeof err.message === "string" ? err.message : String(err);
    console.error("Unhandled error in /api/lead:", msg);
    return wantsJson
      ? json(500, { ok: false, error: "Internal error", detail: msg })
      : text(500, "Internal error: " + msg);
  }
}

function looksLikeJsonAccept(request) {
  const accept = request.headers.get("accept") || "";
  return accept.toLowerCase().includes("application/json");
}

function contentType(request) {
  return (request.headers.get("content-type") || "").toLowerCase();
}

function normalizeObjectStrings(obj) {
  const out = {};
  for (const [k, v] of Object.entries(obj || {})) {
    out[k] = typeof v === "string" ? v.trim() : v;
  }
  return out;
}

function toPlainObjectFromFormData(fd) {
  const out = {};
  for (const [k, v] of fd.entries()) {
    out[k] = typeof v === "string" ? v.trim() : "[file]";
  }
  return out;
}

function pickFirst(obj, keys) {
  for (const k of keys) {
    const v = obj[k];
    if (typeof v === "string" && v.trim() !== "") return v.trim();
  }
  return "";
}

function normalizeLeadFields(data) {
  // Your site sends Title Case names (Name/Email/Phone/Notes/etc)
  const name = pickFirst(data, ["name", "Name", "full_name", "FullName", "Full Name"]);
  const email = pickFirst(data, ["email", "Email", "e-mail", "E-mail"]);
  const phone = pickFirst(data, ["phone", "Phone", "tel", "Tel", "telephone", "Telephone"]);
  const city = pickFirst(data, ["city", "City", "town", "Town"]);
  const message = pickFirst(data, ["message", "Message", "notes", "Notes", "note", "Note"]);

  // Honeypot
  const website = pickFirst(data, ["website", "Website", "url", "URL"]);

  // Everything else, preserved as extras (so you can see what the form actually sent)
  const extras = {};
  const ignore = new Set([
    "name","Name","full_name","FullName","Full Name",
    "email","Email","e-mail","E-mail",
    "phone","Phone","tel","Tel","telephone","Telephone",
    "city","City","town","Town",
    "message","Message","notes","Notes","note","Note",
    "website","Website","url","URL",
  ]);

  for (const [k, v] of Object.entries(data || {})) {
    const key = String(k);
    if (ignore.has(key)) continue;
    if (typeof v === "string" && v.trim() !== "") extras[key] = v.trim();
  }

  return { name, email, phone, city, message, website, extras };
}

function buildEmailText(lead) {
  const lines = [];
  lines.push(`Name: ${lead.name || "-"}`);
  if (lead.email) lines.push(`Email: ${lead.email}`);
  if (lead.phone) lines.push(`Phone: ${lead.phone}`);
  if (lead.city) lines.push(`City: ${lead.city}`);
  if (lead.message) lines.push(`Notes: ${lead.message}`);

  const extraKeys = Object.keys(lead.extras || {});
  if (extraKeys.length) {
    lines.push("");
    lines.push("Extra fields:");
    for (const k of extraKeys.sort()) {
      lines.push(`${k}: ${lead.extras[k]}`);
    }
  }
  return lines.join("\n");
}

async function sendResendEmail({ env, lead, text }) {
  const RESEND_API_KEY = env && env.RESEND_API_KEY;
  const LEAD_TO = env && env.LEAD_TO;
  const LEAD_FROM = env && env.LEAD_FROM;

  if (!RESEND_API_KEY) return { ok: false, status: 500, error: "Missing RESEND_API_KEY env var" };
  if (!LEAD_TO) return { ok: false, status: 500, error: "Missing LEAD_TO env var" };
  if (!LEAD_FROM) return { ok: false, status: 500, error: "Missing LEAD_FROM env var" };

  const subjectCity = lead.city ? ` (${lead.city})` : "";
  const payload = {
    from: LEAD_FROM,
    to: [LEAD_TO],
    subject: `New IGG Lead: ${lead.name || "New Lead"}${subjectCity}`,
    text,
  };

  // Reply-to should be the lead, if provided
  if (lead.email) payload.reply_to = lead.email;

  const resp = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const bodyText = await resp.text().catch(() => "");
  let bodyJson = null;
  try { bodyJson = bodyText ? JSON.parse(bodyText) : null; } catch {}

  if (!resp.ok) {
    return {
      ok: false,
      status: 502,
      error: `Resend error (${resp.status})`,
      detail: bodyText || "(empty response)",
    };
  }

  // Return parsed JSON if possible (usually includes id), else raw text
  return { ok: true, status: 200, data: bodyJson || bodyText || { ok: true } };
}

function json(status, obj) {
  return new Response(JSON.stringify(obj, null, 2), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

function text(status, body) {
  return new Response(body, {
    status,
    headers: {
      "content-type": "text/plain; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}

function redirect303(location) {
  return new Response(null, { status: 303, headers: { "Location": location } });
}