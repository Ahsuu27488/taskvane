# Sensor helper: loads LibreHardwareMonitorLib and prints one JSON line of sensors per interval.
# Runs in its own process so a driver/.NET fault can never crash the Taskvane window.
param([string]$LibDir, [int]$IntervalMs = 1000, [int]$ParentPid = 0)
$ErrorActionPreference = 'Stop'

# The resolver must be compiled C#: a PowerShell scriptblock handler recurses and overflows.
Add-Type -TypeDefinition @'
using System; using System.IO; using System.Reflection;
public static class TaskvaneResolver {
    static string dir;
    public static void Install(string d) {
        dir = d;
        AppDomain.CurrentDomain.AssemblyResolve += (s, e) => {
            var name = new AssemblyName(e.Name).Name;
            if (name.EndsWith(".resources")) return null;
            var p = Path.Combine(dir, name + ".dll");
            return File.Exists(p) ? Assembly.LoadFrom(p) : null;
        };
    }
}
'@
[TaskvaneResolver]::Install($LibDir)

$lhm = Join-Path $LibDir 'LibreHardwareMonitorLib.dll'
try {
    [void][Reflection.Assembly]::LoadFrom($lhm)
    Add-Type -ReferencedAssemblies $lhm, 'System.Runtime', 'netstandard' -IgnoreWarnings -TypeDefinition @'
using System; using System.Text; using System.Globalization;
using LibreHardwareMonitor.Hardware;
public static class TaskvaneReader {
    static Computer pc;
    static readonly string[] Keep = { "Temperature","Power","Fan","Clock","Load","Voltage","Energy","Data","SmallData","Throughput","Level","Control","Factor" };
    public static void Open() {
        pc = new Computer { IsCpuEnabled = true, IsGpuEnabled = true, IsMemoryEnabled = true, IsMotherboardEnabled = true,
                            IsStorageEnabled = true, IsBatteryEnabled = true, IsControllerEnabled = true };
        pc.Open();
    }
    public static void Close() { try { pc.Close(); } catch { } }
    static string Esc(string s) { return (s ?? "").Replace("\\", "\\\\").Replace("\"", "\\\""); }
    public static string Read() {
        var sb = new StringBuilder(16384);
        sb.Append("{\"sensors\":[");
        bool first = true;
        foreach (var hw in pc.Hardware) Walk(hw, hw.Name, hw.HardwareType.ToString(), sb, ref first);
        sb.Append("]}");
        return sb.ToString();
    }
    static void Walk(IHardware hw, string root, string rootType, StringBuilder sb, ref bool first) {
        try { hw.Update(); } catch { return; }
        foreach (var s in hw.Sensors) {
            var t = s.SensorType.ToString();
            if (Array.IndexOf(Keep, t) < 0 || !s.Value.HasValue) continue;
            var v = (double)s.Value.Value;
            if (double.IsNaN(v) || double.IsInfinity(v)) continue;
            if (!first) sb.Append(','); first = false;
            sb.Append("{\"id\":\"").Append(Esc(s.Identifier.ToString()))
              .Append("\",\"hw\":\"").Append(Esc(root)).Append("\",\"hw_type\":\"").Append(rootType)
              .Append("\",\"sub\":\"").Append(hw.Name == root ? "" : Esc(hw.Name))
              .Append("\",\"name\":\"").Append(Esc(s.Name)).Append("\",\"type\":\"").Append(t)
              .Append("\",\"value\":").Append(v.ToString("R", CultureInfo.InvariantCulture)).Append('}');
        }
        foreach (var sub in hw.SubHardware) Walk(sub, root, rootType, sb, ref first);
    }
}
'@
    [TaskvaneReader]::Open()
} catch {
    [Console]::Out.WriteLine('{"error":' + (ConvertTo-Json ([string]$_.Exception.GetBaseException().Message)) + '}')
    [Console]::Out.Flush()
    exit 1
}

while ($true) {
    try { $line = [TaskvaneReader]::Read() } catch { $line = '{"sensors":[]}' }
    [Console]::Out.WriteLine($line)
    [Console]::Out.Flush()
    # Exit when Taskvane is gone (quit or crashed).
    if ($ParentPid -and -not (Get-Process -Id $ParentPid -ErrorAction SilentlyContinue)) { break }
    Start-Sleep -Milliseconds $IntervalMs
}
[TaskvaneReader]::Close()
