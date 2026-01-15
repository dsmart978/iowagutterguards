export async function onRequestPost(context) {
  const { request, env } = context;

  // ---- Config (set these in Cloudflare Pages -> Settings -> Environment variables) ----
  const RESEND_API_KEY = env.RESEND_API_KEY;
  const RESEND_FROM    = env.RESEND_FROM;  // e.g. "Iowa Gutter Guards <leads@iowagutterguards.online>"
  const LEAD_TO        = env.LEAD_TO;      // e.g. "you@yourdomain.com"

  if (!RESEND_API_KEY || !RESEND_FROM || !LEAD_TO) {
    return new Response("Server misconfigured: missing RESEND_API_KEY / RESEND_FROM / LEAD_TO", { status: 500 });
  }

  // ---- Only accept form posts ----
  const ct = request.headers.get("content-type") || "";
  let data = {};
  try {
    if (ct.includes("application/x-www-form-urlencoded") || ct.includes("multipart/form-data")) {
      const fd = await request.formData();
      for (const [k, v] of fd.entries()) {
        // If multiple values, join them
        if (data[k] === undefined) data[k] = v;
        else data[k] = Array.isArray(data[k]) ? data[k].concat([v]) : [data[k], v];
      }
    } else if (ct.includes("application/json")) {
      data = await request.json();
    } else {
      // Try anyway
      const fd = await request.formData();
      for (const [k, v] of fd.entries()) data[k] = v;
    }
  } catch (e) {
    return new Response("Bad request: unable to parse form data", { status: 400 });
  }

  // ---- Basic spam trap (optional hidden field named "website") ----
  if (typeof data.website === "string" && data.website.trim() !== "") {
    // Quietly pretend success
    return Response.redirect(new URL("/thank-you/", request.url).toString(), 303);
  }

  // ---- Normalize likely field names ----
  const name  = (data.name || data.fullname || data.full_name || "").toString().trim();
  const email = (data.email || "").toString().trim();
  const phone = (data.phone || data.tel || data.telephone || "").toString().trim();
  const city  = (data.city || "").toString().trim();
  const msg   = (data.message || data.notes || data.details || "").toString().trim();

  // ---- Minimal validation ----
  if (!phone && !email) {
    return new Response("Please provide at least a phone number or email.", { status: 400 });
  }

  const referer = request.headers.get("Referer") || "";
  const ip = request.headers.get("CF-Connecting-IP") || "";
  const ua = request.headers.get("User-Agent") || "";

  const subject = [IGG Lead] ;

  const lines = [
    Name: ,
    Email: ,
    Phone: ,
    City: ,
    Message: ,
    "",
    Page: ,
    IP: ,
    UA: 
  ];

  const text = lines.join("\n");

  // ---- Send email via Resend REST API ----
  const resp = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Authorization": Bearer ,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      from: RESEND_FROM,
      to: [LEAD_TO],
      subject,
      text
    })
  });

  if (!resp.ok) {
    const body = await resp.text().catch(() => "");
    return new Response(Email send failed (). , { status: 502 });
  }

  return Response.redirect(new URL("/thank-you/", request.url).toString(), 303);
}