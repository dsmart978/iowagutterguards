export async function onRequest(context) {
  const { request, env } = context;

  // Only allow POST
  if (request.method !== "POST") {
    return new Response("Method Not Allowed", {
      status: 405,
      headers: { "Allow": "POST" },
    });
  }

  // Parse form data (supports x-www-form-urlencoded and multipart/form-data)
  const ct = request.headers.get("content-type") || "";
  let data = {};

  try {
    if (ct.includes("application/x-www-form-urlencoded") || ct.includes("multipart/form-data")) {
      const fd = await request.formData();
      for (const [k, v] of fd.entries()) data[k] = String(v);
    } else if (ct.includes("application/json")) {
      data = await request.json();
    } else {
      // Last-resort attempt
      const fd = await request.formData();
      for (const [k, v] of fd.entries()) data[k] = String(v);
    }
  } catch (e) {
    return new Response("Bad Request: could not parse form submission.", { status: 400 });
  }

  // Honeypot: if filled, pretend success (spam-bot)
  const honeypot = (data.website || "").trim();
  if (honeypot) {
    return Response.redirect(new URL("/thanks/", request.url).toString(), 303);
  }

  const name = (data.name || "").trim();
  const email = (data.email || "").trim();
  const phone = (data.phone || "").trim();
  const city = (data.city || "").trim();
  const message = (data.message || "").trim();

  // Basic required fields (tweak as you like)
  if (!name || (!phone && !email) || !message) {
    return new Response("Missing required fields.", { status: 400 });
  }

  // Pull env vars
  const apiKey = env.RESEND_API_KEY;
  const leadTo = (env.LEAD_TO || "").trim();
  const leadFromRaw = (env.LEAD_FROM || "").trim();

  // Validate env vars (DO NOT print secrets)
  const missing = [];
  if (!apiKey) missing.push("RESEND_API_KEY");
  if (!leadTo) missing.push("LEAD_TO");
  if (!leadFromRaw) missing.push("LEAD_FROM");

  if (missing.length) {
    return new Response(
      `Server misconfigured: missing ${missing.join(", ")}.`,
      { status: 500 }
    );
  }

  // Resend wants a proper From header. If you stored only an email, wrap it.
  const leadFrom = leadFromRaw.includes("<")
    ? leadFromRaw
    : `Iowa Gutter Guards <${leadFromRaw}>`;

  const subject = `New IGG Lead: ${name}${city ? " (" + city + ")" : ""}`;

  const lines = [
    `Name: ${name}`,
    `Email: ${email || "(none)"}`,
    `Phone: ${phone || "(none)"}`,
    `City: ${city || "(none)"}`,
    "",
    "Message:",
    message,
    "",
    "----",
    `Submitted: ${new Date().toISOString()}`,
    `IP: ${request.headers.get("cf-connecting-ip") || "(unknown)"}`,
    `UA: ${request.headers.get("user-agent") || "(unknown)"}`,
  ];

  const payload = {
    from: leadFrom,
    to: leadTo,
    subject,
    text: lines.join("\n"),
    reply_to: email || undefined,
  };

  // Send via Resend
  let resendResp, resendBodyText;
  try {
    resendResp = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    resendBodyText = await resendResp.text();
  } catch (e) {
    return new Response(`Resend request failed: ${String(e)}`, { status: 502 });
  }

  if (!resendResp.ok) {
    // This is the money shot: you will finally SEE why it failed.
    return new Response(
      `Resend error (${resendResp.status}): ${resendBodyText}`,
      { status: 502 }
    );
  }

  // Success: redirect to thanks page
  return Response.redirect(new URL("/thanks/", request.url).toString(), 303);
}