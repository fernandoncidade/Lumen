Get-Content requirements.txt | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith('#')) {
        $line = $line -split '\s+#' | Select-Object -First 1
        $name = ($line -split '[\s=@<>#]')[0]
        if ($name) {
            Write-Host ">> $name"
            pip index versions $name 2>$null
        }
    }
}
