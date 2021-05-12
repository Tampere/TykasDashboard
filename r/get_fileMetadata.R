# Getting the right system path
sys.source("../env_config.r")

# Print system path
getwd()

# Call packages
suppressMessages(library(pbixr))
suppressMessages(library(jsonlite))
suppressMessages(library(DBI))
suppressMessages(library(odbc))



########### Create a dataframe containing report name, page names, table names and column names for each pbix-file ########### 


# Get all pbix-files from a specified folder (example: pbi_files folder), which is not in the git repository, adjust the path as needed
files <- list.files(path="../pbi_files", pattern="*.pbix", full.names=TRUE, recursive=FALSE)

#Initialize lists
report_name <-c()
page_name <- c()
table_name <- c()
field_name <- c()

#Loop through all the report files that were found
for(file in files) {
  
  file_path = file
  
  #Use pbixr-library to find report layout-jsons
  gsub__1 <- paste0(".*sections")
  gsub__2 <- "{\"id\":0,\"sections"
  get_layout <- f_read_layout(file_path, gsub__1, gsub__2)
  json_sect <- get_layout$sections
  
  #Use pbixr-library to find report page names
  visual_containers <- json_sect$displayName
  page_names <- unlist(strsplit(visual_containers,split='.', fixed=TRUE))
  
  #Create a list of report page json-objects
  page_json_list <-json_sect$visualContainers
    
  #Loop through all the report page objects
  for (page in 1:length(page_json_list)) {
    page_json <- as.data.frame(page_json_list[page])
  
    #Loop through all the individual visual elements of the page
    for (element in 1:nrow(page_json)) {
      
      #Select one visual
      visual <- fromJSON(page_json$config[element], flatten=F)
      
      #Break down the visual into a list of its metadata values
      content_list <- unlist(visual[3])
      content_list_names <- names(content_list)
      
      #Loop through the visual metadata values
      for (name in content_list_names) {
        
        #Check if metadata row name starts with "singleVisual.prototypeQuery.Select.Name" --> 
        #if yes, then the field contains data about the data source table and its field names that are used in the visual
        
        if (grepl("singleVisual.prototypeQuery.Select.Name", name, fixed = FALSE) == TRUE) {
          
          #Parse result strings into corresponding result lists
          result <- sub("\\).*", "", sub(".*\\(", "", content_list[name]))
          values <- unlist(strsplit(result,split='.', fixed=TRUE))
          table_name[[length(table_name) + 1]] <- values[1]
          field_name[[length(field_name) + 1]] <- values[2]
          page_name[[length(page_name) + 1]] <- page_names[page]

          filename <- basename(file)
          filename_without_extension <- substr(filename, 1, nchar(filename)-5)
          report_name[[length(report_name) + 1]] <- filename_without_extension
          
        }
      }
    }
  }
}

#Combine lists to a dataframe
df <- data.frame(report_name, page_name, table_name, field_name)

#Remove duplicates (if the same field is used multiple times in a report page)
df <- df[!duplicated(df), ]




########### Create an aggregated table for the "all-content search field ########### 


#Initialize empty dataframe for results
df_aggr <- select(df, report_name)

#Initialize sub-dataframes for the analysis and insert them into a list. Here we have one dataframe for each field (page, table, field)
df_page <- select(df, report_name, page_name)
df_table <- select(df, report_name, table_name)
df_field <- select(df, report_name, field_name)
dfList <- list(df_page, df_table, df_field)

#Loop through the list of one-field dataframes to aggregate their values and to remove duplicates
for (x in dfList) {
  
  x <- x[!duplicated(x), ]
  
  #Here we concatenate values from multiple rows into one string, where the initial row values are separated by comma
  if (colnames(x)[2] == 'page_name') {
    x <- x %>% 
      group_by(report_name) %>% 
      mutate(page_name_string = paste0(page_name, collapse = ","))
  }
  if (colnames(x)[2] == 'table_name') {
    x <- x %>% 
      group_by(report_name) %>% 
      mutate(table_name_string = paste0(table_name, collapse = ","))
  }
  if (colnames(x)[2] == 'field_name') {
    x <- x %>% 
      group_by(report_name) %>% 
      mutate(field_name_string = paste0(field_name, collapse = ","))
  }
  
  x <- select(x, report_name, colnames(x)[3])
  x <- x[!duplicated(x), ]
  
  # Join the looped dataframe into the result dataframe and move to the next one-field dataframe
  df_aggr <- merge(df_aggr, x, by = "report_name")
}

# Remove duplicates, concatenate fields and select the final fields for the result dataframe
df_aggr <- df_aggr[!duplicated(df_aggr), ]
df_aggr$content <- paste(df_aggr$page_name, df_aggr$table_name, df_aggr$field_name, sep = ",")
df_aggr$all <- paste(df_aggr$report_name, df_aggr$content, sep = ",")
df_search <- select(df_aggr, report_name, all)




########### Write dataframes into SQL-Server database ########### 


#Replace your own database parameters (server name, database name, table name) here:

#Write df into "report_data" -table
conn <- dbConnect(odbc::odbc(),driver="SQL Server", server = "YOUR SERVER NAME", database = 'YOUR DB NAME')
dbWriteTable(conn, "report_data", df, encoding='UTF-8', overwrite=TRUE)

#Write df_search into "report_ContentSearch" -table
conn <- dbConnect(odbc::odbc(),driver="SQL Server", server = "YOUR SERVER NAME", database = 'YOUR DB NAME')
dbWriteTable(conn, "report_ContentSearch", df_search, encoding='UTF-8', overwrite=TRUE)




