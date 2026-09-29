# 本地 Git 工作流 - historical_multi_agent_sim
#
# 推荐位置：
#   script_tools/run_git_workflow.ps1
#   script_tools/run_git_workflow.bat
#
# 分支约定：
#   develop = 日常开发分支
#   main    = 本地稳定分支
#
# 当前版本只管理“本地 Git”：
#   - 不连接 GitHub
#   - 不 fetch / pull / push
#   - 不创建 release/* / hotfix/*
#
# 主要流程：
#   1) 查看状态
#   2) 在本地保存进度（add + commit）
#   3) 切换到 develop
#   4) 将 develop 快进合并到 main，然后返回 develop
#
# 5-7 预留给未来 Release / Hotfix 流程，目前不启用。

$ErrorActionPreference = "Stop"

function Run-Git {
    & git @args
    if ($LASTEXITCODE -ne 0) {
        throw "Git 命令执行失败：git $($args -join ' ')"
    }
}

function Pause-Menu {
    Write-Host ""
    Read-Host "按 Enter 返回菜单"
}

function Get-RepoRoot {
    $root = (& git rev-parse --show-toplevel 2>$null)
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($root -join "`n"))) {
        throw "当前目录不在 Git 仓库中。请把脚本放到项目根目录的 script_tools 目录后再运行。"
    }
    return (($root -join "`n").Trim())
}

function Get-CurrentBranch {
    $branch = (& git branch --show-current).Trim()
    if ([string]::IsNullOrWhiteSpace($branch)) {
        return "(detached HEAD)"
    }
    return $branch
}

function Test-LocalBranch {
    param([Parameter(Mandatory = $true)][string]$Branch)

    & git show-ref --verify --quiet "refs/heads/$Branch"
    return $LASTEXITCODE -eq 0
}

function Require-LocalBranch {
    param([Parameter(Mandatory = $true)][string]$Branch)

    if (-not (Test-LocalBranch $Branch)) {
        throw "缺少本地分支：$Branch"
    }
}

function Test-Tag {
    param([Parameter(Mandatory = $true)][string]$Tag)

    & git show-ref --verify --quiet "refs/tags/$Tag"
    return $LASTEXITCODE -eq 0
}

function Has-Changes {
    $status = & git status --porcelain
    return -not [string]::IsNullOrWhiteSpace(($status -join "`n"))
}

function Has-StagedChanges {
    & git diff --cached --quiet
    return $LASTEXITCODE -ne 0
}

function Require-CleanTree {
    if (Has-Changes) {
        Write-Host ""
        Write-Host "当前存在未提交修改，操作已取消。" -ForegroundColor Yellow
        Write-Host "请先用菜单 2 提交，或用菜单 10 Stash。" -ForegroundColor Yellow
        Write-Host ""
        & git status -sb
        return $false
    }
    return $true
}

function Get-VersionTags {
    $tags = & git tag
    $result = @()

    foreach ($tag in $tags) {
        if ($tag -match '^v?(\d+)\.(\d+)\.(\d+)$') {
            $version = [Version]"$($Matches[1]).$($Matches[2]).$($Matches[3])"
            $result += [PSCustomObject]@{
                Tag = $tag
                Version = $version
            }
        }
    }

    return $result | Sort-Object Version -Descending
}

function Get-LatestVersionInfo {
    $tags = @(Get-VersionTags)
    if ($tags.Count -eq 0) { return $null }
    return $tags[0]
}

function Get-CommitCount {
    param([Parameter(Mandatory = $true)][string]$Range)

    $value = (& git rev-list --count $Range 2>$null)
    if ($LASTEXITCODE -ne 0) { return 0 }
    return [int](($value -join "").Trim())
}

