#' Plot platemap
#'
#' \code{plot_plate} plots platemaps
#'
#' @param plate
#' @param variable
#' @param well_position
#'
#' @return
#' @export
#'
#' @examples
plot_plate <- function(plate,
                       variable,
                       well_position = "well_position") {
  variable <- rlang::sym(variable)

  well_position <- rlang::sym(well_position)

  plate %<>%
    rowwise() %>%
    mutate(row_id =
             str_sub(!!!well_position, 1, 1)[[1]]) %>%
    mutate(row_id_int =
             str_locate(paste0(LETTERS, collapse = ""), row_id)[[1]]) %>%
    mutate(col_id =
             as.integer(str_sub(!!!well_position, 2, 3)))

  p <-
    ggplot(plate, aes(as.factor(col_id), fct_rev(as.factor(row_id)), fill = !!variable)) +
    geom_tile(color = "white") +
    coord_equal() +
    theme_minimal() +
    scale_x_discrete(name = "", position = "top") +
    scale_y_discrete(name = "")

  p
}



#' Title
#'
#' @param profiles
#'
#' @return
#' @export
#'
#' @examples
similarity <-
  function(profiles,
           metadata_regex = "^Metadata_",
           method = "pearson") {
    # get data matrix
    data_matrix <-
      profiles %>%
      select(-matches(metadata_regex))

    # get metadata
    metadata <-
      profiles %>%
      select(matches(metadata_regex)) %>%
      rowid_to_column(var = "id")

    # measure similarities between treatments
    similarity_ <- cor(t(data_matrix), method = method)

    colnames(similarity_) <- seq(1, ncol(similarity_))

    similarity_ %<>%
      as_tibble() %>%
      rowid_to_column(var = "id1") %>%
      gather(id2, correlation,-id1) %>%
      mutate(id2 = as.integer(id2)) %>%
      arrange(desc(correlation))

    # annotate the similarities data frame

    i1 <- metadata

    names(i1) <- paste0(names(i1), "1")

    i2 <- metadata

    names(i2) <- paste0(names(i2), "2")

    similarity_ %<>%
      inner_join(i1, by = "id1") %>%
      inner_join(i2, by = "id2")

    similarity_

  }


#' Title
#'
#' @param similarity
#' @param grouping_vars
#'
#' @return
#' @export
#'
#' @examples
similarity_summary <-
  function(similarity,
           grouping_vars)  {
    similarity_reps <-
      similarity %>%
      ungroup() %>%
      filter(id1 != id2)

    for (grouping_var in grouping_vars) {
      similarity_reps %<>%
        filter(!!rlang::parse_expr(
          "%s == %s",
          paste0(grouping_var, "1"),
          paste0(grouping_var, "2")
        ))
    }

    similarity_reps %>%
      group_by(across(paste0(grouping_vars, "1"))) %>%
      summarise(value = median(value),
                n = n(),
                .groups = "keep") %>%
      ungroup()

  }
