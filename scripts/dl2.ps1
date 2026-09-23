$ErrorActionPreference = 'Stop'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ProgressPreference = 'SilentlyContinue'
$root = (Join-Path $PSScriptRoot '..\data\papers')

$subj6 = @{ '01'='社會工作'; '02'='社會工作直接服務'; '03'='社會工作管理'; '04'='社會政策與社會立法'; '05'='人類行為與社會環境'; '06'='社會工作研究方法' }
$subj3 = @{ '01'='社會工作'; '02'='社會工作直接服務'; '03'='社會工作管理' }

$exams = @(
  @{ code='106030'; name='106年第一次';     c='107'; pre='06'; map=$subj6; gw='0702' },
  @{ code='106110'; name='106年第二次';     c='107'; pre='06'; map=$subj6; gw='1202' },
  @{ code='106111'; name='106年第二次補辦'; c='107'; pre='06'; map=$subj3; gw=$null  },
  @{ code='107030'; name='107年第一次';     c='107'; pre='06'; map=$subj6; gw='0702' },
  @{ code='107110'; name='107年第二次';     c='107'; pre='06'; map=$subj6; gw='1202' },
  @{ code='108020'; name='108年第一次';     c='107'; pre='06'; map=$subj6; gw='0702' },
  @{ code='108110'; name='108年第二次';     c='107'; pre='06'; map=$subj6; gw='1202' },
  @{ code='109030'; name='109年第一次';     c='107'; pre='06'; map=$subj6; gw='0702' },
  @{ code='109110'; name='109年第二次';     c='107'; pre='06'; map=$subj6; gw='1202' },
  @{ code='110030'; name='110年第一次';     c='105'; pre='04'; map=$subj6; gw='0502' }
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
  if ($e.gw) { $targets += @{ s = $e.gw; title = '國文'; kinds = @('Q') } }

  foreach ($t in $targets) {
    foreach ($kd in $t.kinds) {
      $url = "https://wwwq.moex.gov.tw/exam/wHandExamQandA_File.ashx?t=$kd&code=$($e.code)&c=$($e.c)&s=$($t.s)&q=1"
      $out = Join-Path $dir "$($e.name)_$($t.title)_$($kinds[$kd]).pdf"
      if (Test-Path $out) { $ok++; continue }
      try {
        Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing -TimeoutSec 90
        $len = (Get-Item $out).Length
        $fs = [System.IO.File]::OpenRead($out); $b = New-Object byte[] 4; $fs.Read($b,0,4) | Out-Null; $fs.Close()
        if ($len -lt 2000 -or ($b -join ',') -ne '37,80,68,70') { Remove-Item $out -Force; $skip++ }
        else { $ok++ }
      } catch {
        if (Test-Path $out) { Remove-Item $out -Force }
        if ($kd -eq 'M') { $skip++ } else { $fail += (Split-Path $out -Leaf) }
      }
      Start-Sleep -Milliseconds 300
    }
  }
}

Write-Output "新增下載: $ok 個檔案"
Write-Output "無此檔: $skip"
if ($fail.Count -gt 0) { Write-Output "失敗:"; $fail | ForEach-Object { Write-Output "  $_" } }
