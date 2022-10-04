library(reticulate)

Sys.setenv(TOKENIZERS_PARALLELISM="false")
taxonerd <- NULL

.onLoad <- function(libname, pkgname) {
  envname = "r-taxonerd"
  if (!reticulate::virtualenv_exists(envname = "r-taxonerd")) {
    reticulate::virtualenv_create(envname)
  }
}

#' Install the TaxoNERD python package.
#'
#' @param cuda.version Your CUDA version. Default = NULL.
#' @example \dontrun{install.taxonerd()}
#' @example \dontrun{install.taxonerd(cuda.version="cuda113")}
#' @export install.taxonerd
#' @import reticulate
install.taxonerd <- function(cuda.version=NULL) {
  version = "1.4.0"
  # create a new environment 
  extras = ""
  if (!is.null(cuda.version)) {
    extras = paste("[",cuda.version,"]",sep="")
  }
  reticulate::virtualenv_install("r-taxonerd", packages = paste("taxonerd",extras,"==",version,sep=""), ignore_installed = TRUE)
}

#' Import the TaxoNERD python package.
#'
#' @example import.taxonerd()
#' @import reticulate
import.taxonerd <- function() {
  use_virtualenv("r-taxonerd", required = TRUE)
  import("taxonerd")
}

#' Install the taxonomic entity recognition models.
#'
#' @param model The name of the model.
#' @example \dontrun{install.model("en_core_eco_md")}
#' @export install.model
#' @import reticulate
install.model <- function(model) {
  url = sprintf("https://github.com/nleguillarme/taxonerd/releases/download/v1.4.0/%s-1.0.2.tar.gz", model)
  virtualenv_install("r-taxonerd", packages = url, ignore_installed = TRUE)
}

#' Initialize the taxonomic entity recognition engine.
#'
#' @param model The name of the model. Default is en_core_eco_md.
#' @param exclude A list containing the names of pipeline components to exclude. Excluded components won’t be loaded. Default is empty list.
#' @param linker The name of the entity linker. Default is NULL.
#' @param thresh The mention-entity candidate similarity threshold for entity linking. Default is 0.7.
#' @param gpu Set to TRUE to use GPU if available. Default is FALSE.
#' @return a TaxoNERD object.
#' @examples
#' \dontrun{init.taxonerd(model="en_core_eco_biobert", gpu=TRUE)}
#' \dontrun{init.taxonerd(model="en_core_eco_md", exclude=list("pysbd_sentencizer"), linker="taxref", thresh=0.7, gpu=FALSE)}
#' @export init.taxonerd
init.taxonerd <- function(model="en_core_eco_md", exclude=list(), linker=NULL, thresh=0.7, gpu=FALSE) {
  taxonerd <- import.taxonerd()
  client <- taxonerd$TaxoNERD(gpu)
  nlp <- client$load(model=model, exclude=exclude, linker=linker, threshold=thresh)
  return(client)
}

#' Find taxonomic entity mentions in a piece of text.
#'
#' @param taxonerd A TaxoNERD object.
#' @param text.string A string containing the text to be searched.
#' @return A data frame.
#' @examples
#' \dontrun{df = find.in.text(taxonerd, "Brown bears (Ursus arctos) are recognised as opportunistic omnivores")}
#' @export find.in.text
find.in.text <- function(taxonerd, text.string) {
  return(taxonerd$find_in_text(text.string))
}

#' Find taxonomic entity mentions in file.
#'
#' @param taxonerd A TaxoNERD object.
#' @param file.path The path to the file.
#' @param output.dir.path A path to a directory to store the results. Default is NULL.
#' @return A data frame if output.dir.path is NULL, the path to the file containing the results otherwise.
#' @examples
#' \dontrun{df = find.in.file(taxonerd, "./my_corpus/my_file_1.txt")}
#' @export find.in.file
find.in.file <- function(taxonerd, file.path, output.dir.path=NULL) {
  return(taxonerd$find_in_file(file.path, output.dir.path))
}

#' Find taxonomic entity mentions in a corpus.
#'
#' @param taxonerd A TaxoNERD object.
#' @param input.dir.path The path to the directory containing the corpus.
#' @param output.dir.path A path to a directory to store the results. Default is NULL.
#' @return A list of data frames if output.dir.path is NULL, a list of paths otherwise.
#' @examples
#' \dontrun{dfs = find.in.corpus(taxonerd, "./my_corpus")}
#' @export find.in.corpus
find.in.corpus <- function(taxonerd, input.dir.path, output.dir.path=NULL) {
  return(taxonerd$find_in_corpus(input.dir.path, output.dir.path))
}