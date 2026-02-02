param(
  [string]$Domain = "https://iowagutterguards.online"
)

Set-StrictMode -Version Latest

function HtmlAttrEscape([string]$s) {
  if ($null -eq $s) { return "" }
  return ($s -replace '&','&amp;' -replace '"','&quot;' -replace '<','&lt;' -replace '>','&gt;')
}

function TitleCaseFromSlug([string]$slug) {
  if ([string]::IsNullOrWhiteSpace($slug)) { return "" }
  $parts = $slug -split '-'
  $tc = foreach ($p in $parts) {
    if ([string]::IsNullOrWhiteSpace($p)) { continue }
    ($p.Substring(0,1).ToUpperInvariant() + $p.Substring(1).ToLowerInvariant())
  }
  return ($tc -join ' ')
}

function Get-CanonicalUrl([string]$fullPath, [string]$root, [string]$domain) {
  $rel = [System.IO.Path]::GetRelativePath($root, $fullPath) -replace '\\','/'
  if ($rel -ieq "index.html") { return ($domain.TrimEnd('/') + "/") }
  if ($rel.ToLowerInvariant().EndsWith("/index.html")) {
    $base = $rel.Substring(0, $rel.Length - "index.html".Length)
    return ($domain.TrimEnd('/') + "/" + $base)
  }
  return ($domain.TrimEnd('/') + "/" + $rel)
}

function Pick-MetaDescription([string]$rel) {
  $relLower = $rel.ToLowerInvariant()

  if ($relLower -eq "index.html") {
    return "Premium micro-mesh gutter guard installation across Central Iowa. Stop clogs, reduce overflow, and protect your home. Get a quote from Iowa Gutter Guards."
  }

  if ($relLower -like "privacy-policy/*") {
    return "Read Iowa Gutter Guards’ privacy policy for how we collect, use, and protect your information when you request a quote or contact us."
  }
  if ($relLower -like "terms-of-service/*") {
    return "Review the Iowa Gutter Guards terms of service for quotes, scheduling, cancellations, and responsibilities related to gutter guard installation."
  }
  if ($relLower -like "warranty/*") {
    return "See what’s covered by the Iowa Gutter Guards warranty, what’s excluded, and how to request service for your gutter guard installation."
  }
  if ($relLower -like "customer-service/*") {
    return "Need help with a quote or installation? Contact Iowa Gutter Guards for scheduling, support, and answers about gutter guard installation in Central Iowa."
  }

  $m = [regex]::Match($relLower, '^service-areas/([^/]+)-ia/index\.html$')
  if ($m.Success) {
    $slug = $m.Groups[1].Value
    $city = TitleCaseFromSlug $slug
    return "Gutter guard installation in $city, Iowa. Premium micro-mesh guards to reduce clogs and overflow. Get a fast quote from Iowa Gutter Guards."
  }

  if ($relLower -like "thank-you/*" -or $relLower -like "thanks/*") {
    return "Thanks for reaching out to Iowa Gutter Guards. We received your request and will contact you shortly to confirm details."
  }

  return "Iowa Gutter Guards installs premium micro-mesh gutter guards across Central Iowa to reduce clogs, prevent overflow, and protect your home."
}

function Update-HeadOnly([string]$html, [string]$canonicalTag, [string]$metaTag) {
  $mHead = [regex]::Match($html, '(?is)<head\b[^>]*>.*?</head>')
  if (-not $mHead.Success) { return $html }

  $head = $mHead.Value

  # Canonical: replace or insert. Pattern is intentionally simple and head-only.
  $canonicalPattern = '(?is)<link\b[^>]*\brel\s*=\s*["'']canonical["''][^>]*>'
  if ([regex]::IsMatch($head, $canonicalPattern)) {
    $head = [regex]::Replace($head, $canonicalPattern, $canonicalTag, 1)
  } else {
    $head = $head -replace '(?is)</head>', ("  $canonicalTag`r`n</head>")
  }

  # Meta description: replace or insert.
  $metaPattern = '(?is)<meta\b[^>]*\bname\s*=\s*["'']description["''][^>]*>'
  if ([regex]::IsMatch($head, $metaPattern)) {
    $head = [regex]::Replace($head, $metaPattern, $metaTag, 1)
  } else {
    $head = $head -replace '(?is)</head>', ("  $metaTag`r`n</head>")
  }

  return ($html.Substring(0, $mHead.Index) + $head + $html.Substring($mHead.Index + $mHead.Length))
}

$root = (Get-Location).Path

$files = @()
$files += Get-ChildItem -LiteralPath $root -File -Filter *.html
$files += Get-ChildItem -LiteralPath $root -Recurse -File -Filter index.html

$skipDirs = @("\.git\", "\node_modules\", "\tools\", "\data\", "\functions\", "\assets\")
$files = $files | Where-Object {
  $p = $_.FullName
  if ($p -like "*\city-template.html") { return $false }
  foreach ($sd in $skipDirs) { if ($p -like "*$sd*") { return $false } }
  return $true
} | Sort-Object FullName -Unique

$changed = 0

foreach ($f in $files) {
  $html = Get-Content -LiteralPath $f.FullName -Raw

  $rel = [System.IO.Path]::GetRelativePath($root, $f.FullName) -replace '\\','/'
  $canonical = Get-CanonicalUrl -fullPath $f.FullName -root $root -domain $Domain

  $desc = Pick-MetaDescription -rel $rel
  $descEsc = HtmlAttrEscape $desc

  $canonicalTag = "<link rel=""canonical"" href=""$canonical"" />"
  $metaTag = "<meta name=""description"" content=""$descEsc"" />"

  $updated = Update-HeadOnly -html $html -canonicalTag $canonicalTag -metaTag $metaTag

  if ($updated -ne $html) {
    Set-Content -LiteralPath $f.FullName -Value $updated -Encoding UTF8 -NoNewline
    $changed++
  }
}

Write-Host ""
Write-Host "OK: Updated head tags (canonical + meta description) in $changed file(s) without regex timeouts."