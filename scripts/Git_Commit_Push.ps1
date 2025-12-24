# Git_Commit_Push.ps1
param(
  [string]$Message = "WIP"
)
Set-Location "C:\SPA-Project"
git add .
git commit -m $Message
git push