export async function onRequestPost(context) {
  try {
    const req = context.request;
    const env = context.env;

    // ---- Required env vars ----
    const RESEND_API_KEY = env.RESEND_API_KEY;
    const LEAD_TO = env.LEAD_TO;
    const LEAD_FROM = env.LEAD_FROM;

    if (!RESEND_API_KEY || !LEAD_TO || !LEAD_FROM) {
      return new Response(
        "Server not configured (missing RESEND_API_KEY / LEAD_TO / LEAD_FROM).",
        { status: 500, headers: { "Content-Type": "text/plain; charset=utf-8" } }
      );
    }

    // ---- Parse input (supports normal <form> POST, multipart, urlencoded, or JSON) ----
    const ct = (req.headers.get("content-type") || "").toLowerCase();
    const data = {};

    if (ct.includes("application/json")) {
      const j = await req.json().catch(() => ({}));
      for (const k of Object.keys(j || {})) data[k] = String(j[k] ?? "").trim();
    } else {
      // formData handles multipart + urlencoded
      const fd = await req.formData();
      for (const [k, v] of fd.entries()) data[k] = String(v ?? "").trim();
    }

    // ---- Honeypot ----
    if ((data.website || "").length > 0) {
      return new Response("", { status: 204 });
    }

    const name = (data.name || data.fullname || data.full_name || "").trim();
    const email = (data.email || "").trim();
    const phone = (data.phone || data.tel || data.telephone || "").trim();
    const city = (data.city || "").trim();
    const message = (data.message || data.notes || "").trim();

    if (!name || (!phone && !email)) {
      return new Response("Missing required fields.", {
        status: 400,
        headers: { "Content-Type": "text/plain; charset=utf-8" }
      });
    }

    const subject = `New IGG Lead${city ? " - " + city : ""}: ${name}`;

    const lines = [
      `Name: ${name}`,
      email ? `Email: ${email}` : null,
      phone ? `Phone: ${phone}` : null,
      city ? `City: ${city}` : null,
      message ? `Message: ${message}` : null,
      `Page: ${req.headers.get("referer") || "(no referer)"}`,
      `IP: ${req.headers.get("cf-connecting-ip") || ""}`,
      `UA: ${req.headers.get("user-agent") || ""}`
    ].filter(Boolean);

    const textBody = lines.join("\n");

    // ---- Send via Resend ----
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
        text: textBody,
        reply_to: email || undefined
      })
    });

    if (!r.ok) {
      const err = await r.text().catch(() => "");
      return new Response(`Email send failed: ${r.status} ${err}`, {
        status: 502,
        headers: { "Content-Type": "text/plain; charset=utf-8" }
      });
    }

    // ---- Browser form submit: redirect to thank-you ----
    const url = new URL(req.url);
    const accept = (req.headers.get("accept") || "").toLowerCase();
    const wantsHtml = accept.includes("text/html") || accept.includes("*/*");

    if (wantsHtml) {
      return Response.redirect(url.origin + "/thank-you/", 303);
    }

    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { "Content-Type": "application/json; charset=utf-8" }
    });

  } catch (e) {
    return new Response(`Server error: ${e && e.message ? e.message : String(e)}`, {
      status: 500,
      headers: { "Content-Type": "text/plain; charset=utf-8" }
    });
  }
}

// Optional: helpful for quick sanity checks in a browser
export async function onRequestGet() {
  return new Response("OK (GET) - /api/lead is deployed", {
    status: 200,
    headers: { "Content-Type": "text/plain; charset=utf-8" }
  });
}