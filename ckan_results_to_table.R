library(data.table)
library(jsonlite)


# we have to look up all the possible column names from the resources dt
get_all_column_names <- function(resources_cell) {
    return(names(data.table(resources_cell[[1]])))
}

unlist_resources_cell <- function(
    resources_cell,
    output_colnames) {
    my_dt <- data.table(resources_cell[[1]])
    missing_cols <- setdiff(output_colnames, names(my_dt))
    for (col in missing_cols) {
        my_dt[, (col) := as.character(NA)]
    }
    setcolorder(my_dt, output_colnames)
    setnames(my_dt, paste0("resources.", names(my_dt)))
    return(my_dt)
}

results_file <- "results.json"

json_data <- fromJSON(results_file)
parent_results_dt <- as.data.table(json_data)

my_colclasses <- parent_results_dt[, sapply(.SD, class)]
non_list_cols <- my_colclasses[my_colclasses != "list"]

# I think the resources dt is always a single dt.
parent_results_dt[, length(resources), by = 1:nrow(parent_results_dt)]

all_resources_colnames <- parent_results_dt[
    , get_all_column_names(resources),
    by = names(non_list_cols)
][, unique(V1)]

expanded_resources <- parent_results_dt[
    ,
    unlist_resources_cell(
        resources,
        output_colnames = all_resources_colnames
    ),
    by = names(non_list_cols)
]

fwrite(expanded_resources, "expanded_resources.csv")

# peek

expanded_resources[, unique(resources.url), by = "sample_id"][sample_id == "102.100.100/457847"]

# let's download and assembly this one
expanded_resources[sample_id == "102.100.100/457847"]
