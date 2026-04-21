# MM-Skill v0.3.0 部署脚本
# 将开发目录的 skill 文件同步到 Claude Code 安装目录
# 使用方法：
#   首次安装：在项目根目录运行 .\deploy.ps1
#   更新：git pull 后再运行 .\deploy.ps1

# 检测来源：如果 .git 存在说明是从 repo 运行的
if (Test-Path "$PSScriptRoot\.git") {
    $src = "$PSScriptRoot\skills"
} else {
    $src = "E:\MM_agent\MM-Agent\math-modeling\skills"
}
$dst = "$env:USERPROFILE\.claude\skills"

Write-Host "=== MM-Skill v0.3.0 Deployment ===" -ForegroundColor Cyan
Write-Host "Source: $src" -ForegroundColor Gray
Write-Host "Target: $dst" -ForegroundColor Gray

# 1. Create new directories
Write-Host "`n[1/5] Creating new directories..." -ForegroundColor Yellow
$dirs = @(
    "$dst\mm-review",
    "$dst\mm-writing",
    "$dst\math-modeling\references\templates\cumcm",
    "$dst\math-modeling\references\templates\mcm",
    "$dst\math-modeling\references\templates\generic"
)
foreach ($d in $dirs) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
}
Write-Host "  Done." -ForegroundColor Green

# 2. Copy/update SKILL.md files
Write-Host "`n[2/5] Updating SKILL.md files..." -ForegroundColor Yellow
$skills = @(
    "math-modeling",
    "math-model-command",
    "mm-analysis",
    "mm-modeling",
    "mm-solving",
    "mm-review",
    "mm-writing"
)
foreach ($s in $skills) {
    Copy-Item "$src\$s\SKILL.md" "$dst\$s\SKILL.md" -Force
    Write-Host "  $s" -ForegroundColor White
}
Write-Host "  Done (7 files)." -ForegroundColor Green

# 3. Copy/update references
Write-Host "`n[3/5] Updating reference files..." -ForegroundColor Yellow
$refs = @(
    "abstract_guide.md",
    "actor_critic.md",
    "code_templates.md",
    "dag_scheduler.md",
    "hmml_index.md",
    "hmml_or.md",
    "hmml_optimization.md",
    "hmml_ml.md",
    "hmml_prediction.md",
    "hmml_evaluation.md"
)
foreach ($r in $refs) {
    Copy-Item "$src\math-modeling\references\$r" "$dst\math-modeling\references\$r" -Force
}
Write-Host "  Done (10 files)." -ForegroundColor Green

# 4. Copy LaTeX templates
Write-Host "`n[4/5] Installing LaTeX templates..." -ForegroundColor Yellow
Copy-Item "$src\math-modeling\references\templates\cumcm\main.tex" "$dst\math-modeling\references\templates\cumcm\main.tex" -Force
Copy-Item "$src\math-modeling\references\templates\mcm\main.tex" "$dst\math-modeling\references\templates\mcm\main.tex" -Force
Copy-Item "$src\math-modeling\references\templates\generic\main.tex" "$dst\math-modeling\references\templates\generic\main.tex" -Force
Write-Host "  Done (3 templates)." -ForegroundColor Green

# 5. Delete obsolete files
Write-Host "`n[5/5] Removing obsolete files..." -ForegroundColor Yellow
$obsolete = @(
    "$dst\math-modeling\references\hmml.md",
    "$dst\math-modeling\references\quality_gates.md"
)
foreach ($o in $obsolete) {
    if (Test-Path $o) {
        Remove-Item $o -Force
        Write-Host "  Removed $(Split-Path $o -Leaf)" -ForegroundColor Green
    }
}

# Summary
Write-Host "`n=== Deployment Complete ===" -ForegroundColor Cyan
Write-Host "`nInstalled skills:" -ForegroundColor White
Get-ChildItem "$dst" -Directory | ForEach-Object {
    $skillFile = Join-Path $_.FullName "SKILL.md"
    if (Test-Path $skillFile) {
        $ver = (Select-String -Path $skillFile -Pattern "version:" | Select-Object -First 1).Line.Trim()
        Write-Host "  $($_.Name) ($ver)" -ForegroundColor White
    }
}
