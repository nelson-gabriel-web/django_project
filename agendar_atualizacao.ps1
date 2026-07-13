# Script para agendar a atualização automática no Windows

$scriptPath = "C:\Users\administer\Desktop\meu_site\atualizar_taxas_auto.py"
$pythonPath = "python"

# Criar uma tarefa agendada
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptPath
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "AtualizarTaxasCambio" -Action $action -Trigger $trigger -Principal $principal -Settings $settings

Write-Host "Tarefa agendada criada! A atualização ocorrerá todos os dias às 8h."
Write-Host "Para ver a tarefa: Get-ScheduledTask -TaskName 'AtualizarTaxasCambio'"