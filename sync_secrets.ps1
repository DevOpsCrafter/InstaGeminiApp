$envFile = "secrets.env"

if (-not (Test-Path $envFile)) {
    Write-Host "❌ Error: '$envFile' not found."
    Write-Host "Please rename 'secrets.env.template' to 'secrets.env' and add your keys."
    exit 1
}

Write-Host "🚀 Reading secrets from $envFile..."
$content = Get-Content $envFile
foreach ($line in $content) {
    if ($line -match "^\s*#") { continue } # Skip comments
    if ($line -match "^\s*$") { continue } # Skip empty lines
    
    $parts = $line -split "=", 2
    if ($parts.Count -eq 2) {
        $key = $parts[0].Trim()
        $value = $parts[1].Trim()
        
        Write-Host "   📤 Uploading $key..."
        # Use GH CLI to set secret
        echo $value | gh secret set $key
    }
}

Write-Host "✅ All secrets uploaded to GitHub Actions!"
Write-Host "You can now run the 'Daily Astroboli Post' workflow."
