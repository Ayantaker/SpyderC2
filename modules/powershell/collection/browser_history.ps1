function Get-ChromeHistory {
    $Path = "$Env:systemdrive\Users\$UserName\AppData\Local\Google\Chrome\User Data\Default\History"
    if (-not (Test-Path -Path $Path)) {
        Write-Verbose "[!] Could not find Chrome History for username: $UserName"
    }
    $Regex = '(htt(p|s))://([\w-]+\.)+[\w-]+(/[\w- ./?%&=]*)*?'
    $Value = Get-Content -Path "$Env:systemdrive\Users\$UserName\AppData\Local\Google\Chrome\User Data\Default\History"|Select-String -AllMatches $regex |% {($_.Matches).Value} |Sort -Unique
    $Value | ForEach-Object {
        $Key = $_
        if ($Key -match $Search){
            New-Object -TypeName PSObject -Property @{
                User = $UserName
                Browser = 'Chrome'
                DataType = 'History'
                Data = $_
            }
        }
    }        
}


function ConvertFrom-Json20([object] $item){
    #http://stackoverflow.com/a/29689642
    Add-Type -AssemblyName System.Web.Extensions
    $ps_js = New-Object System.Web.Script.Serialization.JavaScriptSerializer
    return ,$ps_js.DeserializeObject($item)
    
}

function Get-ChromeBookmarks {
$Path = "$Env:systemdrive\Users\$UserName\AppData\Local\Google\Chrome\User Data\Default\Bookmarks"
if (-not (Test-Path -Path $Path)) {
    Write-Verbose "[!] Could not find FireFox Bookmarks for username: $UserName"
}   else {
        $Json = Get-Content $Path
        $Output = ConvertFrom-Json20($Json)
        $Jsonobject = $Output.roots.bookmark_bar.children
        $Jsonobject.url |Sort -Unique | ForEach-Object {
            if ($_ -match $Search) {
                New-Object -TypeName PSObject -Property @{
                    User = $UserName
                    Browser = 'Chrome'
                    DataType = 'Bookmark'
                    Data = $_
                }
            }
        }
    }
}

$UserName = "$ENV:USERNAME"
$history = Get-ChromeHistory

# Get-ChromeBookmarks

$bookmarks = Get-ChromeBookmarks


return $history + $bookmarks