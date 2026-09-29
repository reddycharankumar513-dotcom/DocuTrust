Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Push-Location "$PSScriptRoot\..\frontend"
try {
  corepack pnpm install --frozen-lockfile
  corepack pnpm run build
}
finally {
  Pop-Location
}
