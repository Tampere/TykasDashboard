/*Script for creating a view that queries the basic information of ReportServer reports.

/Specify the database where the view is to be created. If no linked servers are set up, it should be located
in the the same SQL Server than then ReportServer DB.*/
USE [YOUR DB NAME]
GO
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE VIEW [dbo].[Report_main]
	AS
SELECT
       c.[Path],
       c.[Name],
       c.[Description],
       c.[Hidden],
	     x.unique_user_count as [Count of unique users in last 30 days],
       u.[UserName] as [Original author],
       c.[CreationDate],
       u2.[UserName] as [Last publisher],
       c.[ModifiedDate],
       c.[ContentSize]/(1024.0*1024.0) as [Size (mb)]

  FROM [ReportServer].[dbo].[Catalog] as c INNER JOIN [ReportServer].[dbo].[Users] as u
  ON c.CreatedByID=u.UserID
  INNER JOIN  [ReportServer].[dbo].[Users] as u2
  ON c.[ModifiedByID]=u2.UserID
  LEFT JOIN 
  (SELECT c.[name] as reportName, count(distinct e.username) as unique_user_count
   FROM [ReportServer].[dbo].[Catalog] c 
   INNER JOIN [ReportServer].[dbo].[ExecutionLogStorage] e on c.ItemID = e.reportid 
   WHERE e.TimeStart >= getdate()-30 AND e.TimeEnd < getdate()
   GROUP BY c.[name]) as x
  ON c.[Name]=x.reportName
  WHERE c.Type=13
GO
