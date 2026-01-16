/* functions/api/lead.js
   Cloudflare Pages Function: /api/lead
   - Accepts form-encoded, multipart, or JSON submissions
   - Sends lead email via Resend
   - Redirects browser submissions to /thanks/ (303)
   - Returns JSON for API callers (Accept: application/json)
   - Never throws uncaught exceptions (prevents CF 1101)
*/

function pickFirst(obj, keys) {
  for (const k of keys) {
    const v = obj[k];
    if (typeof v === "string" && v.trim() !== "") return v.trim();
  }
  return "";
}

function looksLikeJsonAccept(request) {
  const accept = request.headers.get("accept") || "";
  return accept.toLowerCase().includes("application/json");
}

function contentType(request) {
  return (request.headers.get("content-type") || "").toLowerCase();
}

function toPlainObjectFromFormData(fd) {
  const out = {};
  for (const [k, v] of fd.entries()) {
    out[k] = typeof v === "string" ? v : "[file]";
  }
  return out;
}

function normalizeLeadFields(data) {
  const name = pickFirst(data, ["name", "Name", "full_name", "FullName"]);
  const email = pickFirst(data, ["email", "Email"]);
  const phone = pickFirst(data, ["phone", "Phone", "tel", "Tel", "telephone", "Telephone"]);
  const city = pickFirst(data, ["city", "City", "town", "Town"]);
  const message = pickFirst(data, ["message", "Message", "notes", "Notes", "note", "Note"]);

  const website = pickFirst(data, ["website", "Website", "url", "URL"]);

  const extras = {};
  for (const [k, v] of Object.entries(data)) {
    const key = String(k);
    if (["website", "Website"].includes(key)) continue;
    if (["name","Name","email","Email","phone","Phone","tel","Tel","telephone","Telephone","city","City","message","Message","notes","Notes"].includes(key)) continue;
    if (typeof v === "string" && v.trim() !== "") extras[key] = v.trim();
  }

  return { name, email, phone, city, message, website, extras };
}

function buildEmailText(lead) {
  const lines = [];
  lines.push(`Name: ${lead.name || "-"}`);
  lines.push(`Email: ${lead.email || "-"}`);
  lines.push(`Phone: ${lead.phone || "-"}`);
  if (lead.city) lines.push(`City: ${lead.city}`);
  if (lead.message) lines.push(`Notes: ${lead.message}`);

  const extraKeys = Object.keys(lead.extras || {});
  if (extraKeys.length) {
    lines.push("");
    lines.push("Extra fields:");
    for (const k of extraKeys.sort()) lines.push(`${k}: ${lead.extras[k]}`);
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
  if (lead.email) payload.reply_to = lead.email;

  const resp = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  const bodyText = await resp.text().catch(() => "");
  if (!resp.ok) {
    return { ok: false, status: 502, error: `Resend error (${resp.status}): ${bodyText || "(empty response)"}` };
  }
  return { ok: true, status: 200, data: bodyText };
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
  return new Response(null, { status: 303, headers: { Location: location } });
}

export async function onRequest(context) {
  const request = context.request;
  const env = context.env;

  if (request.method === "GET" || request.method === "HEAD") {
    return text(405, "Method Not Allowed. POST a lead to /api/lead.");
  }
  if (request.method !== "POST") {
    return text(405, "Method Not Allowed.");
  }

  const wantsJson = looksLikeJsonAccept(request);

  try {
    const ct = contentType(request);
    let data = {};

    if (ct.includes("application/json")) {
      data = await request.json();
    } else if (ct.includes("application/x-www-form-urlencoded") || ct.includes("multipart/form-data")) {
      const fd = await request.formData();
      data = toPlainObjectFromFormData(fd);
    } else {
      try {
        const fd = await request.formData();
        data = toPlainObjectFromFormData(fd);
      } catch (e) {
        return wantsJson ? json(400, { ok: false, error: "Unsupported Content-Type" }) : text(400, "Unsupported Content-Type");
      }
    }

    const lead = normalizeLeadFields(data);

    if (lead.website) {
      console.log("Honeypot hit, dropping lead.");
      return wantsJson ? json(200, { ok: true }) : redirect303("/thanks/");
    }

    if (!lead.name || (!lead.email && !lead.phone)) {
      const err = "Missing required fields: name and (email or phone).";
      return wantsJson ? json(400, { ok: false, error: err }) : text(400, err);
    }

    const emailText = buildEmailText(lead);

    console.log("Lead received:", {
      name: lead.name,
      email: lead.email || null,
      phone: lead.phone || null,
      city: lead.city || null,
      extrasCount: Object.keys(lead.extras || {}).length,
    });

    const sent = await sendResendEmail({ env, lead, text: emailText });

    if (!sent.ok) {
      console.error("Resend failed:", sent.error);
      return wantsJson ? json(sent.status, { ok: false, error: sent.error }) : text(sent.status, sent.error);
    }

    return wantsJson ? json(200, { ok: true }) : redirect303("/thanks/");
  } catch (err) {
    const msg = err && err.message ? err.message : String(err);
    console.error("Unhandled error in /api/lead:", msg, err);
    return wantsJson
      ? json(500, { ok: false, error: "Internal error", detail: msg })
      : text(500, `Internal error: ${msg}`);
  }
}