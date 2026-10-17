# Maximize a process's main window and bring it to the front (for screen recording).
#   win-front.ps1 -Name lightcraft [-Restore]
param([string]$Name, [switch]$Restore)
Add-Type @'
using System; using System.Runtime.InteropServices;
public static class W {
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern void keybd_event(byte k, byte s, uint f, UIntPtr e);
}
'@
$p = Get-Process -Name $Name -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
if (-not $p) { Write-Error "no window for $Name"; exit 1 }
$h = $p.MainWindowHandle
[W]::ShowWindow($h, $(if ($Restore) { 9 } else { 3 })) | Out-Null
# Alt tap lets SetForegroundWindow work from a background process
[W]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero); [W]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
[W]::SetForegroundWindow($h) | Out-Null
"front: $Name ($($p.MainWindowTitle))"
