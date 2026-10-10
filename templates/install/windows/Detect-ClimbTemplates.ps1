# Intune detection script for the Climb templates Win32 app.
# Detected (exit 0 with output) when the installed version matches this package.
$Expected = '@VERSION@'  # filled in by _build/package_build.py
$Installed = (Get-ItemProperty -Path 'HKLM:\SOFTWARE\Climb\Templates' -Name 'Version' -ErrorAction SilentlyContinue).Version
$Marker = Join-Path $env:ProgramData 'Climb\Templates\Office'
if ($Installed -eq $Expected -and (Test-Path $Marker)) {
    Write-Output "Climb templates $Installed installed"
    exit 0
}
exit 1
