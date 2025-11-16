# Ollama 자동 설치 스크립트 (PowerShell)
# Windows 전용

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Ollama 자동 설치 스크립트" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# 1. Ollama 설치 확인
Write-Host "[1/4] Ollama 설치 확인 중..." -ForegroundColor Cyan
$ollamaInstalled = $false
try {
    $version = & ollama --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Ollama가 이미 설치되어 있습니다: $version" -ForegroundColor Green
        $ollamaInstalled = $true
    }
} catch {
    Write-Host "[INFO] Ollama가 설치되어 있지 않습니다." -ForegroundColor Yellow
}

# 2. Ollama 다운로드 및 설치
if (-not $ollamaInstalled) {
    Write-Host ""
    Write-Host "[2/4] Ollama 다운로드 중..." -ForegroundColor Cyan

    $downloadUrl = "https://ollama.com/download/OllamaSetup.exe"
    $installerPath = "$env:TEMP\OllamaSetup.exe"

    try {
        Write-Host "다운로드 URL: $downloadUrl" -ForegroundColor Gray
        Write-Host "저장 위치: $installerPath" -ForegroundColor Gray

        # 브라우저에서 다운로드 페이지 열기
        Write-Host ""
        Write-Host "브라우저에서 다운로드 페이지를 엽니다..." -ForegroundColor Yellow
        Start-Process "https://ollama.com/download/windows"

        Write-Host ""
        Write-Host "다운로드한 OllamaSetup.exe를 실행하여 설치를 완료하세요." -ForegroundColor Yellow
        Write-Host "설치 완료 후 이 스크립트로 돌아와 Enter를 누르세요." -ForegroundColor Yellow
        Read-Host "설치 완료 후 Enter를 누르세요"

        # 설치 확인
        try {
            $version = & ollama --version 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "[OK] Ollama 설치 완료: $version" -ForegroundColor Green
                $ollamaInstalled = $true
            } else {
                Write-Host "[FAIL] Ollama 설치를 확인할 수 없습니다." -ForegroundColor Red
                Write-Host "PowerShell을 재시작한 후 다시 시도하세요." -ForegroundColor Yellow
                exit 1
            }
        } catch {
            Write-Host "[FAIL] Ollama 설치를 확인할 수 없습니다." -ForegroundColor Red
            Write-Host "PowerShell을 재시작한 후 다시 시도하세요." -ForegroundColor Yellow
            exit 1
        }

    } catch {
        Write-Host "[ERROR] 다운로드 실패: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "[2/4] Ollama 설치 단계 건너뛰기 (이미 설치됨)" -ForegroundColor Green
}

# 3. Ollama 서버 시작
Write-Host ""
Write-Host "[3/4] Ollama 서버 확인 중..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "[OK] Ollama 서버가 실행 중입니다!" -ForegroundColor Green
} catch {
    Write-Host "[INFO] Ollama 서버를 시작합니다..." -ForegroundColor Yellow
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 5

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434" -TimeoutSec 5 -ErrorAction Stop
        Write-Host "[OK] Ollama 서버 시작 성공!" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Ollama 서버 시작 실패" -ForegroundColor Yellow
        Write-Host "수동으로 'ollama serve'를 실행해주세요." -ForegroundColor Yellow
    }
}

# 4. Llama 3.1 8B 모델 다운로드
Write-Host ""
Write-Host "[4/4] Llama 3.1 8B 모델 확인 중..." -ForegroundColor Cyan

$modelList = & ollama list 2>$null
if ($modelList -match "llama3.1:8b") {
    Write-Host "[OK] Llama 3.1 8B 모델이 이미 설치되어 있습니다!" -ForegroundColor Green
} else {
    Write-Host "[INFO] Llama 3.1 8B 모델이 설치되어 있지 않습니다." -ForegroundColor Yellow
    Write-Host ""
    $download = Read-Host "Llama 3.1 8B 모델을 다운로드하시겠습니까? (약 4.7GB, 5-15분 소요) (y/n)"

    if ($download -eq "y" -or $download -eq "Y") {
        Write-Host ""
        Write-Host "모델 다운로드 시작... (시간이 걸릴 수 있습니다)" -ForegroundColor Yellow
        & ollama pull llama3.1:8b

        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] 모델 다운로드 완료!" -ForegroundColor Green
        } else {
            Write-Host "[FAIL] 모델 다운로드 실패" -ForegroundColor Red
        }
    } else {
        Write-Host "[SKIP] 모델 다운로드를 건너뜁니다." -ForegroundColor Yellow
        Write-Host "나중에 'ollama pull llama3.1:8b'로 다운로드하세요." -ForegroundColor Yellow
    }
}

# 최종 확인
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "설치 완료!" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

Write-Host "다음 명령으로 설치를 확인하세요:" -ForegroundColor Yellow
Write-Host "  python Local_LLM/check_ollama.py" -ForegroundColor White
Write-Host ""
Write-Host "Admin Agent Local 실행:" -ForegroundColor Yellow
Write-Host "  cd Local_LLM/Admin_Agent_Local/scripts" -ForegroundColor White
Write-Host "  python admin_agent_local.py" -ForegroundColor White
Write-Host ""
