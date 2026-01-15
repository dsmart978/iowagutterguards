export async function onRequest(context) {
  const req = context.request;
  const url = new URL(req.url);

  // Only allow POST
  if (req.method !== "POST") {
    return new Response("Method Not Allowed", { status: 405, headers: { "Allow": "POST" } });
  }

  try {
    // ---- Parse form data ----
    const ct = (req.headers.get("content-type") || "").toLowerCase();
    let data = {};

    if (ct.includes("application/x-www-form-urlencoded") || ct.includes("multipart/form-data")) {
      const fd = await req.formData();
      for (const [k, v] of fd.entries()) data[k] = String(v ?? "").trim();
    } else if (ct.includes("application/json")) {
      data = await req.json();
      for (const k of Object.keys(data)) data[k] = String(data[k] ?? "").trim();
    } else {
      const fd = await req.formData();
      for (const [k, v] of fd.entries()) data[k] = String(v ?? "").trim();
    }

    // ---- Honeypot ----
    if ((data.website || "").length > 0) {
      return new Response("", { status: 204 });
    }

    const name  = (data.name || data.fullname || data.full_name || "").trim();
    const email = (data.email || "").trim();
    const phone = (data.phone || data.tel || data.telephone || "").trim();
    const city  = (data.city || "").trim();
    const message = (data.message || data.notes || "").trim();

    if (!name || (!phone && !email)) {
      return new Response("Missing required fields.", { status: 400 });
    }

    // ---- Env vars (Cloudflare Pages -> Settings -> Variables and Secrets) ----
    const RESEND_API_KEY = context.env.RESEND_API_KEY;
    const LEAD_TO = context.env.LEAD_TO;
    const LEAD_FROM = context.env.LEAD_FROM;

    if (!RESEND_API_KEY || !LEAD_TO || !LEAD_FROM) {
      return new Response("Server not configured (missing RESEND_API_KEY / LEAD_TO / LEAD_FROM).", { status: 500 });
    }

    const subject = `New IGG Lead${city ? " - " + city : ""}: ${name}`;

    const lines = [
      `Name: ${name}`,
      email ? `Email: ${email}` : null,
      phone ? `Phone: ${phone}` : null,
      city ? `City: ${city}` : null,
      message ? `Message: ${message}` : null,
      `Page: ${url.origin}${url.pathname}`,
      `IP: ${(req.headers.get("cf-connecting-ip") || "").trim()}`,
      `UA: ${(req.headers.get("user-agent") || "").trim()}`
    ].filter(Boolean);

    const textBody = lines.join("\n");
    const htmlBody = `<pre style="white-space:pre-wrap;font-family:ui-monospace,Menlo,Consolas,monospace">${escapeHtml(textBody)}</pre>`;

    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${RESEND_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        from: LEAD_FROM,
        to: [LEAD_TO],
        subject,
        html: htmlBody,
        reply_to: email || undefined
      })
    });

    if (!r.ok) {
      const err = await r.text().catch(() => "");
      return new Response(`Email send failed: ${r.status} ${err}`, { status: 502 });
    }

    // Redirect after successful submit
    return Response.redirect(url.origin + "/thank-you/", 303);

  } catch (e) {
    return new Response(`Server error: ${e && e.message ? e.message : String(e)}`, { status: 500 });
  }
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}