function Show-Status {
    Write-Host ""
    Write-Host "========== 本地 Git 状态 ==========" -ForegroundColor Cyan
    Write-Host "仓库：$repoRoot"
    Write-Host "当前分支：$(Get-CurrentBranch)"

    $latest = Get-LatestVersionInfo
    if ($latest) {
        Write-Host "最新本地 Tag：$($latest.Tag)" -ForegroundColor Green
    }
    else {
        Write-Host "最新本地 Tag：无"
    }

    Write-Host ""
    & git status -sb

    Write-Host ""
    Write-Host "本地分支：" -ForegroundColor Cyan
    & git branch -vv

    if ((Test-LocalBranch "main") -and (Test-LocalBranch "develop")) {
        $developAhead = Get-CommitCount "main..develop"
        $mainAhead = Get-CommitCount "develop..main"

        Write-Host ""
        Write-Host "main / develop 差异：" -ForegroundColor Cyan
        Write-Host "  develop 比 main 多：$developAhead 个提交"
        Write-Host "  main 比 develop 多：$mainAhead 个提交"
    }

    Write-Host ""
    Write-Host "最近提交：" -ForegroundColor Cyan
    & git log --oneline --decorate --graph -12
}

function Save-Progress {
    $current = Get-CurrentBranch

    if ($current -eq "(detached HEAD)") {
        Write-Host "当前处于 detached HEAD，不能直接保存开发进度。" -ForegroundColor Yellow
        Write-Host "请先切回 develop 或其他本地分支。"
        return
    }

    if ($current -eq "main") {
        Write-Host "main 是本地稳定分支，不允许通过菜单 2 直接提交。" -ForegroundColor Yellow
        Write-Host "日常开发请使用 develop；稳定后再用菜单 4 合并到 main。"
        return
    }

    if (-not (Has-Changes)) {
        Write-Host "当前没有需要提交的修改。" -ForegroundColor Yellow
        return
    }

    Write-Host ""
    & git status
    Write-Host ""

    $message = Read-Host "请输入 Commit 说明"
    if ([string]::IsNullOrWhiteSpace($message)) {
        Write-Host "Commit 说明不能为空。" -ForegroundColor Red
        return
    }

    Run-Git add .

    if (-not (Has-StagedChanges)) {
        Write-Host "没有可提交的已暂存修改（可能都被 .gitignore 忽略）。" -ForegroundColor Yellow
        return
    }

    Run-Git commit -m $message

    Write-Host ""
    Write-Host "✓ 已保存到本地 Git：$current" -ForegroundColor Green
}

function Switch-Develop {
    if (-not (Require-CleanTree)) { return }

    if (-not (Test-LocalBranch "develop")) {
        Require-LocalBranch "main"
        Write-Host "本地还没有 develop，将从 main 创建 develop。" -ForegroundColor Yellow
        Run-Git switch main
        Run-Git switch -c develop
        Write-Host ""
        Write-Host "✓ 已创建并切换到 develop。" -ForegroundColor Green
        return
    }

    Run-Git switch develop
    Write-Host ""
    Write-Host "✓ 已切换到 develop。" -ForegroundColor Green
}

function Merge-DevelopIntoMain {
    if (-not (Require-CleanTree)) { return }

    Require-LocalBranch "develop"
    Require-LocalBranch "main"

    $developAhead = Get-CommitCount "main..develop"
    $mainAhead = Get-CommitCount "develop..main"

    Write-Host ""
    Write-Host "========== 合并 develop -> main ==========" -ForegroundColor Cyan
    Write-Host "develop 比 main 多：$developAhead 个提交"
    Write-Host "main 比 develop 多：$mainAhead 个提交"

    if ($mainAhead -gt 0) {
        Write-Host ""
        Write-Host "main 存在 develop 没有的提交。为了避免自动产生复杂合并，本次操作已停止。" -ForegroundColor Red
        Write-Host "请先用菜单 13 查看分支图，确认为什么 main 出现了独有提交。" -ForegroundColor Yellow
        return
    }

    if ($developAhead -eq 0) {
        Write-Host ""
        Write-Host "main 已经包含 develop 的全部提交，无需合并。" -ForegroundColor Yellow
        return
    }

    Write-Host ""
    Write-Host "将进入 main 的提交：" -ForegroundColor Cyan
    & git log --oneline --decorate "main..develop"

    Write-Host ""
    Write-Host "本操作只在本地执行，不会连接任何远程仓库。"
    Write-Host "合并方式：fast-forward only（保持历史简单、避免额外 merge commit）。"
    Write-Host "完成后会自动切回 develop。"
    Write-Host ""

    $confirm = Read-Host "确认将 develop 合并到 main？(Y/N)"
    if ($confirm -notmatch '^[Yy]$') {
        Write-Host "已取消。"
        return
    }

    $startBranch = Get-CurrentBranch

    Run-Git switch main

    try {
        Run-Git merge --ff-only develop
    }
    catch {
        # 尽量回到原分支；如果失败，则保留 Git 的现场供用户检查。
        try {
            if ($startBranch -ne "main" -and $startBranch -ne "(detached HEAD)") {
                & git switch $startBranch *> $null
            }
        }
        catch {}
        throw
    }

    Run-Git switch develop

    Write-Host ""
    Write-Host "✓ develop 已合并到 main。" -ForegroundColor Green
    Write-Host "✓ main 与 develop 当前指向同一个最新提交。" -ForegroundColor Green
    Write-Host "✓ 已自动返回 develop，继续日常开发即可。" -ForegroundColor Green
}

