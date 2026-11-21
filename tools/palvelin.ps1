# tools/palvelin.ps1 – pelin paikallinen testipalvelin ilman Pythonia (Windowsin oma PowerShell riittää).
# Käynnistys: tuplaklikkaa repon juuressa olevaa tiedostoa pelaa_paikallisesti.cmd
# Avaa pelin osoitteeseen http://localhost:8000/ ja palvelee repon tiedostot. Lopetus: sulje ikkuna.
param([int]$Port = 8000)

$root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path.TrimEnd('\', '/')
$mime = @{
  '.html' = 'text/html; charset=utf-8'; '.htm' = 'text/html; charset=utf-8'
  '.js' = 'text/javascript; charset=utf-8'; '.mjs' = 'text/javascript; charset=utf-8'
  '.css' = 'text/css; charset=utf-8'; '.json' = 'application/json; charset=utf-8'
  '.txt' = 'text/plain; charset=utf-8'; '.md' = 'text/plain; charset=utf-8'; '.csv' = 'text/plain; charset=utf-8'
  '.jpg' = 'image/jpeg'; '.jpeg' = 'image/jpeg'; '.png' = 'image/png'; '.webp' = 'image/webp'; '.svg' = 'image/svg+xml'; '.ico' = 'image/x-icon'
  '.mp4' = 'video/mp4'; '.webm' = 'video/webm'
  '.mp3' = 'audio/mpeg'; '.ogg' = 'audio/ogg'; '.wav' = 'audio/wav'; '.m4a' = 'audio/mp4'
  '.glb' = 'model/gltf-binary'; '.gltf' = 'model/gltf+json'; '.bin' = 'application/octet-stream'; '.wasm' = 'application/wasm'
}

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$Port/")
try { $listener.Start() } catch {
  Write-Host "Porttia $Port ei saatu käyttöön (onko palvelin jo auki toisessa ikkunassa?)." -ForegroundColor Red
  Write-Host $_.Exception.Message
  exit 1
}

Write-Host ""
Write-Host "  Porin kopterilento pyörii osoitteessa  http://localhost:$Port/" -ForegroundColor Green
Write-Host "  Kansio: $root"
Write-Host "  Lopeta sulkemalla tämä ikkuna."
Write-Host ""
try { Start-Process "http://localhost:$Port/" } catch { }

while ($listener.IsListening) {
  try { $ctx = $listener.GetContext() } catch { break }
  $req = $ctx.Request
  $res = $ctx.Response
  try {
    $rel = [Uri]::UnescapeDataString($req.Url.AbsolutePath).TrimStart('/')
    if ($rel -eq '' -or $rel.EndsWith('/')) { $rel = $rel + 'index.html' }
    $full = [IO.Path]::GetFullPath([IO.Path]::Combine($root, $rel))
    $inside = $full.StartsWith($root + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)
    if (-not $inside -or -not [IO.File]::Exists($full)) {
      $res.StatusCode = 404
      Write-Host "404  /$rel" -ForegroundColor DarkYellow
    } else {
      $ext = [IO.Path]::GetExtension($full).ToLowerInvariant()
      $type = $mime[$ext]
      if (-not $type) { $type = 'application/octet-stream' }
      $res.ContentType = $type
      $res.Headers.Add('Cache-Control', 'no-store')
      $fs = [IO.File]::OpenRead($full)
      try {
        $res.ContentLength64 = $fs.Length
        if ($req.HttpMethod -ne 'HEAD') { $fs.CopyTo($res.OutputStream) }
      } finally { $fs.Close() }
    }
  } catch {
    # selain katkaisi latauksen tms. – jatketaan
  } finally {
    try { $res.Close() } catch { }
  }
}
