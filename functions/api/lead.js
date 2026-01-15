export async function onRequestPost(context) {
  try {
    const req = context.request;
    const url = new URL(req.url);

    // ---- Parse form data (works for both browser <form> POST and fetch) ----
    const ct = (req.headers.get("content-type") || "").toLowerCase();
    let data = {};
    if (ct.includes("application/x-www-form-urlencoded") || ct.includes("multipart/form-data")) {
      const fd = await req.formData();
      for (const [k, v] of fd.entries()) data[k] = String(v ?? "").trim();
    } else if (ct.includes("application/json")) {
      data = await req.json();
      for (const k of Object.keys(data)) data[k] = String(data[k] ?? "").trim();
    } else {
      // Last-resort: try formData anyway
      const fd = await req.formData();
      for (const [k, v] of fd.entries()) data[k] = String(v ?? "").trim();
    }

    // ---- Honeypot (spam bots fill it, humans don't) ----
    if ((data.website || "").length > 0) {
      return new Response("", { status: 204 });
    }

    const name  = (data.name || data.fullname || data.full_name || "").trim();
    const email = (data.email || "").trim();
    const phone = (data.phone || data.tel || data.telephone || "").trim();
    const city  = (data.city || "").trim();
    const message = (data.message || data.notes || "").trim();

    // Basic validation: require at least name + (phone or email)
    if (!name || (!phone && !email)) {
      return new Response("Missing required fields.", { status: 400 });
    }

    // ---- Env vars (set these in Cloudflare Pages > Settings > Variables and Secrets) ----
    const RESEND_API_KEY = context.env.RESEND_API_KEY;
    const LEAD_TO = context.env.LEAD_TO;
    const LEAD_FROM = context.env.LEAD_FROM;

    if (!RESEND_API_KEY || !LEAD_TO || !LEAD_FROM) {
      return new Response("Server not configured (missing RESEND_API_KEY / LEAD_TO / LEAD_FROM).", { status: 500 });
    }

    const subject = New IGG Lead: ;
    const lines = [
      Name: ,
      email ? Email:  : null,
      phone ? Phone:  : null,
      city ? City Page:  : null,
      message ? Message:  : null,
      Source: ,
      IP: ,
      UA: 
    ].filter(Boolean);

    const textBody = lines.join("\n");
    const htmlBody = <pre style="white-space:pre-wrap;font-family:ui-monospace,Menlo,Consolas,monospace"></pre>;

    // ---- Send via Resend ----
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": Bearer ,
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
      return new Response(Email send failed:  , { status: 502 });
    }

    // ---- Return redirect for normal form posts ----
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
    return new Response(Server error: , { status: 500 });
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