function Switch-AnyBranch {
    if (-not (Require-CleanTree)) { return }

    Write-Host ""
    Write-Host "现有本地分支：" -ForegroundColor Cyan
    & git branch --format='%(refname:short)'
    Write-Host ""

    $branch = Read-Host "输入要切换的分支名"
    if ([string]::IsNullOrWhiteSpace($branch)) { return }

    if (-not (Test-LocalBranch $branch)) {
        Write-Host "不存在本地分支：$branch" -ForegroundColor Red
        return
    }

    Run-Git switch $branch
    Write-Host ""
    Write-Host "✓ 已切换到 $branch。" -ForegroundColor Green
}

function Checkout-Tag {
    if (-not (Require-CleanTree)) { return }

    $tags = @(Get-VersionTags)
    if ($tags.Count -eq 0) {
        Write-Host "当前没有三段式版本 Tag。" -ForegroundColor Yellow
        return
    }

    Write-Host ""
    Write-Host "现有版本：" -ForegroundColor Cyan
    foreach ($item in $tags) {
        Write-Host "  $($item.Tag)"
    }

    Write-Host ""
    $tag = Read-Host "输入要查看/运行的 Tag，例如 v0.1.0"
    if ([string]::IsNullOrWhiteSpace($tag)) { return }

    if (-not (Test-Tag $tag)) {
        Write-Host "Tag 不存在：$tag" -ForegroundColor Red
        return
    }

    Run-Git switch --detach $tag

    Write-Host ""
    Write-Host "✓ 已切换到 $tag（detached HEAD）。" -ForegroundColor Green
    Write-Host "建议这里只运行/查看，不直接修改；完成后用菜单 3 回到 develop。"
}

function Stash-Changes {
    if (-not (Has-Changes)) {
        Write-Host "当前没有未提交修改。" -ForegroundColor Yellow
        return
    }

    $message = Read-Host "Stash 说明（可留空）"
    if ([string]::IsNullOrWhiteSpace($message)) {
        $message = "temporary changes"
    }

    Run-Git stash push -u -m $message

    Write-Host ""
    Write-Host "✓ 已临时保存修改。" -ForegroundColor Green
}

function Restore-Stash {
    $stashList = & git stash list
    if ([string]::IsNullOrWhiteSpace(($stashList -join "`n"))) {
        Write-Host "当前没有 Stash。" -ForegroundColor Yellow
        return
    }

    Write-Host ""
    & git stash list
    Write-Host ""

    $confirm = Read-Host "恢复最近一个 Stash？(Y/N)"
    if ($confirm -match '^[Yy]$') {
        Run-Git stash pop
    }
}

function Show-TagDetails {
    $tags = @(Get-VersionTags)
    if ($tags.Count -eq 0) {
        Write-Host "当前没有三段式版本 Tag。" -ForegroundColor Yellow
        return
    }

    Write-Host ""
    foreach ($item in $tags) {
        Write-Host "  $($item.Tag)"
    }
    Write-Host ""

    $tag = Read-Host "输入要查看的 Tag"
    if ([string]::IsNullOrWhiteSpace($tag)) { return }

    if (-not (Test-Tag $tag)) {
        Write-Host "Tag 不存在：$tag" -ForegroundColor Red
        return
    }

    Write-Host ""
    Run-Git show $tag --no-patch
}

