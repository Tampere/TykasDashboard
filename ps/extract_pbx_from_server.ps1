<# .SYNOPSIS
      Export of all SSRS reports datasources and images
   .DESCRIPTION
      This PowerShell script exports all (or filtered) reports, data sources and images directly from the ReportServer database
      to a specified folder. For the file name the complete report path is used; for file name invalid characters are replaced with a -.
      Reports are exported with .rdl as extension, data sources with .rds and resources without any additional extension.
      Please change the "Configuration data" below to your enviroment.
      Works with SQL Server 2005 and higher versions in all editions.
      Requires SELECT permission on the ReportServer database.
   .NOTES
      Original Author  : Olaf Helper
      Requires: PowerShell Version 1.0, Ado.Net assembly
	  Modifications: Jouni Alin
	  Important: Please have a look at script that says "CT.[Path] like" and adjust the filter or remove the condition
   .LINK
      GetSqlBinary: http://msdn.microsoft.com/en-us/library/system.data.sqlclient.sqldatareader.getsqlbinary.aspx
   .EXAMPLE
      From PowerShell, with script execution rights (set them with Set-ExecutionPolicy command in PowerShell if necessary), execute
	  .\extract_pbx_from_server.ps1 "MYSQLSERVER.mydomain.fi" "ReportServer" "C:\Temp\report_files\"
      Make sure you have the folder referred as existing folder.	  
   
#>


# Configuration data as arguments
[string] $server   = $args[0];        # SQL Server Instance that hosts the Power BI Report Server database, e.g. MYSQLSERVER.mydomain.fi
[string] $database = $args[1];        # ReportServer database name, most likely ReportServer
[string] $folder   = $args[2];          # Path to export the report files to, e.g. C:\Temp\report_files\

# Select-Statement for file name & blob data with filter. Notice the path filter for test environment use, e.g. search from paths that contain Sandbox.
# Can be excluded to include all, of course.
$sql = "SELECT	CT.[Path]
        ,CT.[Type]
		,ISNULL(cc.ContentType,'SSRS') as ContentType
        ,CONVERT(varbinary(max), cc.[Content]) AS PBI_BinaryContent
        ,CONVERT(varbinary(max), ct.[Content]) AS RDL_BinaryContent
        FROM dbo.[Catalog] AS CT
		LEFT OUTER JOIN dbo.CatalogItemExtendedContent cc
			ON ct.ItemID = cc.ItemId
        WHERE CT.[Type] IN (2, 8, 5,13) 
	    AND ISNULL(cc.ContentType,'CatalogItem') = 'CatalogItem'";		
 #       WHERE CT.[Type] IN (8)";

# Open ADO.NET Connection with Windows authentification.
$con = New-Object Data.SqlClient.SqlConnection;
$con.ConnectionString = "Data Source=$server;Initial Catalog=$database;Integrated Security=True;";
$con.Open();

Write-Output ((Get-Date -format yyyy-MM-dd-HH:mm:ss) + ": Started ...");

# New command and reader.
$cmd = New-Object Data.SqlClient.SqlCommand $sql, $con;
$rd = $cmd.ExecuteReader();

$invalids = [System.IO.Path]::GetInvalidFileNameChars();
# Looping through all selected datasets.
While ($rd.Read())
{
    Try
    {
        # Get the name and make it valid.
        $name = $rd.GetString(0);
		Write-Output "fetching $name"
        foreach ($invalid in $invalids)
           {    $name = $name.Replace($invalid, "-");    }

        If ($rd.GetInt32(1) -eq 2)
            {    $name = $name + ".rdl";    }
        ElseIf ($rd.GetInt32(1) -eq 5)
            {    $name = $name + ".rds";    }
        ElseIf ($rd.GetInt32(1) -eq 8)
            {    $name = $name + ".rsd";    }
        ElseIf ($rd.GetInt32(1) -eq 11)
            {    $name = $name + ".kpi";    }
        ElseIf ($rd.GetInt32(1) -eq 13)
	    {   $name = $name + ".pbix";    }

			
			
        Write-Output ((Get-Date -format yyyy-MM-dd-HH:mm:ss) + ": Exporting {0}" -f $name);

        $name = [System.IO.Path]::Combine($folder, $name);

        # New BinaryWriter; existing file will be overwritten.
        $fs = New-Object System.IO.FileStream ($name), Create, Write;
        $bw = New-Object System.IO.BinaryWriter($fs);

        # Read of complete Blob with GetSqlBinary
        if ($rd.GetString(2) -eq "SSRS") {
			$bt = $rd.GetSqlBinary(4).Value;
		} else{
			$bt = $rd.GetSqlBinary(3).Value;
		}
		
		
        $bw.Write($bt, 0, $bt.Length);
        $bw.Flush();
        $bw.Close();
        $fs.Close();
    }
    Catch
    {
        Write-Output ($_.Exception.Message)
    }
    Finally
    {
        $fs.Dispose();
    }
}

# Closing & Disposing all objects
$rd.Close();
$cmd.Dispose();
$con.Close();
$con.Dispose();

Write-Output ((Get-Date -format yyyy-MM-dd-HH:mm:ss) + ": Finished");