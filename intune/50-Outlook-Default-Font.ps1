<#
.SYNOPSIS
    Sets the brand font as the default for new emails in Outlook on the web and the new Outlook.

.DESCRIPTION
    Outlook on the web and the new Outlook (Windows, and Mac where it follows the mailbox
    settings) take the compose font from each mailbox, not from the device, so Intune cannot set
    it. This script uses Exchange Online PowerShell to set, for every user mailbox (or the ones
    you name):

      - DefaultFontName  Open Sans (the brand body font)
      - DefaultFontSize  2 (10pt; Outlook on the web sizes run 1 to 7, 3 = 12pt)
      - DefaultFontColor #4A5878 (Slate, the brand body text colour on white)

    People can still change their own font afterwards; re-running the script sets it back.
    Re-run it after adding people, or schedule it. Recipients without Open Sans see Arial.

    Needs the ExchangeOnlineManagement module (installed for your user if missing) and an
    account with the Exchange Administrator role.

.PARAMETER Identity
    Only these mailboxes (UPN or address), for a pilot. Default: every user mailbox.
.PARAMETER FontName
    Default Open Sans.
.PARAMETER FontSize
    1 to 7. Default 2.
.PARAMETER FontColor
    #RRGGBB. Default #4A5878. Pass #000000 for plain black.

.EXAMPLE
    pwsh ./50-Outlook-Default-Font.ps1 -Identity you@climb-uk.com -WhatIf
.EXAMPLE
    pwsh ./50-Outlook-Default-Font.ps1
#>
[CmdletBinding(SupportsShouldProcess)]
param(
    [string[]]$Identity,
    [string]$FontName = 'Open Sans',
    [ValidateRange(1, 7)][int]$FontSize = 2,
    [ValidatePattern('^#[0-9A-Fa-f]{6}$')][string]$FontColor = '#4A5878',
    [string]$Organization,
    [switch]$UseDeviceCode
)

$ErrorActionPreference = 'Stop'
function Write-ClimbStep([string]$Message) { Write-Host "==> $Message" -ForegroundColor Cyan }

if (-not (Get-Module -ListAvailable -Name ExchangeOnlineManagement)) {
    Write-ClimbStep 'Installing ExchangeOnlineManagement for this user'
    Install-Module ExchangeOnlineManagement -Scope CurrentUser -Repository PSGallery -Force
}
Import-Module ExchangeOnlineManagement
$connect = @{ ShowBanner = $false }
if ($Organization) { $connect.Organization = $Organization }
if ($UseDeviceCode) { $connect.Device = $true }
Connect-ExchangeOnline @connect

$mailboxes = if ($Identity) { $Identity | ForEach-Object { Get-EXOMailbox -Identity $_ } }
             else { Get-EXOMailbox -RecipientTypeDetails UserMailbox -ResultSize Unlimited }
Write-ClimbStep "$(@($mailboxes).Count) mailbox(es): $FontName, size $FontSize, $FontColor"

$changed = 0; $same = 0; $failed = 0
foreach ($m in $mailboxes) {
    $now = Get-MailboxMessageConfiguration -Identity $m.UserPrincipalName
    if ($now.DefaultFontName -eq $FontName -and $now.DefaultFontSize -eq $FontSize -and $now.DefaultFontColor -eq $FontColor) {
        $same++; continue
    }
    $was = "$($now.DefaultFontName) $($now.DefaultFontSize) $($now.DefaultFontColor)"
    if ($PSCmdlet.ShouldProcess($m.UserPrincipalName, "Set compose font (was $was)")) {
        try {
            Set-MailboxMessageConfiguration -Identity $m.UserPrincipalName -DefaultFontName $FontName -DefaultFontSize $FontSize -DefaultFontColor $FontColor
            Write-Host "  $($m.UserPrincipalName): set (was $was)"
            $changed++
        }
        catch { Write-Warning "$($m.UserPrincipalName): $($_.Exception.Message)"; $failed++ }
    }
}

Disconnect-ExchangeOnline -Confirm:$false | Out-Null
Write-ClimbStep "Changed $changed, already set $same, failed $failed$(if ($WhatIfPreference) { ' (dry run: nothing was changed)' })."
if ($failed) { exit 1 }
