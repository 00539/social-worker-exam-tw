$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ProgressPreference = 'SilentlyContinue'
$root = (Join-Path $PSScriptRoot '..\data\papers')
New-Item -ItemType Directory -Force -Path $root | Out-Null

# 6科時期(111-114)科目對照
$subj6 = @{ '01'='社會工作'; '02'='社會工作直接服務'; '03'='社會工作管理'; '04'='社會政策與社會立法'; '05'='人類行為與社會環境'; '06'='社會工作研究方法' }
# 5科時期(115起)科目對照
$subj5 = @{ '01'='社會工作'; '02'='社會工作直接服務'; '03'='社會政策與社會立法'; '04'='人類行為與社會環境'; '05'='社會工作研究方法' }

$exams = @(
  @{ code='111030'; name='111年第一次'; c='105'; pre='04'; map=$subj6; gw='0502' },
  @{ code='111110'; name='111年第二次'; c='105'; pre='04'; map=$subj6; gw='1102' },
  @{ code='112030'; name='112年第一次'; c='103'; pre='03'; map=$subj6; gw='0401' },
  @{ code='112110'; name='112年第二次'; c='103'; pre='03'; map=$subj6; gw='1001' },
  @{ code='113030'; name='113年第一次'; c='103'; pre='03'; map=$subj6; gw='0401' },
  @{ code='113100'; name='113年第二次'; c='103'; pre='03'; map=$subj6; gw='1201' },
  @{ code='114030'; name='114年第一次'; c='103'; pre='03'; map=$subj6; gw='0401' },
  @{ code='114100'; name='114年第二次'; c='103'; pre='03'; map=$subj6; gw='1201' },
  @{ code='115030'; name='115年第一次'; c='103'; pre='03'; map=$subj5; gw=$null },
  @{ code='115100'; name='115年第二次'; c='103'; pre='03'; map=$subj5; gw=$null }
)

$kinds = @{ 'Q'='試題'; 'S'='答案'; 'M'='更正答案' }
$ok = 0; $skip = 0; $fail = @()

foreach ($e in $exams) {
  $dir = Join-Path $root $e.name
  New-Item -ItemType Directory -Force -Path $dir | Out-Null

  $targets = @()
  foreach ($k in ($e.map.Keys | Sort-Object)) {
    $targets += @{ s = ($e.pre + $k); title = $e.map[$k]; kinds = @('Q','S','M') }
  }
  if ($e.gw) { $targets += @{ s = $e.gw; title = '國文（作文）'; kinds = @('Q') } }

  foreach ($t in $targets) {
    foreach ($kd in $t.kinds) {
      $url = "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?t=$kd&code=$($e.code)&c=$($e.c)&s=$($t.s)&q=1"
      $fn = "$($e.name)_$($t.title)_$($kinds[$kd]).pdf"
      $out = Join-Path $dir $fn
      if (Test-Path $out) { $ok++; continue }
      try {
        Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing -TimeoutSec 90
        $len = (Get-Item $out).Length
        $fs = [System.IO.File]::OpenRead($out); $b = New-Object byte[] 4; $fs.Read($b,0,4) | Out-Null; $fs.Close()
        $head = $b -join ','
        if ($len -lt 2000 -or $head -ne '37,80,68,70') {
          Remove-Item $out -Force
          $skip++
        } else { $ok++ }
      } catch {
        if (Test-Path $out) { Remove-Item $out -Force }
        if ($kd -eq 'M') { $skip++ } else { $fail += $fn }
      }
      Start-Sleep -Milliseconds 300
    }
  }
}

Write-Output "下載成功: $ok 個檔案"
Write-Output "無此檔(多為未發布更正答案): $skip"
if ($fail.Count -gt 0) { Write-Output "失敗:"; $fail | ForEach-Object { Write-Output "  $_" } }
