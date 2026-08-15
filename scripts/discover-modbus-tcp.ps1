param(
    [Parameter(Mandatory = $true)]
    [string[]]$Cidr,

    [switch]$ModbusProbe,

    [switch]$Json,

    [string]$Output
)

$ErrorActionPreference = "Stop"
$script = Join-Path $PSScriptRoot "discover-modbus-tcp.py"
$argsList = @()
foreach ($item in $Cidr) {
    $argsList += @("--cidr", $item)
}
if ($ModbusProbe) {
    $argsList += "--modbus-probe"
}
if ($Json) {
    $argsList += "--json"
}
if ($Output) {
    $argsList += @("--output", $Output)
}

python $script @argsList