function Show-FullGraph {
    Write-Host ""
    & git log --graph --decorate --oneline --all --date-order
}

function Switch-Main {
    if (-not (Require-CleanTree)) { return }

    Require-LocalBranch "main"
    Run-Git switch main

    Write-Host ""
    Write-Host "✓ 已切换到 main。" -ForegroundColor Green
    Write-Host "main 用于查看本地稳定版本；日常修改请回到 develop。"
}

# ------------------------------------------------------------
# 启动
# ------------------------------------------------------------

try {
    $repoRoot = Get-RepoRoot
}
catch {
    Write-Host "发生错误：$($_.Exception.Message)" -ForegroundColor Red
    Read-Host "按 Enter 退出"
    exit 1
}

Set-Location $repoRoot

while ($true) {
    Clear-Host

    $latest = Get-LatestVersionInfo

    Write-Host "================================================" -ForegroundColor Cyan
    Write-Host " historical_multi_agent_sim - 本地 Git 管理" -ForegroundColor Cyan
    Write-Host " develop = 日常开发 / main = 本地稳定" -ForegroundColor Cyan
    Write-Host " 仅本地：不连接 GitHub / 不执行远程操作" -ForegroundColor Cyan
    Write-Host "================================================"
    Write-Host ""
    Write-Host "仓库：$repoRoot"
    Write-Host "当前：$(Get-CurrentBranch)"

    if ($latest) {
        Write-Host "本地 Tag：$($latest.Tag)" -ForegroundColor Green
    }
    else {
        Write-Host "本地 Tag：无"
    }

    Write-Host ""
    Write-Host "1.  查看状态 / 分支 / 最近提交"
    Write-Host "2.  保存当前进度（git add + commit；禁止直接提交 main）"
    Write-Host "3.  切换到 develop"
    Write-Host "4.  合并 develop -> main（本地稳定版）"
    Write-Host "    5-7 暂不启用（预留给以后发布流程）" -ForegroundColor DarkGray
    Write-Host "8.  切换到任意本地分支"
    Write-Host "9.  查看 / 运行旧版本 Tag"
    Write-Host "10. 临时保存修改（Stash）"
    Write-Host "11. 恢复最近 Stash"
    Write-Host "12. 查看 Tag 详细信息"
    Write-Host "13. 查看完整分支图"
    Write-Host "14. 切换到 main（只查看稳定版）"
    Write-Host "0.  退出"
    Write-Host ""

    $choice = Read-Host "请选择"

    try {
        switch ($choice) {
            "1"  { Show-Status; Pause-Menu }
            "2"  { Save-Progress; Pause-Menu }
            "3"  { Switch-Develop; Pause-Menu }
            "4"  { Merge-DevelopIntoMain; Pause-Menu }
            "5"  { Write-Host "菜单 5 暂未启用。" -ForegroundColor Yellow; Pause-Menu }
            "6"  { Write-Host "菜单 6 暂未启用。" -ForegroundColor Yellow; Pause-Menu }
            "7"  { Write-Host "菜单 7 暂未启用。" -ForegroundColor Yellow; Pause-Menu }
            "8"  { Switch-AnyBranch; Pause-Menu }
            "9"  { Checkout-Tag; Pause-Menu }
            "10" { Stash-Changes; Pause-Menu }
            "11" { Restore-Stash; Pause-Menu }
            "12" { Show-TagDetails; Pause-Menu }
            "13" { Show-FullGraph; Pause-Menu }
            "14" { Switch-Main; Pause-Menu }
            "0"  { break }
            default {
                Write-Host "无效选项。" -ForegroundColor Yellow
                Pause-Menu
            }
        }
    }
    catch {
        Write-Host ""
        Write-Host "发生错误：$($_.Exception.Message)" -ForegroundColor Red
        Write-Host "建议先使用菜单 1 查看当前状态。" -ForegroundColor Yellow
        Pause-Menu
    }

    if ($choice -eq "0") { break }
}
