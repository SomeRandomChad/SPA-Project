Get-NetTCPConnection -LocalPort 3000 -State Listen | Select-Object -Property LocalAddress,LocalPort,OwningProcess

Get-Process -Id (Get-NetTCPConnection -LocalPort 3000 -State Listen).OwningProcess