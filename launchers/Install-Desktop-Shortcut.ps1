$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$launcherVbs = Join-Path $PSScriptRoot "Launch-SDS.vbs"
$iconPath = Join-Path $projectRoot "assets\sds.ico"
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "SD Solutions.lnk"

if (-not (Test-Path (Split-Path $iconPath))) {
    New-Item -ItemType Directory -Path (Split-Path $iconPath) -Force | Out-Null
}

if (-not (Test-Path $iconPath)) {
    Add-Type -AssemblyName System.Drawing
    $size = 256
    $bitmap = New-Object System.Drawing.Bitmap $size, $size
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.Clear([System.Drawing.Color]::FromArgb(15, 36, 71))

    $rect = New-Object System.Drawing.Rectangle 24, 24, 208, 208
    $brush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
        $rect,
        [System.Drawing.Color]::FromArgb(56, 132, 255),
        [System.Drawing.Color]::FromArgb(15, 36, 71),
        45
    )
    $graphics.FillEllipse($brush, $rect)

    $font = New-Object System.Drawing.Font("Segoe UI", 64, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
    $textBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::White)
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    $graphics.DrawString("SDS", $font, $textBrush, (New-Object System.Drawing.RectangleF 0, 0, $size, $size), $format)

    $iconHandle = $bitmap.GetHicon()
    $icon = [System.Drawing.Icon]::FromHandle($iconHandle)
    $stream = New-Object System.IO.FileStream($iconPath, [System.IO.FileMode]::Create)
    $icon.Save($stream)
    $stream.Close()
    $graphics.Dispose()
    $bitmap.Dispose()
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $launcherVbs
$shortcut.WorkingDirectory = $projectRoot
$shortcut.WindowStyle = 1
$shortcut.Description = "Launch SD Solutions (SDS) evidence analysis"
$shortcut.IconLocation = "$iconPath,0"
$shortcut.Save()

Write-Host "Desktop shortcut created:"
Write-Host $shortcutPath
