if ($PSVersionTable.PSVersion.Major -lt 7)
{
    Write-Host "Running on an old PowerShell version and thus exiting now"
    exit
}
Write-Host "Still Running"
