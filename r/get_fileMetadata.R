# Getting the right system path
sys.source("../env_config.r")

# Print system path
getwd()

# Call package pbixr
suppressMessages(library(pbixr))

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
df





