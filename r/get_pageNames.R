# Getting the right system path
sys.source("../env_config.r")

# Print system paht
getwd()

# Call package pbixr
suppressMessages(library(pbixr))

# Get all pbix-files from a specified folder (example: pbi_files folder), which is not in the git repository, adjust the path as needed
files <- list.files(path="../pbi_files", pattern="*.pbix", full.names=TRUE, recursive=FALSE)

#Initialize lists
page_name <- c()
report_name <- c()

#Loop through all the report files that were found
for(i in files) {
  
  file_path = i

  #Use pbixr-library to find page names of the report
  gsub__1 <- paste0(".*sections")
  gsub__2 <- "{\"id\":0,\"sections"
  get_layout <- f_read_layout(file_path, gsub__1, gsub__2)
  computer_name <- get_layout$sections$name
  ReportPages <- get_layout$sections$displayName
  
    #Append report page names to a list
    for (x in ReportPages) {
      page_name[[length(page_name) + 1]] <- x 
    }
    #Append the corresponding report name to a list as many times as there are pages in the report
    for (a in 1:length(ReportPages)) {
      report_name[[length(report_name) + 1]] <- i
    }
  
}
#Combine to a dataframe
df <- data.frame(unlist(report_name), unlist(page_name))
colnames(df) <- c('ReportName','PageName')

